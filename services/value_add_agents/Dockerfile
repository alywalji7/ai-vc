FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY . .

# Create growth plans directory
RUN mkdir -p /app/growth_plans

# Run the service
CMD ["python", "main.py"]