#!/bin/bash

# Move to project directory
# shellcheck disable=SC2164
cd /osa_expert_admin

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

## Set keys in Django project
#echo "Set keys in Django project"
python manage.py setkeys

## Load DB data from fixture
#echo "Load DB data from fixture"
python manage.py loaddata *fixture.json

# Create superuser for Django
echo "Create superuser for Django"
echo "Username '${DJANGO_SUPERUSER_USERNAME}' | Password '${DJANGO_SUPERUSER_PASSWORD}' | mail '${DJANGO_SUPERUSER_EMAIL}'"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')" | python manage.py shell

## Download nltk dependencies
echo "Download nltk dependencies"
python3 -c "import nltk; nltk.download('punkt')"

# Start celery
echo "Starting celery"
celery -A osa_expert_admin worker -l INFO -B &

# Start server through gunicorn
echo "Starting server through gunicorn"
gunicorn --bind 0.0.0.0:8000 osa_expert_admin.wsgi:application