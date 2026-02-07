# E1 Assistant - Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Start the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
