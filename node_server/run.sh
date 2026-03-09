#!/usr/bin/with-contenv bashio

# Config from HA
REPO=$(bashio::config 'repo')        # username/name.git
TOKEN=$(bashio::config 'github_token')

echo "Removing old app..."
rm -rf /app/*

echo "Cloning private repo..."
git clone --depth 1 https://$TOKEN@github.com/$REPO.git /app

echo "Installing dependencies..."
cd /app
npm install --omit=dev

echo "Starting Node server..."
node index.js