#!/usr/bin/with-contenv bashio

echo "Starting Flask web server..."

# Set Flask app environment
export FLASK_APP=/data/www/app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

# Run Flask
python3 -m flask run
