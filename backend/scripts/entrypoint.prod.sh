#!/bin/bash

set -e

echo "Starting CodeCrafts Backend in Production Mode..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create initial data if needed
echo "Setting up initial data..."
python scripts/setup_production_data.py

# Start the application
echo "Starting application..."
exec "$@"