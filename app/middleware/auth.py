from fastapi import Request, HTTPException, status
from ..services.token_service import TokenService
from ..core.security import verify_token
from starlette.responses import JSONResponse
import logging

async def verify_token_middleware(request: Request, call_next):
    # Skip auth for auth endpoints
    if request.url.path.startswith("/api/v1/auth"):
        return await call_next(request)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_str = auth_header.split(" ")[1]
        logging.info(f"Checking token: {token_str[:10]}...")
        
        # First check if token exists and is active in database
        token_service = TokenService()
        token_doc = token_service.get_token_by_value(token_str)
        logging.info(f"Found token doc: {token_doc.model_dump() if token_doc else None}")
        
        if not token_doc:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token not found"},
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not token_doc.is_active:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token is invalid or revoked"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Then verify JWT validity
        try:
            verify_token(token_str)
        except Exception as e:
            logging.error(f"JWT verification failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token is invalid"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
    except Exception as e:
        logging.error(f"Auth middleware error: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)},
            headers={"WWW-Authenticate": "Bearer"},
        ) 