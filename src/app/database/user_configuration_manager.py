from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "llm_experimenter"
COLLECTION_NAME = "user_configuration"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
user_config_collection = db[COLLECTION_NAME]

DEFAULT_FIELDS = ["temperature", "max_tokens", "top_p", "presence_penalty", "frequency_penalty"]

def get_user_config(user_email: str, fallback: dict) -> dict:
    config = user_config_collection.find_one({"email": user_email})
    if config:
        return {field: config.get(field, fallback[field]) for field in DEFAULT_FIELDS}
    return fallback

def save_user_config(user_email: str, config: dict):
    config_doc = {
        "email": user_email,
        "updated_at": datetime.utcnow(),
    }
    config_doc.update({field: config.get(field) for field in DEFAULT_FIELDS})
    
    user_config_collection.update_one(
        {"email": user_email},
        {"$set": config_doc},
        upsert=True
    )