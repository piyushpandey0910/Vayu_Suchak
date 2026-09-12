from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/auth", tags=["Authentication (Placeholder)"])

@router.get("/status")
async def auth_status():
    """
    Informational placeholder endpoint documenting future auth support.
    In v1, all core endpoints are fully public without authentication.
    """
    return {
        "auth_enabled": False,
        "mode": "public_access",
        "message": "Vayu Suchak is currently running in public no-login mode. Authentication hooks are ready for future JWT/OAuth integration."
    }

@router.post("/login")
async def login_placeholder():
    raise HTTPException(
        status_code=501,
        detail="Authentication is planned for a future release. Currently, all features are freely available without login."
    )
