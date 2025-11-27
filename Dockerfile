# Start from slim Python 3.11 image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient and general builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    default-mysql-client \
    pkg-config \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and upgrade pip
COPY requirements.txt /app/
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install wheel  # Ensure wheel is installed
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files (optional for testing)
RUN python manage.py collectstatic --noinput || echo "Skipping collectstatic for now"

# Expose Django port
EXPOSE 8000

# Default command
CMD ["gunicorn", "LearningSystem.wsgi:application", "--bind", "0.0.0.0:8000"]
