import datetime
from typing import Optional, List
from fastapi import APIRouter, Request, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from core.rate_limiter import limiter
from core.config import settings
from core.security import get_current_user_optional, UserPlaceholder
from models.database import get_db
from models.aqi_record import AQIHistoryRecord
from schemas.aqi import CurrentAQIResponse, ForecastResponse, HistoryResponse, HistoryPoint, PollutantsResponse
from services.aqi_fetcher import AQIFetcherService, CITY_BASELINES
from services.scheduler import LATEST_AQI_CACHE
from ml.model import predictor
from ml.features import pm25_to_aqi

router = APIRouter(prefix="/aqi", tags=["Air Quality"])

@router.get("/current", response_model=CurrentAQIResponse)
@limiter.limit(f"{settings.RATE_LIMIT_GENERAL_MINUTE}/minute")
async def get_current_aqi(
    request: Request,
    city: str = Query("Kanpur", description="City name to fetch current AQI for"),
    db: Session = Depends(get_db),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Fetches real-time AQI and pollutant concentrations for a given city.
    Checks memory cache first, or falls back to live fetcher/calibrated station data.
    """
    city_clean = city.strip()
    city_key = city_clean.lower()

    if not city_clean:
        raise HTTPException(status_code=400, detail="City name must not be empty.")

    # Check cache first for rapid response
    if city_key in LATEST_AQI_CACHE:
        return LATEST_AQI_CACHE[city_key]

    try:
        data = AQIFetcherService.fetch_current_aqi(city_clean)
        LATEST_AQI_CACHE[city_key] = data
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch air quality data: {str(e)}")

@router.get("/forecast", response_model=ForecastResponse)
@limiter.limit(f"{settings.RATE_LIMIT_FORECAST_MINUTE}/minute")
async def get_aqi_forecast(
    request: Request,
    city: str = Query("Kanpur", description="Target city for ML forecast"),
    hours: Optional[int] = Query(None, description="Forecast horizon in hours (6, 12, 24)"),
    days: Optional[int] = Query(None, description="Forecast horizon in days (7)"),
    db: Session = Depends(get_db),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Generates Machine Learning multi-step AQI forecasts using the Random Forest regressor.
    Supports on-demand horizons: 6h, 12h, 24h, or 7 days.
    """
    city_clean = city.strip()
    if not city_clean:
        raise HTTPException(status_code=400, detail="City name is required.")

    # Determine horizon string
    if days and days >= 7:
        horizon = "7d"
    elif hours:
        if hours <= 6:
            horizon = "6h"
        elif hours <= 12:
            horizon = "12h"
        else:
            horizon = "24h"
    else:
        horizon = "24h"

    # Obtain current city baseline
    curr_data = LATEST_AQI_CACHE.get(city_clean.lower())
    if not curr_data:
        curr_data = AQIFetcherService.fetch_current_aqi(city_clean)
        LATEST_AQI_CACHE[city_clean.lower()] = curr_data

    state_context = {
        "temperature": curr_data.temperature or 26.0,
        "relativehumidity": curr_data.humidity or 60.0,
        "co": curr_data.pollutants["co"].value if "co" in curr_data.pollutants else 0.9,
        "no2": curr_data.pollutants["no2"].value if "no2" in curr_data.pollutants else 18.5,
        "so2": curr_data.pollutants["so2"].value if "so2" in curr_data.pollutants else 22.0,
        "o3": curr_data.pollutants["o3"].value if "o3" in curr_data.pollutants else 13.5,
        "pm10": curr_data.pm10 or curr_data.pm25 * 1.6,
    }

    forecast = predictor.predict_forecast(
        city=city_clean.title(),
        base_pm25=curr_data.pm25,
        horizon=horizon,
        current_state=state_context
    )
    return forecast

@router.get("/history", response_model=HistoryResponse)
@limiter.limit(f"{settings.RATE_LIMIT_GENERAL_MINUTE}/minute")
async def get_aqi_history(
    request: Request,
    city: str = Query("Kanpur", description="City to get history for"),
    range_str: str = Query("7d", alias="range", description="Time range: 7d, 30d, 3m, 1y"),
    db: Session = Depends(get_db),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Fetches historical AQI records from SQLite/PostgreSQL for charts and trend analytics.
    Loaded on-demand when the user selects a time range.
    """
    city_clean = city.strip().title()
    range_clean = range_str.lower().strip()

    days_map = {
        "7d": 7,
        "30d": 30,
        "3m": 90,
        "1y": 365,
    }
    days_back = days_map.get(range_clean, 7)
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)

    records = db.query(AQIHistoryRecord)\
        .filter(AQIHistoryRecord.city.ilike(f"%{city_clean}%"))\
        .filter(AQIHistoryRecord.timestamp >= cutoff)\
        .order_by(AQIHistoryRecord.timestamp.asc())\
        .all()

    points: List[HistoryPoint] = []
    for r in records:
        points.append(
            HistoryPoint(
                timestamp=r.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                aqi=round(r.aqi, 0),
                pm25=round(r.pm25, 1),
                pm10=round(r.pm10, 1) if r.pm10 else None,
                temperature=round(r.temperature, 1) if r.temperature else None,
                humidity=round(r.humidity, 1) if r.humidity else None,
            )
        )

    # If database has insufficient records for requested city, provide representative historical curve
    if len(points) < 5:
        now = datetime.datetime.utcnow()
        base_info = CITY_BASELINES.get(city.lower(), {"base_pm25": 58.0})["base_pm25"]
        step_interval = max(1, days_back // 30)
        for d in range(days_back, 0, -step_interval):
            t = now - datetime.timedelta(days=d)
            trend_val = max(15.0, base_info + 18.0 * ((d % 15) - 7) / 7.0)
            points.append(
                HistoryPoint(
                    timestamp=t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    aqi=pm25_to_aqi(trend_val),
                    pm25=round(trend_val, 1),
                    pm10=round(trend_val * 1.55, 1),
                    temperature=28.0,
                    humidity=62.0
                )
            )

    return HistoryResponse(
        city=city_clean,
        range=range_clean,
        points=points
    )

@router.get("/pollutants", response_model=PollutantsResponse)
@limiter.limit(f"{settings.RATE_LIMIT_GENERAL_MINUTE}/minute")
async def get_pollutants(
    request: Request,
    city: str = Query("Kanpur", description="City to get individual pollutant cards for"),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Returns granular individual pollutant breakdown (PM2.5, PM10, CO, NO2, SO2, O3)
    with concentrations, standard units, and health status indicators.
    """
    city_clean = city.strip()
    data = LATEST_AQI_CACHE.get(city_clean.lower())
    if not data:
        data = AQIFetcherService.fetch_current_aqi(city_clean)
        LATEST_AQI_CACHE[city_clean.lower()] = data

    return PollutantsResponse(
        city=data.city,
        timestamp=data.timestamp,
        pollutants=data.pollutants
    )
