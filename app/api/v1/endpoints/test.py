from fastapi import APIRouter, Depends, HTTPException, Path
import asyncio
from ....services.auth_service import AuthService, get_current_user
from ....models.user import User
from ....db.mongodb import get_database
from typing import Dict

router = APIRouter()

@router.get("/sleep/{seconds}")
async def sleep_endpoint(
    seconds: int = Path(..., ge=1, le=10),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Test endpoint that sleeps for specified seconds"""
    await asyncio.sleep(seconds)
    return {
        "status": "OK",
        "slept_for": seconds,
        "user": current_user.model_dump()
    } 