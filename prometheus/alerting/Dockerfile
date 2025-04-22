FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy notifier script
COPY slack_notifier.py .

# Make script executable
RUN chmod +x slack_notifier.py

# Create a non-root user to run the notifier
RUN addgroup --system --gid 1001 alerting && \
    adduser --system --uid 1001 --gid 1001 alerting
USER alerting

EXPOSE 9093

# Run the notifier
CMD ["python", "slack_notifier.py"]