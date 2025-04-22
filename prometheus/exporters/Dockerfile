FROM python:3.11-slim

WORKDIR /app

# Install dependencies for both exporters
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy exporter scripts
COPY aws_cost_exporter.py .
COPY openai_usage_exporter.py .

# Default command (can be overridden in docker-compose)
CMD ["python", "aws_cost_exporter.py"]