#!/usr/bin/with-contenv bashio

# Kloonime repo /app
REPO=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

echo "Removing old app..."
rm -rf /app/*

echo "Cloning private repo..."
git clone --depth 1 https://$TOKEN@github.com/$REPO /app

echo "Installing dependencies..."
cd /app
npm install --omit=dev

# Node foreground (PID 1)
node index.js