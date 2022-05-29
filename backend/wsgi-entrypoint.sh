#!/bin/sh

until cd /app/
do
    echo "Ожидание готовности django-сервера..."
done

until ./manage.py migrate
do
    echo "Ожидание готовности базы данных..."
done

./manage.py collectstatic --noinput
gunicorn foodgram.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4