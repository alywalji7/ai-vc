FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir python-dotenv

# Copy slack notifier script
COPY slack_notifier.py .

# Make the script executable
RUN chmod +x slack_notifier.py

# Set environment variables
ENV PORT=9093

# Expose the webhook port
EXPOSE 9093

# Run the slack notifier
CMD ["python", "slack_notifier.py"]