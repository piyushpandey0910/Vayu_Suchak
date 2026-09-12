"""
Offline training and evaluation script for Vayu Suchak AQI Prediction.
Evaluates multiple model candidates using time-based train/test splits.
Reports MAE, RMSE, and R2 metrics, and saves the best model artifact.
"""

import os
from typing import Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "kanpur_clean_wide.csv")
MODEL_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "aqi_model.pkl")
FEATURES_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "model_features.pkl")

def load_and_preprocess_data(csv_path: str) -> Tuple[pd.DataFrame, list]:
    print(f"[Train] Reading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)

    # Drop columns if present
    cols_to_drop = [c for c in ["nox", "wind_direction", "wind_speed"] if c in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    # Forward fill / backward fill numeric columns
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    # Cap outliers at 99th percentile
    cap = df["pm25"].quantile(0.99)
    df = df[df["pm25"] <= cap]
    print(f"[Train] PM2.5 capped at 99th percentile: {cap:.2f} ug/m3")

    # Time features
    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Lag features & rolling average (15-min intervals: 4 steps = 1h, 96 steps = 24h, 24 steps = 6h)
    df["pm25_lag_1h"] = df["pm25"].shift(4)
    df["pm25_lag_24h"] = df["pm25"].shift(96)
    df["pm25_rolling_6h"] = df["pm25"].rolling(24).mean()

    df = df.dropna().reset_index(drop=True)
    feature_cols = [c for c in df.columns if c not in ["datetime", "pm25"]]
    print(f"[Train] Dataset shape after feature engineering: {df.shape}")
    print(f"[Train] Features ({len(feature_cols)}): {feature_cols}")
    return df, feature_cols

def train_and_evaluate():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

    df, feature_cols = load_and_preprocess_data(DATA_PATH)

    # Time-based split: First 80% for training, remaining 20% held-out test
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train, y_train = train_df[feature_cols], train_df["pm25"]
    X_test, y_test = test_df[feature_cols], test_df["pm25"]

    print(f"[Train] Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    candidates = {
        "Ridge Regression (Baseline)": Ridge(alpha=1.0),
        "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=150, max_depth=10, random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=15, n_jobs=-1, random_state=42)
    }

    results = {}
    best_name = None
    best_r2 = -1.0
    best_model = None

    print("\n" + "="*70)
    print(f"{'Model Candidate':<30} | {'MAE':<8} | {'RMSE':<8} | {'R2 Score':<8}")
    print("="*70)

    for name, model in candidates.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        results[name] = {"MAE": mae, "RMSE": rmse, "R2": r2, "model": model}
        print(f"{name:<30} | {mae:<8.3f} | {rmse:<8.3f} | {r2:<8.3f}")

        if r2 > best_r2:
            best_r2 = r2
            best_name = name
            best_model = model

    print("="*70)
    print(f"--> Selected Best Model: '{best_name}' with R2={best_r2:.4f}")

    # Save best model and features
    print(f"[Train] Saving model to: {MODEL_OUTPUT_PATH}")
    joblib.dump(best_model, MODEL_OUTPUT_PATH)
    print(f"[Train] Saving features to: {FEATURES_OUTPUT_PATH}")
    joblib.dump(feature_cols, FEATURES_OUTPUT_PATH)
    print("[Train] Training complete successfully!")

if __name__ == "__main__":
    from typing import Tuple
    train_and_evaluate()
