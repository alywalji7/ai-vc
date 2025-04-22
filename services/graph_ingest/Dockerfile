FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to utilize Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose ports for API and metrics
EXPOSE 8080
EXPOSE 8091

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV METRICS_PORT=8091

# Run the service
CMD ["python", "main.py"]