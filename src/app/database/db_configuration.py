from pymongo import MongoClient, errors
from datetime import datetime
import os

class User_Config_Manager:
    def __init__(self, uri=None, db_name="llmExperimenter", collection_name="user_configuration"):
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

    def get_user_configs(self, user_email):
        try:
            cursor = self.collection.find({"email": user_email})
            return list(cursor)
        except errors.PyMongoError as e:
            print(f"Failed to retrieve user configurations: {e}")
            return []

    def close_connection(self):
        if self.client:
            self.client.close()