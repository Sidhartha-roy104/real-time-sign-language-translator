# Real-time Sign Language Translator

A Windows-oriented prototype that recognizes a limited set of sign-language gestures from a webcam. It combines MediaPipe Holistic landmarks with local YOLOv5 weights and presents the result through a Flask web interface. A separate script can publish the annotated video to a virtual camera.

## What currently works

- **Web application:** webcam preview with hand and pose landmarks, YOLOv5 detection, and a detected-label display.
- **Accounts:** sign-up, login, profile viewing, password change, and profile updates backed by MongoDB.
- **Virtual camera mode:** `SignCam.py` sends annotated frames through `pyvirtualcam` for use by applications such as OBS or video-conferencing software.
- **Supported model assets:**
	- `CoreProject/signLang/weights/best.pt` is loaded by the Flask pipeline.
	- `CoreProject/modelS/weights/best.pt` is loaded by the virtual-camera script.
	- `CoreProject/modelN800/weights/best.pt` is available as another trained model but is not selected by the current scripts.

The project is a gesture recognizer, not a complete speech-to-sign or sign-to-speech translator. The `/audio` page is present in the UI, but there is no implemented speech-recognition or text-to-speech pipeline in the current code.

## How the project works

```text
Webcam
	-> OpenCV frame capture
	-> MediaPipe Holistic landmarks
	-> black landmark image
	-> local YOLOv5 model
	-> detected class name
	-> Flask MJPEG stream and label
```

The main flow lives in `CoreProject/body.py`:

1. `get_cap()` opens camera `0` lazily at up to 1280x720 and 30 FPS.
2. `collectData()` processes each frame with MediaPipe.
3. YOLOv5 runs against the landmark image and accepts detections above 0.80 confidence.
4. `CoreProject/app.py` exposes the annotated frames through `/video` and renders the UI templates.

`CoreProject/SignCam.py` uses a separate inference loop, a 0.90 confidence threshold, and `modelS/weights/best.pt` before sending frames to a virtual camera.

## Project layout

```text
CoreProject/
	app.py                  Flask routes and web server
	body.py                 Webcam, MediaPipe, and Flask inference pipeline
	SignCam.py              Standalone virtual-camera pipeline
	config.py               Dataset label list and training image path
	requirements.txt        Python dependencies
	backend/mongo.py        MongoDB connection and account operations
	templates/              Jinja HTML pages
	static/                 CSS and image assets
	signLang/weights/       Weights used by the Flask pipeline
	modelS/weights/         Weights used by SignCam.py
	modelN800/weights/      Additional trained weights
	yolov5/                 Local YOLOv5 source used with torch.hub
	smart-callback-app/     Placeholder; not currently implemented
```

## Prerequisites

- Windows with a working webcam.
- Python 3.10 or 3.11 is recommended for the pinned 2023-era dependencies.
- A local MongoDB server, or a reachable MongoDB connection string.
- Git is useful if you need to clone or update the repository.
- OBS Studio is optional and useful when consuming the virtual-camera output.
- A CUDA-capable PyTorch installation is optional. CPU inference can work, but it will usually be slower.

## Installation

From the repository root:

```powershell
cd CoreProject
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install PyTorch separately if it is not already available. Choose the command that matches your hardware from the [official PyTorch installer](https://pytorch.org/get-started/locally/). For the CUDA 11.7 command used by the original project, the historical form was:

```powershell
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

The exact PyTorch build should match the Python version and installed NVIDIA driver. The repository requirements file does not pin `torch` explicitly.

## Configuration

`CoreProject/backend/mongo.py` uses this default connection:

```text
mongodb://localhost:27017/
```

Use `MONGO_URI` to override it:

```powershell
$env:MONGO_URI = "mongodb://localhost:27017/"
```

The application stores data in database `login_info`, collection `login0`. Start MongoDB before using sign-up or login. Camera inference can still be inspected independently, but account pages may fail when MongoDB is unavailable.

## Run the Flask application

From `CoreProject` with the virtual environment activated:

```powershell
python app.py
```

The app listens on `http://127.0.0.1:5000/` and attempts to open that URL automatically. If the browser does not open, visit it manually.

Useful pages and endpoints:

| Path | Purpose |
| --- | --- |
| `/` | Login page |
| `/signup` | Account creation |
| `/index` or `/home` | Main application page |
| `/translate` | Translation page |
| `/video` | Multipart MJPEG webcam stream |
| `/label` | Latest detected label as JSON |
| `/profile` | Profile page |
| `/about` | About page |
| `/audio` | Audio UI placeholder |
| `/features` | Features page |

Open `/translate` to start the camera workflow. The first inference can take longer while the local model is loaded.

## Run virtual-camera mode

Run this in a separate terminal from `CoreProject`:

```powershell
python SignCam.py
```

The script captures camera `0`, draws the detected sign on the frame, and publishes 1280x720 video at 30 FPS through `pyvirtualcam`. Select the resulting virtual camera in OBS or another supported application. Stop it with `Ctrl+C`.

Do not run the Flask and virtual-camera scripts at the same time if both need exclusive access to the same physical webcam.

## Troubleshooting

### Camera does not open

- Close other apps using the webcam.
- Check Windows camera permissions.
- Try another camera index in `body.py` or `SignCam.py` instead of `0`.
- On Windows, the code first tries DirectShow (`cv2.CAP_DSHOW`) and then falls back to the default OpenCV backend.

### Model loading fails

- Confirm `CoreProject/signLang/weights/best.pt` exists for Flask mode.
- Confirm `CoreProject/modelS/weights/best.pt` exists for virtual-camera mode.
- Verify that PyTorch is installed and compatible with the selected Python version.
- Flask mode falls back to a dummy model when its weights cannot be loaded, so the page may open without producing detections.

### MongoDB errors

- Start MongoDB and verify the `MONGO_URI` value.
- Test the connection with:

	```powershell
	python backend\mongo.py
	```

## Important limitations

- Credentials are currently stored as plain text in MongoDB; this is not production-safe.
- Flask uses a placeholder secret key in `app.py`; set a secure value before deployment.
- The application is a prototype with global state and a single webcam stream. It is not designed for multi-user production hosting.
- The virtual-camera script and Flask app use different model files and thresholds.
- `smart-callback-app` contains a small frontend skeleton, but its backend and README are empty; treat it as unfinished work.

## Development notes

The local `yolov5` directory is used by `torch.hub.load(..., source="local")`, so it must remain alongside the model and application directories. The model class names determine the labels shown by the UI; `config.py` documents the intended training vocabulary, but it is not itself used for runtime inference.

## License

See [LICENSE](LICENSE).

