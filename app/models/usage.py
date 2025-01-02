from pydantic import BaseModel, ConfigDict
import datetime

class APIUsage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str | None = None
    user_id: str
    token: str
    token_id: str | None = None
    endpoint: str
    method: str = "GET"
    status_code: int = 200
    response_time: float
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) 