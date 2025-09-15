FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y potrace && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose Render’s default port
ENV PORT=10000
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
