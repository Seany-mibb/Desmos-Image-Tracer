# Use a Python base image
FROM python:3.11-slim

# Install system dependencies including potrace
RUN apt-get update && \
    apt-get install -y potrace gcc libxml2-dev libxslt-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Render expects
EXPOSE 10000

# Use Render's $PORT env variable
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
