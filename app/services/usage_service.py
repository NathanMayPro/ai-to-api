import datetime
from typing import List, Dict
from ..db.mongodb import MongoDB
from ..models.usage import APIUsage
import logging
from pymongo.database import Database

class UsageService:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db.usage

    def create_usage(self, usage: APIUsage) -> APIUsage:
        """Create a new usage record"""
        try:
            result = self.collection.insert_one(usage.model_dump())
            usage.id = str(result.inserted_id)
            return usage
        except Exception as e:
            logging.error(f"Error creating usage record: {e}")
            raise

    def get_user_usage(self, user_id: str, start_date: datetime.datetime = None, end_date: datetime.datetime = None) -> List[APIUsage]:
        """Get usage statistics for a specific user"""
        try:
            query = {"user_id": user_id}
            if start_date and end_date:
                query["timestamp"] = {
                    "$gte": start_date,
                    "$lte": end_date
                }
            
            return [APIUsage(**usage) for usage in self.collection.find(query)]
        except Exception as e:
            logging.error(f"Error getting user usage: {e}")
            return []

    def calculate_user_costs(self, user_id: str, price_per_call: float = 0.01) -> Dict:
        """Calculate costs for a user based on their API usage"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$endpoint",
                "total_calls": {"$sum": 1},
                "avg_response_time": {"$avg": "$response_time"},
                "total_cost": {"$sum": price_per_call}
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_api_metrics(self, api_id: str) -> Dict:
        """Get metrics for a specific API"""
        pipeline = [
            {"$match": {"api_id": api_id}},
            {"$group": {
                "_id": None,
                "total_calls": {"$sum": 1},
                "avg_response_time": {"$avg": "$response_time"},
                "success_rate": {
                    "$avg": {"$cond": [{"$lt": ["$status_code", 400]}, 1, 0]}
                }
            }}
        ]
        
        return next(self.collection.aggregate(pipeline), None) 

async def get_user_usage_cost(user_id: str, db: Database) -> float:
    """Get the total cost for a user's API usage"""
    try:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_cost": {"$sum": 0.01}  # $0.01 per API call
            }}
        ]
        
        result = await db.usage.aggregate(pipeline).to_list(length=1)
        if result:
            return result[0]["total_cost"]
        return 0.0
    except Exception as e:
        logging.error(f"Error calculating user cost: {e}")
        return 0.0 