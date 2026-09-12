import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

# Official AQI Categorization per prompt specifications
AQI_CATEGORIES = [
    (0, 50, "Good", "#22C55E"),
    (51, 100, "Moderate", "#EAB308"),
    (101, 150, "Unhealthy for Sensitive Groups", "#F97316"),
    (151, 200, "Unhealthy", "#EF4444"),
    (201, 300, "Very Unhealthy", "#A855F7"),
    (301, 500, "Hazardous", "#7F1D1D"),
]

def get_aqi_category_and_color(aqi: float) -> Tuple[str, str]:
    """Returns the category label and hex color code for a given AQI value."""
    aqi_val = max(0.0, float(aqi))
    for low, high, category, color in AQI_CATEGORIES:
        if aqi_val <= high:
            return category, color
    return "Hazardous", "#7F1D1D"

def pm25_to_aqi(pm25: float) -> float:
    """
    Computes standard Air Quality Index (AQI) from PM2.5 concentration (ug/m3)
    using standard linear piecewise interpolation (CPCB / EPA conversion).
    """
    c = max(0.0, float(pm25))
    # Breakpoints: (C_low, C_high, I_low, I_high)
    breakpoints = [
        (0.0, 30.0, 0.0, 50.0),
        (30.1, 60.0, 51.0, 100.0),
        (60.1, 90.0, 101.0, 200.0),
        (90.1, 120.0, 201.0, 300.0),
        (120.1, 250.0, 301.0, 400.0),
        (250.1, 500.0, 401.0, 500.0),
    ]

    for c_low, c_high, i_low, i_high in breakpoints:
        if c <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low
            return round(aqi, 1)

    # Beyond 500 ug/m3
    return min(500.0, round(400.0 + (c - 250.0) * 0.4, 1))

def aqi_to_pm25(aqi: float) -> float:
    """Inverse mapping from AQI to approximate PM2.5."""
    a = max(0.0, float(aqi))
    if a <= 50:
        return round(a * (30.0 / 50.0), 1)
    elif a <= 100:
        return round(30.0 + (a - 50.0) * (30.0 / 50.0), 1)
    elif a <= 200:
        return round(60.0 + (a - 100.0) * (30.0 / 100.0), 1)
    elif a <= 300:
        return round(90.0 + (a - 200.0) * (30.0 / 100.0), 1)
    elif a <= 400:
        return round(120.0 + (a - 300.0) * (130.0 / 100.0), 1)
    else:
        return round(250.0 + (a - 400.0) * 1.5, 1)

def build_features_from_state(
    current_dt: pd.Timestamp,
    pm25: float,
    pm25_lag_1h: float,
    pm25_lag_24h: float,
    pm25_rolling_6h: float,
    co: float = 0.9,
    no: float = 2.5,
    no2: float = 18.5,
    o3: float = 13.0,
    pm10: float = 105.0,
    relativehumidity: float = 65.0,
    so2: float = 24.0,
    temperature: float = 25.0,
    feature_cols: list = None
) -> pd.DataFrame:
    """
    Constructs a 1-row DataFrame strictly matching the model feature signature:
    ['co', 'no', 'no2', 'o3', 'pm10', 'relativehumidity', 'so2', 'temperature',
     'hour', 'day_of_week', 'month', 'is_weekend', 'pm25_lag_1h', 'pm25_lag_24h', 'pm25_rolling_6h']
    """
    hour = current_dt.hour
    day_of_week = current_dt.dayofweek
    month = current_dt.month
    is_weekend = int(day_of_week >= 5)

    data = {
        "co": [co],
        "no": [no],
        "no2": [no2],
        "o3": [o3],
        "pm10": [pm10],
        "relativehumidity": [relativehumidity],
        "so2": [so2],
        "temperature": [temperature],
        "hour": [hour],
        "day_of_week": [day_of_week],
        "month": [month],
        "is_weekend": [is_weekend],
        "pm25_lag_1h": [pm25_lag_1h],
        "pm25_lag_24h": [pm25_lag_24h],
        "pm25_rolling_6h": [pm25_rolling_6h],
    }
    df = pd.DataFrame(data)
    if feature_cols:
        df = df[feature_cols]
    return df
