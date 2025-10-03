#!/bin/bash

set -e

echo "Building Docker image..."
docker build -t amnezia-vpn-admin-bot .

echo "Stopping existing container if running..."
docker stop amnezia-vpn-bot 2>/dev/null || true
docker rm amnezia-vpn-bot 2>/dev/null || true

echo "Starting new container..."
docker run -d \
  --name amnezia-vpn-bot \
  --restart unless-stopped \
  amnezia-vpn-admin-bot

echo "Bot deployed successfully!"
echo "Check logs with: docker logs -f amnezia-vpn-bot"
