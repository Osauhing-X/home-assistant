# run.sh
#!/usr/bin/with-contenv bashio

echo "Starting Flask on 0.0.0.0:5000"

python3 -m venv /venv
. /venv/bin/activate
pip install --no-cache-dir flask

cd /data/www

# Test simple server
python -m flask run --host=0.0.0.0 --port=5000
