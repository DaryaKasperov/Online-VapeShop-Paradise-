#!/bin/bash
echo "🚀 Starting build process..."
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear -v 2
echo "🗄️ Running migrations..."
python manage.py migrate --noinput
echo "✅ Build completed!"