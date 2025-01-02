from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from .db.mongodb import MongoDB
from .api.v1.router import api_router
from .middleware.usage_tracker import track_usage
from .middleware.auth import verify_token_middleware
from .dependencies import get_optional_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    MongoDB.connect_to_mongo()
    yield
    # Shutdown
    MongoDB.close_mongo_connection()

app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_optional_user)])

# Add middlewares in correct order
app.middleware("http")(verify_token_middleware)  # Auth first
app.middleware("http")(track_usage)  # Then usage tracking

app.include_router(api_router, prefix="/api/v1") 