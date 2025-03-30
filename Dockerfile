# --- Stage 1: Build React Frontend ---
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

# Copy package.json and package-lock.json first for caching
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy the rest of the frontend code (will now ignore local node_modules)
COPY frontend/ ./

# Set API URL for production build (relative path works well here)
# This assumes your API routes are prefixed with /api in Flask
ENV REACT_APP_API_URL=/api
RUN npx react-scripts build

# --- Stage 2: Build Python Backend ---
FROM python:3.9-slim

ENV PORT 8080
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Copy requirements first for caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (app.py, helpers, etc.)
COPY backend/ .

# Copy built frontend files from the previous stage into 'frontend_build' dir
COPY --from=frontend-builder /app/frontend/build ./frontend_build

# Make sure app.py uses the correct static folder path:
# Flask(__name__, static_folder='frontend_build', static_url_path='')
# Ensure app.py serves index.html from 'frontend_build'

EXPOSE $PORT

# Run the Flask app (ensure debug=False in app.py)
# CMD ["flask", "run", "--host=0.0.0.0", "--port=$PORT"] # Comment this out

# Use Gunicorn for production
# Make sure 'app:app' matches your Flask app instance in app.py
# Use --timeout 0 for potentially long-running API calls (like to Gemini)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]