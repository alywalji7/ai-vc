FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy exporter scripts
COPY *.py ./

# Create non-root user
RUN addgroup --system --gid 1001 exporter && \
    adduser --system --uid 1001 --gid 1001 exporter
USER exporter

# Default command - will be overridden by docker-compose
CMD ["python", "aws_cost_exporter.py"]