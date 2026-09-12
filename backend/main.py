import contextlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.rate_limiter import limiter
from models.database import engine, Base
from services.scheduler import start_scheduler, stop_scheduler
from ml.model import predictor

# Import routers
from routers import aqi, advisory, ai_chat, locations, auth

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    print(f"[App] Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    print(f"[App] Database URL: {settings.DATABASE_URL.split('@')[-1]}")
    print(f"[App] WAQI Key: {settings.redact_key(settings.WAQI_API_KEY)}")
    print(f"[App] OpenAQ Key: {settings.redact_key(settings.OPENAQ_API_KEY)}")
    print(f"[App] Gemini Key: {settings.redact_key(settings.GEMINI_API_KEY)}")

    # Initialize tables
    Base.metadata.create_all(bind=engine)

    # Initialize predictor model
    predictor.load_model()

    # Start background scheduler
    start_scheduler()

    yield

    # Shutdown tasks
    print("[App] Shutting down background tasks...")
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Public API for Air Quality Index (AQI) forecasting, pollutant monitoring, and AI health advisory.",
    lifespan=lifespan
)

# Connect SlowAPI rate limiter
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Returns friendly 429 response when an IP exceeds rate limits."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "You're sending requests too quickly — please wait a moment.",
            "detail": str(exc.detail)
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(aqi.router, prefix=settings.API_V1_STR)
app.include_router(advisory.router, prefix=settings.API_V1_STR)
app.include_router(ai_chat.router, prefix=settings.API_V1_STR)
app.include_router(locations.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)

import os
from fastapi.staticfiles import StaticFiles

# Detect built React frontend dist (for single-container/single-server fullstack serving)
possible_dist_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"),
    os.path.join(os.path.dirname(__file__), "static"),
    "/app/frontend/dist"
]

frontend_dist = None
for p in possible_dist_paths:
    if os.path.isdir(p) and os.path.exists(os.path.join(p, "index.html")):
        frontend_dist = p
        break

if frontend_dist:
    print(f"[App] Serving full-stack React UI from: {frontend_dist}")
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/", tags=["Health Check"])
    async def root():
        return {
            "app": settings.PROJECT_NAME,
            "status": "online",
            "docs": "/docs",
            "version": settings.VERSION,
            "mode": "public_no_auth"
        }

@app.get("/api/health", tags=["Health Check"])
async def health():
    return {
        "status": "healthy",
        "ml_ready": predictor.is_ready,
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
