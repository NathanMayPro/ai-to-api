from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from bson import ObjectId
import datetime

from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    oauth2_scheme,
)
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, TokenData
from ..db.mongodb import get_database
from ..models.token import Token
from ..services.token_service import TokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_database)
) -> User:
    """Get current authenticated user from token"""
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)

class AuthService:
    def __init__(self, db: MongoClient):
        self.db = db
        self.users_collection = self.db.users

    async def create_user(self, user_data: UserCreate, is_admin: bool = False) -> UserResponse:
        # Check if user exists
        if self.users_collection.find_one({"email": user_data.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            is_admin=is_admin
        )
        
        # If this is the first user, make them an admin
        if await self.users_collection.count_documents({}) == 0:
            user.is_admin = True

        result = await self.users_collection.insert_one(user.model_dump())
        user.id = str(result.inserted_id)
        return UserResponse(**user.model_dump())

    async def create_admin_user(self, user_data: UserCreate) -> UserResponse:
        """Create an admin user. Only works if there are no existing users."""
        if await self.users_collection.count_documents({}) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create admin user: users already exist"
            )
        return await self.create_user(user_data, is_admin=True)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user_dict = self.users_collection.find_one({"email": email})
        if not user_dict:
            return None
        
        user = User(**user_dict)
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        user_dict = self.users_collection.find_one({"email": email})
        if user_dict is None:
            raise credentials_exception

        return User(**user_dict)

    def create_user_token(self, user: User) -> str:
        token_data = {"sub": user.email, "user_id": str(user.id)}
        expires_delta = datetime.timedelta(minutes=30)
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
        
        token_data.update({"exp": expire})
        access_token = create_access_token(token_data)

        # Create token using token service
        token_service = TokenService()
        token = Token(
            user_id=str(user.id),
            token=access_token,
            expires_at=expire,
            description="Login token"
        )
        token_service.create_token(token)
        
        return access_token 