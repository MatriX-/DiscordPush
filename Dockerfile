# Build stage for React frontend
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build stage for Python backend
FROM python:3.9-slim
WORKDIR /app

# Copy frontend build
COPY --from=frontend-build /app/frontend/build /app/frontend/build

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy environment variables template
COPY .env.template .env

# Expose port
EXPOSE 7777

# Start the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7777"] 