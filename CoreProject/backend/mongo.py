from urllib.parse import quote_plus
from pymongo import MongoClient
import os

# Use env var if set, otherwise default to local MongoDB
MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://localhost:27017/"

# If you prefer to construct from MONGO_USER/MONGO_PASS:
# user = quote_plus(os.environ.get("MONGO_USER","user"))
# pwd  = quote_plus(os.environ.get("MONGO_PASS","password"))
# MONGO_URI = f"mongodb://{user}:{pwd}@localhost:27017/your_db"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["login_info"]
col = db["login0"]

#Validate email and password
def validate(email,password):
    if email and password:
        data = col.find_one({"email":email,"password":password})
        return bool(data)
    return False

#Insert data into database
def insert(name,email,password,disability,role,dob,slink,glink,llink,bio,gender):
    if name and check(email) and password and disability and role:
        query={"name":name,
               "email":email,
               "password":password,
               "disability":disability,
               "role":role,
               "dob":dob,
               "slink":slink,
               "glink":glink,
               "llink":llink,
               "bio":bio,
               "gender":gender}
        col.insert_one(query)
        return True
    return False

#Update data in database
def update(name,email,disability,role,dob,slink,llink,glink,bio,gender):
    if not check(email):
        if name and email :
            col.update_many({"email":email}, {"$set":{"name":name,"disability":disability,"role":role,"dob":dob,"slink":slink,"glink":glink,"llink":llink,"bio":bio,"gender":gender}})
            return True
    return False

def updatepwd(email,password):
    if not check(email):
        if password and email :
            col.update_many({"email":email}, {"$set":{"password":password}})
            return True
    return False

#Check if email already exists
def check(email):
    if email:
        data=col.find_one({"email":email})
        return False if data else True
    return True

#show all data in database
def show(email):
    if email:
        data=col.find_one({"email":email},{"_id":0})
        return data
    return False

if __name__ == "__main__":
    import sys
    import pymongo
    print("Python:", sys.executable)
    print("pymongo version:", getattr(pymongo, "__version__", "unknown"))
    print("Using MONGO_URI:", MONGO_URI)
    try:
        res = client.admin.command("ping")
        print("Mongo ping:", res)
        sample = col.find_one({}, {"_id": 0})
        print("Sample document:", sample)
    except Exception as e:
        print("Connection/test error:", repr(e))
