from fastapi import FastAPI

from app.core.config import settings
from app.routers.auth_routes import router as auth_router


app = FastAPI(
    title=settings.app_name,
    description="Standalone authentication microservice with JWT security",
    version="1.0.0",
)


# Register authentication endpoints
app.include_router(auth_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "ShopEase Authentication Service is running",
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "service": "authentication",
    }
