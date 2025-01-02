from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import MongoClient
from typing import Annotated

from ....services.auth_service import AuthService
from ....schemas.user import UserCreate, UserResponse
from ....schemas.token import Token
from ....db.mongodb import get_database

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: MongoClient = Depends(get_database)
) -> UserResponse:
    auth_service = AuthService(db)
    return await auth_service.create_user(user_data)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: MongoClient = Depends(get_database)
) -> Token:
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_user_token(user)
    return Token(access_token=access_token, token_type="bearer")
