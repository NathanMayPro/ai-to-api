from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.models.user import User
from app.models.usage import APIUsage
from app.services.auth_service import get_current_user
from app.services.usage_service import get_user_usage_cost
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user), db=Depends(get_database)):
    """
    Get all users and their details. Only accessible by admin users.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this endpoint"
        )
    
    users_collection = db["users"]
    users = await users_collection.find().to_list(length=None)
    return users

@router.get("/users/costs")
async def get_users_costs(current_user: User = Depends(get_current_user), db=Depends(get_database)):
    """
    Get all users and their associated costs. Only accessible by admin users.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this endpoint"
        )
    
    users_collection = db["users"]
    users = await users_collection.find().to_list(length=None)
    
    user_costs = []
    for user in users:
        cost = await get_user_usage_cost(user["id"], db)
        user_costs.append({
            "user_id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "total_cost": cost
        })
    
    return user_costs
