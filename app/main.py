from fastapi import FastAPI

from app.api.v1.endpoints import health
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health.router)
app.include_router(api_router, prefix="/api/v1")

# hello 
