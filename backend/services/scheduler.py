import datetime
import os
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from models.database import SessionLocal
from models.aqi_record import AQIHistoryRecord
from services.aqi_fetcher import AQIFetcherService, CITY_BASELINES
from ml.features import pm25_to_aqi
from core.config import settings

# Memory cache for fast responses
LATEST_AQI_CACHE = {}

def refresh_city_data(city: str):
    """Fetches real-time AQI and records to cache and database."""
    try:
        data = AQIFetcherService.fetch_current_aqi(city)
        LATEST_AQI_CACHE[city.lower()] = data

        # Persist to database
        db = SessionLocal()
        try:
            record = AQIHistoryRecord(
                city=data.city,
                timestamp=datetime.datetime.utcnow(),
                aqi=data.aqi,
                pm25=data.pm25,
                pm10=data.pm10,
                co=data.pollutants["co"].value if "co" in data.pollutants else None,
                no2=data.pollutants["no2"].value if "no2" in data.pollutants else None,
                so2=data.pollutants["so2"].value if "so2" in data.pollutants else None,
                o3=data.pollutants["o3"].value if "o3" in data.pollutants else None,
                temperature=data.temperature,
                humidity=data.humidity,
                source=data.source
            )
            db.add(record)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"[Scheduler] Error refreshing {city}: {e}")

def periodic_refresh_job():
    """Refreshes primary cities every 20 minutes."""
    print("[Scheduler] Running periodic AQI refresh job...")
    for city in ["kanpur", "delhi", "mumbai", "bengaluru", "lucknow"]:
        refresh_city_data(city)

def seed_initial_history_if_empty():
    """
    Seeds database with historical records on initial startup
    using the Kanpur dataset or simulated historical records.
    """
    db = SessionLocal()
    try:
        count = db.query(AQIHistoryRecord).count()
        if count > 50:
            print(f"[Database] History table already seeded with {count} records.")
            return

        print("[Database] Seeding historical records into SQLite database...")
        records = []
        now = datetime.datetime.utcnow()

        # Try reading kanpur_clean_wide.csv
        csv_path = settings.ML_DATA_PATH
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                df["datetime"] = pd.to_datetime(df["datetime"])
                # Sample 400 points evenly across time
                sample_df = df.iloc[::max(1, len(df) // 400)].tail(400)
                for _, row in sample_df.iterrows():
                    pm25 = float(row.get("pm25", 60.0))
                    records.append(
                        AQIHistoryRecord(
                            city="Kanpur",
                            timestamp=row["datetime"].to_pydatetime().replace(tzinfo=None),
                            aqi=pm25_to_aqi(pm25),
                            pm25=pm25,
                            pm10=float(row.get("pm10", pm25 * 1.6)),
                            co=float(row.get("co", 0.9)),
                            no=float(row.get("no", 2.5)),
                            no2=float(row.get("no2", 18.5)),
                            so2=float(row.get("so2", 24.0)),
                            o3=float(row.get("o3", 13.0)),
                            temperature=float(row.get("temperature", 26.0)),
                            humidity=float(row.get("relativehumidity", 65.0)),
                            source="CPCB Station"
                        )
                    )
            except Exception as e:
                print(f"[Database] Error reading seed CSV: {e}")

        # Seed synthetic history for other major cities (last 90 days)
        for city_name, base_info in [("Delhi", 110.0), ("Mumbai", 48.0), ("Bengaluru", 32.0)]:
            for day in range(90, 0, -1):
                ts = now - datetime.timedelta(days=day, hours=12)
                p25 = max(10.0, base_info + (day % 14 - 7) * 2.5)
                records.append(
                    AQIHistoryRecord(
                        city=city_name,
                        timestamp=ts,
                        aqi=pm25_to_aqi(p25),
                        pm25=p25,
                        pm10=p25 * 1.5,
                        temperature=28.0,
                        humidity=60.0,
                        source="Station Historical"
                    )
                )

        if records:
            db.bulk_save_objects(records)
            db.commit()
            print(f"[Database] Successfully seeded {len(records)} history records.")
    finally:
        db.close()

scheduler = BackgroundScheduler()

def start_scheduler():
    seed_initial_history_if_empty()
    # Initial quick cache fill for popular cities
    for city in ["kanpur", "delhi", "mumbai", "bengaluru", "lucknow"]:
        try:
            LATEST_AQI_CACHE[city] = AQIFetcherService.fetch_current_aqi(city)
        except Exception:
            pass

    scheduler.add_job(periodic_refresh_job, "interval", minutes=20, id="aqi_refresh_job", replace_existing=True)
    scheduler.start()
    print("[Scheduler] APScheduler background service started (interval: 20 min).")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] APScheduler stopped.")
