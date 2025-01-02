from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme), request: Request = None):
    if request and (request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json")):
        return None  # Allow access to docs without authentication
    if token:
        # Here you would normally verify the token and return the user
        # For now, just return a placeholder
        return {"user": "authenticated"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    ) 