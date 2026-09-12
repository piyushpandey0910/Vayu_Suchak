from typing import List, Optional
from fastapi import APIRouter, Request, Query, Depends
from core.rate_limiter import limiter
from core.config import settings
from core.security import get_current_user_optional, UserPlaceholder
from schemas.locations import LocationSearchResponse, LocationItem

router = APIRouter(prefix="/locations", tags=["Locations"])

# Searchable catalog of Indian and international locations
LOCATIONS_CATALOG = [
    LocationItem(city="Kanpur", state="Uttar Pradesh", country="India", lat=26.4499, lon=80.3319),
    LocationItem(city="Delhi", state="National Capital Territory", country="India", lat=28.6139, lon=77.2090),
    LocationItem(city="Mumbai", state="Maharashtra", country="India", lat=19.0760, lon=72.8777),
    LocationItem(city="Bengaluru", state="Karnataka", country="India", lat=12.9716, lon=77.5946),
    LocationItem(city="Lucknow", state="Uttar Pradesh", country="India", lat=26.8467, lon=80.9462),
    LocationItem(city="Kolkata", state="West Bengal", country="India", lat=22.5726, lon=88.3639),
    LocationItem(city="Hyderabad", state="Telangana", country="India", lat=17.3850, lon=78.4867),
    LocationItem(city="Chennai", state="Tamil Nadu", country="India", lat=13.0827, lon=80.2707),
    LocationItem(city="Pune", state="Maharashtra", country="India", lat=18.5204, lon=73.8567),
    LocationItem(city="Ahmedabad", state="Gujarat", country="India", lat=23.0225, lon=72.5714),
    LocationItem(city="Varanasi", state="Uttar Pradesh", country="India", lat=25.3176, lon=82.9739),
    LocationItem(city="Jaipur", state="Rajasthan", country="India", lat=26.9124, lon=75.7873),
    LocationItem(city="Agra", state="Uttar Pradesh", country="India", lat=27.1767, lon=78.0081),
    LocationItem(city="Patna", state="Bihar", country="India", lat=25.5941, lon=85.1376),
    LocationItem(city="Bhopal", state="Madhya Pradesh", country="India", lat=23.2599, lon=77.4126),
    LocationItem(city="Chandigarh", state="Punjab / Haryana", country="India", lat=30.7333, lon=76.7794),
    LocationItem(city="Noida", state="Uttar Pradesh", country="India", lat=28.5355, lon=77.3910),
    LocationItem(city="Gurugram", state="Haryana", country="India", lat=28.4595, lon=77.0266),
    LocationItem(city="London", state="England", country="United Kingdom", lat=51.5074, lon=-0.1278),
    LocationItem(city="New York", state="New York", country="United States", lat=40.7128, lon=-74.0060),
]

@router.get("/search", response_model=LocationSearchResponse)
@limiter.limit(f"{settings.RATE_LIMIT_GENERAL_MINUTE}/minute")
async def search_locations(
    request: Request,
    q: str = Query("", description="Location query term"),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Searches available cities and monitoring stations.
    Debounced on frontend to avoid extraneous calls.
    """
    query_clean = q.strip().lower()
    if not query_clean:
        # Return popular default suggestions
        results = LOCATIONS_CATALOG[:6]
    else:
        results = [
            loc for loc in LOCATIONS_CATALOG
            if query_clean in loc.city.lower() or (loc.state and query_clean in loc.state.lower())
        ]
        # If no exact catalog match, return user's custom query dynamically
        if not results:
            results = [LocationItem(city=q.strip().title(), state="Monitored Area", country="India")]

    return LocationSearchResponse(
        query=q,
        results=results[:8]
    )
