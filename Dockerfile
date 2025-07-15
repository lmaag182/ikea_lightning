# Use a slim Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the script and any necessary files
COPY mqtt_logger.py .

# Install dependencies
RUN pip install --no-cache-dir paho-mqtt

# Run the script
CMD ["python", "mqtt_logger.py"] 