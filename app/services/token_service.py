import datetime
from typing import List
from ..db.mongodb import MongoDB
from ..models.token import Token
from bson.objectid import ObjectId
import logging

class TokenService:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.collection = self.db.tokens

    def create_token(self, token: Token) -> Token:
        """Create a new token"""
        # Generate ID before inserting
        token.id = str(ObjectId())
        result = self.collection.insert_one(token.model_dump())
        return token

    def get_user_tokens(self, user_id: str) -> List[Token]:
        return [Token(**token) for token in self.collection.find({"user_id": user_id})]

    def get_token(self, token_id: str) -> Token | None:
        """Get token by its ID"""
        try:
            token_data = self.collection.find_one({"id": token_id})
            logging.info(f"Getting token by ID {token_id}, found: {token_data}")
            return Token(**token_data) if token_data else None
        except Exception as e:
            logging.error(f"Error getting token: {e}")
            return None

    def deactivate_token(self, token_id: str) -> bool:
        """Deactivate a token"""
        try:
            logging.info(f"Deactivating token {token_id}")
            result = self.collection.update_one(
                {"id": token_id},  # Use the stored ID field
                {"$set": {"is_active": False}}
            )
            logging.info(f"Deactivation result: {result.modified_count}")
            
            # Verify the update
            token = self.get_token(token_id)
            logging.info(f"Token after deactivation: {token.model_dump() if token else None}")
            
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error deactivating token: {e}")
            return False

    def get_token_by_value(self, token_value: str) -> Token | None:
        """Get token by its value"""
        try:
            token_data = self.collection.find_one({"token": token_value})
            if not token_data:
                return None
            
            # Ensure ID is set
            if "_id" in token_data:
                token_data["id"] = str(token_data["_id"])
                # Update the stored document with the id field
                self.collection.update_one(
                    {"_id": token_data["_id"]},
                    {"$set": {"id": token_data["id"]}}
                )
                
            logging.info(f"Found token data: {token_data}")
            return Token(**token_data) if token_data else None
        except Exception as e:
            logging.error(f"Error getting token by value: {e}")
            return None

    def update_last_used(self, token: str) -> bool:
        result = self.collection.update_one(
            {"token": token},
            {"$set": {"last_used": datetime.datetime.now(datetime.timezone.utc)}}
        )
        return result.modified_count > 0 