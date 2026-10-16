#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Setting up Silent Verification Python environment..."

if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d "venv" ]; then
        echo "==> Creating virtual environment (venv)..."
        python3 -m venv venv || python -m venv venv
    fi
    echo "==> Activating virtual environment..."
    source venv/bin/activate
fi

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Applying database migrations..."
python manage.py migrate

echo "==> Collecting static assets..."
python manage.py collectstatic --noinput

echo "==> Silent Verification Build completed successfully!"
