from fastapi import APIRouter
from .endpoints import auth, test, usage, tokens, users

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    test.router,
    prefix="/test",
    tags=["test"]
)

api_router.include_router(
    usage.router,
    prefix="/usage",
    tags=["usage"]
)

api_router.include_router(
    tokens.router,
    prefix="/tokens",
    tags=["tokens"]
) 

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)