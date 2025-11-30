#!/bin/bash

# Author: Abolfazl
# Version: v1.0.0
# Date: 5/16/25
# Description: entrypoint for PetShop API.
# Usage: ./entrypoint.sh

set e

export DJANGO_SETTINGS_MODULE=core.settings.production
echo "Using Django settings: $DJANGO_SETTINGS_MODULE"

echo "Applying database migrations..."
python3 manage.py migrate

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
echo "Redis URL: $REDIS_LOCATION"
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers $(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 )) \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -
