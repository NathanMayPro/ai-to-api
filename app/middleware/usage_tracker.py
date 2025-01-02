from fastapi import Request
import time
import logging
from ..db.mongodb import MongoDB
from ..models.usage import APIUsage
from ..services.token_service import TokenService
from ..services.usage_service import UsageService
from ..core.security import verify_token

async def track_usage(request: Request, call_next):
    # Start timing
    start_time = time.time()
    
    # Initialize variables
    token_str = None
    token_id = None
    user_id = None
    
    # Get token from authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header.split(" ")[1]
        try:
            # Get user_id from token payload
            payload = verify_token(token_str)
            user_id = payload.get("user_id")
            
            # Get token details
            token_service = TokenService()
            token_doc = token_service.get_token_by_value(token_str)
            if token_doc:
                token_id = token_doc.id
                token_service.update_last_used(token_str)
        except Exception as e:
            logging.error(f"Error processing token: {e}")
            pass
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000
    
    if user_id and token_str:
        # Create and store usage record
        try:
            usage = APIUsage(
                user_id=user_id,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                token=token_str,
                token_id=token_id
            )
            
            usage_service = UsageService()
            usage_service.create_usage(usage)
        except Exception as e:
            logging.error(f"Error tracking usage: {e}")
    
    return response 