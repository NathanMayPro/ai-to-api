from pydantic import BaseModel, ConfigDict, EmailStr

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str | None = None
    email: EmailStr
    username: str
    password_hash: str
    is_admin: bool = False 