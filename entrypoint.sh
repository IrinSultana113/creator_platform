#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
until python -c "import psycopg2; psycopg2.connect(dbname='${POSTGRES_DB:-creator_platform}', user='${POSTGRES_USER:-postgres}', password='${POSTGRES_PASSWORD:-postgres}', host='${POSTGRES_HOST:-db}', port='${POSTGRES_PORT:-5432}')" 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Waiting for Elasticsearch to start..."
until curl -s "${ELASTICSEARCH_URL:-http://elasticsearch:9200}/_cluster/health?wait_for_status=yellow&timeout=1s" > /dev/null 2>&1; do
  sleep 2
done
echo "Elasticsearch is ready."

echo "Creating migrations..."
python manage.py makemigrations authentication creators --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Loading seed data into Elasticsearch..."
python manage.py load_creators

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn creator_platform.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
