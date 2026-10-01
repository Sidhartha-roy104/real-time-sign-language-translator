import threading
import cv2
import mediapipe as mp
import numpy as np
import os
import torch
from typing import Tuple, Optional
import traceback

# replace eager model/camera init with lazy loaders
_model = None
_cap = None
_model_lock = threading.Lock()
_cap_lock = threading.Lock()

# lightweight dummy results/model used when real model fails to load
class _DummyResults:
    def render(self):
        return []
    def pandas(self):
        class _P: 
            xyxy = [None]
        return _P()

class _DummyModel:
    def __call__(self, *args, **kwargs):
        return _DummyResults()

def get_model():
    global _model
    with _model_lock:
        if _model is None:
            REPO = os.path.join(os.path.dirname(__file__), "yolov5")
            weights = os.path.join(os.path.dirname(__file__), "signLang", "weights", "best.pt")
            try:
                # only try load if weights file exists
                if os.path.exists(weights):
                    _model = torch.hub.load(REPO, 'custom', path=weights,
                                           force_reload=False, trust_repo=True, source='local')
                else:
                    print(f"[body.get_model] weights not found at {weights} - using dummy model")
                    _model = _DummyModel()
            except Exception:
                print("[body.get_model] failed to load model, using dummy model")
                traceback.print_exc()
                _model = _DummyModel()
        return _model

def get_cap():
    global _cap
    with _cap_lock:
        if _cap is None:
            try:
                _cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not _cap.isOpened():
                    _cap = cv2.VideoCapture(0)
            except Exception:
                _cap = cv2.VideoCapture(0)
            try:
                _cap.set(cv2.CAP_PROP_FPS, 30)
                _cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                _cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            except Exception:
                pass
        return _cap

# Mediapipe setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.3, min_tracking_confidence=0.3)

# Global variable for sharing latest detected word (thread-safe)
_latest_lock = threading.Lock()
_latest_sign = ""

def set_latest(sign: str):
    global _latest_sign
    with _latest_lock:
        _latest_sign = sign

def get_latest() -> str:
    with _latest_lock:
        return _latest_sign

def draw_landmarks(image, results):
    # check existence before drawing
    if hasattr(results, "left_hand_landmarks") and results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style())
    if hasattr(results, "right_hand_landmarks") and results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style())
    if hasattr(results, "pose_landmarks") and results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing_styles.get_default_pose_landmarks_style())
    return image

letter = ""
offset = 1

def collectData() -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], str]:
    """
    Capture one frame, run Mediapipe + YOLOv5 on it and return:
    (image_with_landmarks, pred_img_rendered, original_frame, crop_bg, detected_label)
    Returns None values if capture failed.
    """
    global letter

    cap = get_cap()
    ret, frame = cap.read()
    if not ret:
        return None, None, None, None, letter

    original = frame.copy()
    crop_bg = np.zeros(frame.shape, dtype=np.uint8)
    black = np.zeros(frame.shape, dtype=np.uint8)

    # Mediapipe detection
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = holistic.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    draw_landmarks(image, results)
    draw_landmarks(black, results)

    # YOLOv5 detection (model returns a Results object)
    model = get_model()
    try:
        yolo_results = model(black)
    except Exception:
        # don't crash — use dummy results
        traceback.print_exc()
        yolo_results = _DummyResults()

    # render() returns list of images; handle safely
    try:
        rendered = yolo_results.render()
        pred_img = np.squeeze(rendered[0]) if isinstance(rendered, (list, tuple)) and len(rendered) > 0 else None
    except Exception:
        pred_img = None

    # iterate detections dataframe safely
    try:
        df = yolo_results.pandas().xyxy[0]
    except Exception:
        df = None

    if df is not None:
        for _, row in df.iterrows():
            conf = float(row.get('confidence', 0.0))
            if conf > 0.8:
                name = str(row.get('name', ''))
                if name and name != letter:
                    letter = name
                    set_latest(letter)
                # compute crop coordinates safely
                x1 = max(int(row.get('xmin', 0)) - offset, 0)
                y1 = max(int(row.get('ymin', 0)) - offset, 0)
                x2 = max(int(row.get('xmax', 0)) + offset, 0)
                y2 = max(int(row.get('ymax', 0)) + offset, 0)
                # ensure bounds
                h, w = pred_img.shape[:2] if pred_img is not None else (0, 0)
                x2 = min(x2, w)
                y2 = min(y2, h)
                if pred_img is not None and y2 > y1 and x2 > x1:
                    crop_img = pred_img[y1:y2, x1:x2]
                    crop_bg[y1:y2, x1:x2] = crop_img
                return image, pred_img, original, crop_bg, name

    return image, pred_img, original, crop_bg, letter

def release_resources():
    global _cap
    try:
        cap = get_cap()
        if cap is not None:
            cap.release()
    except Exception:
        pass
    try:
        _cap = None
    except Exception:
        pass
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

# expose helper for Flask / other modules
latest_sign = get_latest
cleanup = release_resources
