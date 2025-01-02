from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    username: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str

class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    sub: str
    user_id: str | None = None 