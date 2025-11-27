#!/bin/bash

# ============================
# Fast Demo Script: AI Learning Platform
# ============================

# Exit on error
set -e

# Step 1: Build and start Docker services in detached mode
echo "Building and starting Docker services..."
docker-compose up --build -d

# Step 2: Wait a few seconds for DBs and Redis to start
echo "Waiting for databases and Redis to initialize..."
sleep 10

# Step 3: Run migrations
echo "Running Django migrations..."
docker-compose exec web python manage.py migrate

# Step 4: Collect static files
echo "Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# Step 5: Create superuser if not exists (optional)
# Uncomment the line below to create superuser interactively
# docker-compose exec web python manage.py createsuperuser

# Step 6: Start Ngrok
echo "Starting Ngrok..."
# Make sure you have ngrok installed and authenticated
# Exposes Django default port 8000
ngrok http 8000 &
sleep 3

# Get the public URL from Ngrok API
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[0].public_url')

echo "-------------------------------------"
echo "🎉 Your platform is live!"
echo "Shareable link: $NGROK_URL"
echo "-------------------------------------"

# Tail Docker logs so you can monitor
docker-compose logs -f
