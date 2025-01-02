from pydantic import BaseModel, ConfigDict
import datetime

class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str | None = None
    user_id: str
    token: str
    is_active: bool = True
    created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    expires_at: datetime.datetime
    last_used: datetime.datetime | None = None
    description: str = "Login token" 