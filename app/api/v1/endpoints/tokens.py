from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ....services.token_service import TokenService
from ....services.auth_service import AuthService
from ....models.token import Token
from ....models.user import User
from ....db.mongodb import get_database

router = APIRouter()

@router.get("/", response_model=List[Token])
async def list_tokens(
    current_user: User = Depends(AuthService(get_database()).get_current_user)
):
    """List all tokens for the current user"""
    token_service = TokenService()
    return token_service.get_user_tokens(str(current_user.id))

@router.get("/{token_id}", response_model=Token)
async def get_token(
    token_id: str,
    current_user: User = Depends(AuthService(get_database()).get_current_user)
):
    """Get specific token details"""
    token_service = TokenService()
    token = token_service.get_token(token_id)
    
    if not token or token.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Token not found")
    
    return token

@router.delete("/{token_id}")
async def revoke_token(
    token_id: str,
    current_user: User = Depends(AuthService(get_database()).get_current_user)
):
    """Revoke a specific token"""
    token_service = TokenService()
    token = token_service.get_token(token_id)
    
    if not token or token.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Token not found")
    
    token_service.deactivate_token(token_id)
    return {"message": "Token revoked successfully"} 