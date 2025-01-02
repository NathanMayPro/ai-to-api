from fastapi import APIRouter, Depends
import datetime
from typing import Optional

from ....services.usage_service import UsageService
from ....services.auth_service import AuthService
from ....models.user import User
from ....db.mongodb import get_database

router = APIRouter()

@router.get("/stats")
async def get_usage_stats(
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    current_user: User = Depends(AuthService(get_database()).get_current_user)
):
    """Get usage statistics for the current user"""
    usage_service = UsageService()
    
    if not start_date:
        start_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
    if not end_date:
        end_date = datetime.datetime.now(datetime.timezone.utc)
    
    usage = usage_service.get_user_usage(str(current_user.id), start_date, end_date)
    costs = usage_service.calculate_user_costs(str(current_user.id))
    
    return {
        "usage": usage,
        "costs": costs,
        "period": {
            "start": start_date,
            "end": end_date
        }
    } 