# ==========================================
# Stage 1: Build React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /build

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy source and build static assets
COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python FastAPI + ML Backend
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (build tools for scientific packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install backend Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application and ML assets
COPY backend/ ./backend/

# Copy built frontend assets from Stage 1 into the frontend dist location
COPY --from=frontend-builder /build/dist ./frontend/dist

# Expose single full-stack port
EXPOSE 8000

WORKDIR /app/backend

# Run the unified FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
