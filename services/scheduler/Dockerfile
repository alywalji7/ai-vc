FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Expose ports
EXPOSE 8000  # API
EXPOSE 5555  # Flower
EXPOSE 9090  # Prometheus metrics

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Command to run the service
CMD ["python", "main.py"]