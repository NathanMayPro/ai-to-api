from typing import Optional
from pymongo import MongoClient
from ..core.config import settings

class MongoDB:
    client: Optional[MongoClient] = None
    db = None  # Remove type hint as it's causing issues with bool check

    @classmethod
    def connect_to_mongo(cls):
        if cls.client is None:
            cls.client = MongoClient(settings.mongodb_url)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            print("Connected to MongoDB!")

    @classmethod
    def close_mongo_connection(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            print("MongoDB connection closed!")

    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.connect_to_mongo()
        return cls.db

def get_database():
    return MongoDB.get_db() 