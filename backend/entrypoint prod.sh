#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waitng for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec "$@"