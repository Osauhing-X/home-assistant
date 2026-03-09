#!/usr/bin/with-contenv bashio
set -e

# Kloonime repo /app
REPO=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

rm -rf /app/*
git clone --depth 1 https://$TOKEN@github.com/$REPO /app

cd /app
npm install --omit=dev

# Node foreground PID 1
node index.js