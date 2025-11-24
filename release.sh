#!/bin/bash
# Release script for Heroku
# This script runs database migrations and collects static files

set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Release complete!"

