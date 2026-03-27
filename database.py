from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["clinic_ai"]

appointments = db["appointments"]
patients = db["patients"]