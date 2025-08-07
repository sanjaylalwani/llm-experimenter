from pymongo import MongoClient, errors
from datetime import datetime
import os

class HistoryManager:
    def __init__(self, uri=None, db_name="llmExperimenter", collection_name="history"):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._connect_to_db()

    def _connect_to_db(self):
        try:
            self.client = MongoClient(self.mongo_uri)
            db = self.client[self.db_name]
            self.collection = db[self.collection_name]
        except errors.ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            raise

    def save_history(self, user, session_id, model, prompt, response):
        if not all([user, session_id, model, prompt, response]):
            raise ValueError("All fields are required to save history.")
        history_doc = {
            "user": user,
            "session_id": session_id,
            "model": model,
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.utcnow()
        }
        try:
            self.collection.insert_one(history_doc)
        except errors.PyMongoError as e:
            print(f"Failed to insert history document: {e}")
            raise

    def get_history(self, user, limit=10):
        try:
            cursor = self.collection.find({"user": user})\
                                    .sort("timestamp", -1)\
                                    .limit(limit)
            return list(cursor)
        except errors.PyMongoError as e:
            print(f"Failed to retrieve history: {e}")
            return []

    def close_connection(self):
        if self.client:
            self.client.close()