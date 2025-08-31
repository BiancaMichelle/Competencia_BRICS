#!/bin/bash
# Build script for Vercel deployment

echo "🚀 Starting build process for Django app..."

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Run migrations (optional, depending on your setup)
# python manage.py migrate --noinput

echo "✅ Build completed successfully!"
