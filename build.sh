#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load fixtures if they exist
if [ -f "mercadocesar/fixtures/admin_user.json" ]; then
    python manage.py loaddata mercadocesar/fixtures/admin_user.json
else
    echo "No admin_user.json fixture found, skipping..."
fi