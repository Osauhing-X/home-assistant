#!/usr/bin/with-contenv bashio

USERNAME=$(bashio::config 'github_username')
TOKEN=$(bashio::config 'github_token')
REPO=$(bashio::config 'repo')

echo "Downloading server repo..."

rm -rf /app/server

git clone --depth 1 https://$TOKEN@github.com/$USERNAME/$REPO.git /app/server

echo "Installing dependencies..."

cd /app/server
npm install --omit=dev

echo "Starting Node server..."

node index.js