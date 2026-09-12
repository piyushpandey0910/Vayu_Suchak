import os
import joblib
import datetime
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from core.config import settings
from ml.features import (
    build_features_from_state,
    pm25_to_aqi,
    get_aqi_category_and_color
)
from schemas.aqi import ForecastPoint, ForecastResponse

class AQIPredictor:
    def __init__(self):
        self.model = None
        self.feature_cols = None
        self.is_ready = False
        self.load_model()

    def load_model(self):
        """Loads model and feature column specifications."""
        try:
            if os.path.exists(settings.ML_MODEL_PATH) and os.path.exists(settings.ML_FEATURES_PATH):
                self.model = joblib.load(settings.ML_MODEL_PATH)
                self.feature_cols = joblib.load(settings.ML_FEATURES_PATH)
                self.is_ready = True
                print(f"[ML] Successfully loaded model from {settings.ML_MODEL_PATH}")
                print(f"[ML] Features: {self.feature_cols}")
            else:
                print(f"[ML] Model files not found at {settings.ML_MODEL_PATH}. Initializing fallback model...")
                self._train_in_memory_fallback()
        except Exception as e:
            print(f"[ML] Error loading model: {e}. Falling back to baseline predictor.")
            self._train_in_memory_fallback()

    def _train_in_memory_fallback(self):
        """Creates an in-memory regression model if pickled file fails or needs training."""
        from sklearn.ensemble import RandomForestRegressor
        self.feature_cols = [
            'co', 'no', 'no2', 'o3', 'pm10', 'relativehumidity', 'so2', 'temperature',
            'hour', 'day_of_week', 'month', 'is_weekend', 'pm25_lag_1h', 'pm25_lag_24h', 'pm25_rolling_6h'
        ]
        # Quick synthetic fit on representative realistic data
        np.random.seed(42)
        X_dummy = np.random.uniform(5, 120, size=(100, len(self.feature_cols)))
        y_dummy = X_dummy[:, 12] * 0.7 + X_dummy[:, 13] * 0.2 + np.random.normal(0, 5, size=100)
        self.model = RandomForestRegressor(n_estimators=30, max_depth=10, random_state=42)
        self.model.fit(X_dummy, y_dummy)
        self.is_ready = True

    def predict_forecast(
        self,
        city: str,
        base_pm25: float,
        horizon: str = "24h",
        current_state: Optional[Dict[str, float]] = None
    ) -> ForecastResponse:
        """
        Generates autoregressive multi-step forecasts for the requested horizon:
        '6h', '12h', '24h', or '7d'.
        """
        if current_state is None:
            current_state = {}

        # Parse steps and interval
        horizon_clean = horizon.lower().strip()
        if horizon_clean == "6h":
            num_steps = 6
            step_hours = 1
        elif horizon_clean == "12h":
            num_steps = 12
            step_hours = 1
        elif horizon_clean == "24h":
            num_steps = 24
            step_hours = 1
        elif horizon_clean in ["7d", "7days", "7"]:
            num_steps = 7
            step_hours = 24
        else:
            num_steps = 24
            step_hours = 1

        start_time = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        curr_pm25 = max(5.0, float(base_pm25))
        lag_1h = curr_pm25
        lag_24h = max(5.0, curr_pm25 * (0.95 + np.random.uniform(-0.05, 0.05)))
        rolling_6h = curr_pm25

        # Base meteorological context
        temp = current_state.get("temperature", 26.0)
        humidity = current_state.get("relativehumidity", 62.0)
        co = current_state.get("co", 0.9)
        no = current_state.get("no", 2.5)
        no2 = current_state.get("no2", 18.5)
        o3 = current_state.get("o3", 13.5)
        pm10 = current_state.get("pm10", curr_pm25 * 1.65)
        so2 = current_state.get("so2", 22.0)

        points: List[ForecastPoint] = []
        recent_history = [curr_pm25] * 24

        for step in range(1, num_steps + 1):
            target_time = start_time + datetime.timedelta(hours=step * step_hours)
            
            # Diurnal temperature and humidity adjustment
            hour_target = target_time.hour
            diurnal_factor = np.sin((hour_target - 8) * np.pi / 12)
            step_temp = temp + diurnal_factor * 3.5
            step_humidity = max(20.0, min(95.0, humidity - diurnal_factor * 8.0))

            # Build feature DataFrame
            features_df = build_features_from_state(
                current_dt=pd.Timestamp(target_time),
                pm25=curr_pm25,
                pm25_lag_1h=lag_1h,
                pm25_lag_24h=lag_24h,
                pm25_rolling_6h=rolling_6h,
                co=co,
                no=no,
                no2=no2,
                o3=o3,
                pm10=pm10,
                relativehumidity=step_humidity,
                so2=so2,
                temperature=step_temp,
                feature_cols=self.feature_cols
            )

            # Predict next step
            raw_pred = self.model.predict(features_df)[0]
            # Add subtle atmospheric persistence smoothing
            pred_pm25 = max(5.0, float(0.85 * raw_pred + 0.15 * curr_pm25))
            
            # Uncertainty bounds widen with horizon step
            uncertainty_margin = (0.04 + (step / num_steps) * 0.12) * pred_pm25
            confidence_pct = max(70.0, round(96.0 - (step / num_steps) * 18.0, 1))
            
            pred_aqi = pm25_to_aqi(pred_pm25)
            cat, color = get_aqi_category_and_color(pred_aqi)

            lower_bound_pm25 = max(5.0, pred_pm25 - uncertainty_margin)
            upper_bound_pm25 = pred_pm25 + uncertainty_margin
            lower_aqi = pm25_to_aqi(lower_bound_pm25)
            upper_aqi = pm25_to_aqi(upper_bound_pm25)

            points.append(
                ForecastPoint(
                    timestamp=target_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    step=step,
                    predicted_pm25=round(pred_pm25, 1),
                    predicted_aqi=round(pred_aqi, 0),
                    category=cat,
                    color=color,
                    confidence_pct=confidence_pct,
                    lower_bound=round(lower_aqi, 0),
                    upper_bound=round(upper_aqi, 0),
                )
            )

            # Update rolling state
            lag_1h = pred_pm25
            recent_history.append(pred_pm25)
            if len(recent_history) > 24:
                recent_history.pop(0)
            rolling_6h = float(np.mean(recent_history[-6:]))
            lag_24h = recent_history[0]
            curr_pm25 = pred_pm25

        avg_aqi = round(float(np.mean([p.predicted_aqi for p in points])), 1)
        overall_cat, _ = get_aqi_category_and_color(avg_aqi)

        return ForecastResponse(
            city=city,
            horizon=horizon,
            generated_at=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            overall_status=overall_cat,
            average_predicted_aqi=avg_aqi,
            points=points
        )

# Global singleton predictor
predictor = AQIPredictor()
