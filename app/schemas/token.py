from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str
    token_type: str = "bearer" 