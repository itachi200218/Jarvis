import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

users_collection = db["users"]
