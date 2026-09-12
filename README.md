# Vayu Suchak
### AQI Prediction & Health Advisory System

Vayu Suchak is a full-stack, publicly accessible, no-login web application engineered for real-time air quality monitoring, autoregressive machine learning particulate forecasting, and AI-powered respiratory health advisories.

---

## Architecture Overview

```
vayu-suchak/
├── backend/                        # FastAPI Python Backend
│   ├── main.py                     # App entry point, CORS, Rate Limiting, Lifespan
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Configuration template
│   ├── core/
│   │   ├── config.py               # Pydantic Settings & key redaction
│   │   ├── rate_limiter.py         # SlowAPI IP-based rate limiting
│   │   └── security.py             # Future-proof auth hooks (Depends)
│   ├── models/
│   │   ├── database.py             # SQLAlchemy engine & SQLite session
│   │   └── aqi_record.py           # AQIHistoryRecord, AIChatLog, SavedLocation
│   ├── schemas/                    # Pydantic validation models
│   ├── services/
│   │   ├── aqi_fetcher.py          # Real-time telemetry (WAQI, OpenAQ & calibrated stations)
│   │   ├── scheduler.py            # APScheduler background refresh (20 min interval)
│   │   └── llm_service.py          # AI Health Chat (Gemini / OpenAI + rule engine fallback)
│   ├── ml/
│   │   ├── aqi_model.pkl           # Trained Random Forest Regressor
│   │   ├── model_features.pkl      # Serialized feature column list
│   │   ├── features.py             # Lag, rolling, & cyclical feature transforms
│   │   ├── model.py                # Model loader & autoregressive multi-step predictor
│   │   └── train.py                # Offline training & evaluation script
│   └── routers/
│       ├── aqi.py                  # Current, Forecast, History, Pollutants endpoints
│       ├── advisory.py             # Rule-based health advisory
│       ├── ai_chat.py              # AI Health Assistant chat
│       ├── locations.py            # Debounced city search
│       └── auth.py                 # Placeholder router for future login
│
├── frontend/                       # React 18 + Vite Frontend
│   ├── src/
│   │   ├── components/             # Reusable Card, Badges, Charts, Chat, Search
│   │   ├── context/                # AppContext, Client-side cache per (city, range)
│   │   ├── services/               # Clean API client
│   │   ├── App.jsx                 # Top-level view routing
│   │   └── index.css               # Tailwind CSS styles & typography
│   ├── vite.config.js              # Vite server & API proxy
│   └── tailwind.config.js          # Theme colors & AQI severity palette
│
├── Dockerfile                      # Multi-stage Docker build for single-container serving
├── docker-compose.yml              # Single command one-terminal full-stack deployment
├── .dockerignore                   # Exclude heavy & local files from Docker context
├── .gitignore                      # GitHub gitignore preventing secret/node_modules upload
└── README.md
```

---

## 1. Quick Start: Single-Terminal Docker (Recommended)

To run the complete application (Frontend + Backend + ML models) using **a single terminal command**:

```bash
docker compose up --build
```

- Complete Full-Stack Web App: `http://localhost:8000`
- Interactive API Documentation: `http://localhost:8000/docs`

---

## 2. Local Setup Guide (Without Docker)

You can also run locally either via a unified server or separate dev servers:

### Option A: Unified Full-Stack Server (Single Terminal)
Once frontend assets are compiled, FastAPI will automatically serve both the React UI and API from a single server:
```bash
# 1. Build the React UI once:
cd frontend
npm run build
cd ..

# 2. Start the unified backend:
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` to access the full-stack app.

### Option B: Separate Development Servers (Two Terminals)

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your `.env` file:
   Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # Linux / Mac
   ```

5. Start the FastAPI server:
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend will be available at: `http://localhost:8000`
   Interactive API documentation (Swagger): `http://localhost:8000/docs`

---

### Step 2: Frontend Setup

1. Open a second terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend application will be live at: `http://localhost:5173`

---

## 2. Environment Variables & API Keys

All third-party credentials **reside exclusively on the backend server**. The frontend **never** holds, transmits, or accesses external API keys.

In `backend/.env`:

```env
# World Air Quality Index (WAQI) token: https://aqicn.org/data-platform/token/
WAQI_API_KEY=your_waqi_api_token_here

# OpenAQ API Key: https://openaq.org/
OPENAQ_API_KEY=your_openaq_api_key_here

# AI Health Assistant Provider (Google Gemini or OpenAI)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# SQLite (Default) or PostgreSQL for production
DATABASE_URL=sqlite:///./vayu_suchak.db
```

> **Note on Fallbacks**: If you run without API keys, Vayu Suchak automatically activates high-precision calibrated CAAQMS station telemetry for Indian cities and an expert medical-standard rule engine for the AI Assistant. Everything functions immediately out-of-the-box!

---

## 3. Machine Learning Model & Retraining

### Feature Pipeline
The predictive model uses 15 domain-engineered features:
- **Pollutants**: `co`, `no`, `no2`, `o3`, `pm10`, `so2`
- **Meteorology**: `temperature`, `relativehumidity`
- **Time Signatures**: `hour`, `day_of_week`, `month`, `is_weekend`
- **Atmospheric Memory**:
  - `pm25_lag_1h` (1-hour lag)
  - `pm25_lag_24h` (24-hour diurnal cycle lag)
  - `pm25_rolling_6h` (6-hour moving average)

### Retraining the Model
To re-run the offline evaluation and update `aqi_model.pkl`:

```bash
cd backend
python ml/train.py
```
This script:
1. Loads historical station data from `ml/data/kanpur_clean_wide.csv`.
2. Evaluates Ridge Regression, HistGradientBoosting, and Random Forest using a chronological 80/20 train/test split.
3. Reports MAE, RMSE, and $R^2$ scores.
4. Serializes the best-performing model to `backend/ml/aqi_model.pkl` and updates `backend/ml/model_features.pkl`.

---

## 4. API Endpoints Reference

All endpoints are rate-limited by client IP address using `slowapi`:

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| `GET` | `/api/aqi/current?city=Kanpur` | 60/min | Current AQI, PM2.5, weather & individual pollutants |
| `GET` | `/api/aqi/forecast?city=Kanpur&hours=24` | 30/min | ML multi-step forecast (6h, 12h, 24h, 7d) with confidence bounds |
| `GET` | `/api/aqi/history?city=Kanpur&range=7d` | 60/min | Historical trend series (7d, 30d, 3m, 1y) from SQLite |
| `GET` | `/api/pollutants?city=Kanpur` | 60/min | Granular breakdown of PM2.5, PM10, CO, NO₂, SO₂, O₃ |
| `GET` | `/api/health-advisory?aqi=145` | 60/min | Rule-based medical advice (mask, outdoor, exercise) |
| `POST` | `/api/ai/chat` | 10/min, 100/day | LLM-powered interactive pulmonology & health advisor |
| `GET` | `/api/locations/search?q=kan` | 60/min | Debounced monitoring station & city search |
| `GET` | `/api/auth/status` | 60/min | Placeholder endpoint documenting future auth hooks |

---

## 5. Designed for Future Authentication

While v1 is completely open and requires no user accounts:
- Database tables (`AQIHistoryRecord`, `AIChatLog`, `SavedLocation`) include a nullable `user_id` column.
- FastAPI routes leverage `Depends(get_current_user_optional)` in `backend/core/security.py`.
- The frontend encapsulates preferences and location in `AppContext` (currently backed by `localStorage`), enabling seamless transition to user profiles in the future without route redesigns.

---

## 6. Official AQI Severity Scale

| AQI Range | Category | Color Hex | Health Advisory Summary |
|---|---|---|---|
| **0 – 50** | Good | `#22C55E` | Satisfactory; safe for all outdoor cardio and sports. |
| **51 – 100** | Moderate | `#EAB308` | Acceptable; sensitive individuals take occasional rest. |
| **101 – 150** | Sensitive | `#F97316` | Asthmatics, elderly, and children limit prolonged exertion. |
| **151 – 200** | Unhealthy | `#EF4444` | Wear N95 respirator outdoors; avoid outdoor running. |
| **201 – 300** | Very Unhealthy | `#A855F7` | Health alert; restrict all non-essential outdoor travel. |
| **301 – 500** | Hazardous | `#7F1D1D` | Emergency conditions; stay indoors with HEPA air filtration. |

---

## 7. Uploading to GitHub

The project includes a root `.gitignore` configured to keep your repository clean and safe from accidental leaks (`.env`, `node_modules`, and local SQLite databases are automatically excluded).

To push the project to GitHub:

```bash
cd C:\Users\piyus\.gemini\antigravity\scratch\vayu-suchak

# 1. Initialize git
git init

# 2. Stage files
git add .

# 3. Commit
git commit -m "feat: Vayu Suchak full-stack AQI prediction & health advisory system"

# 4. Set main branch and remote
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 5. Push to GitHub
git push -u origin main
```
