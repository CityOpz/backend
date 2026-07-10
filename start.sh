#!/bin/sh
set -e

python manage.py migrate
python manage.py seed_admin

gunicorn cityops.wsgi:application --bind 0.0.0.0:${PORT:-10000}
