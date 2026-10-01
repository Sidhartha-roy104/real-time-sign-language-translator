# from backend import mongo
# # create a simple test user
# ok = mongo.insert(
#     name="Test User",
#     email="test@example.com",
#     password="testpass",
#     disability="none",
#     role="tester",
#     dob="2000-01-01",
#     slink="",
#     glink="",
#     llink="",
#     bio="seed user",
#     gender="other"
# )
# print("Inserted:", ok)
# print("Show:", mongo.show("test@example.com"))
import sys
from pathlib import Path
# ensure backend folder is on sys.path so `import mongo` finds local mongo.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mongo

# create a simple test user
ok = mongo.insert(
    name="Test User",
    email="test@example.com",
    password="testpass",
    disability="none",
    role="tester",
    dob="2000-01-01",
    slink="",
    glink="",
    llink="",
    bio="seed user",
    gender="other"
)
print("Inserted:", ok)
print("Show:", mongo.show("test@example.com"))