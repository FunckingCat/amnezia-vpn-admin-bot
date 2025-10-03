#!/bin/bash

set -e

SERVER_IP=$(grep 'server.ip' config/credentials.properties | cut -d'=' -f2)
SERVER_USER=$(grep 'server.user' config/credentials.properties | cut -d'=' -f2)
SERVER_PASSWORD=$(grep 'server.password' config/credentials.properties | cut -d'=' -f2)

echo "Deploying to $SERVER_USER@$SERVER_IP..."

echo "Creating deployment package..."
tar czf bot-deploy.tar.gz \
    src/ \
    config/ \
    main.py \
    requirements.txt \
    Dockerfile \
    --exclude='*.pyc' \
    --exclude='__pycache__'

echo "Uploading files..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no bot-deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

echo "Deploying on server..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
cd /opt
rm -rf amnezia-vpn-bot
mkdir -p amnezia-vpn-bot
cd amnezia-vpn-bot
tar xzf /tmp/bot-deploy.tar.gz
rm /tmp/bot-deploy.tar.gz

echo "Building Docker image..."
docker build -t amnezia-vpn-admin-bot .

echo "Stopping existing container..."
docker stop amnezia-vpn-bot 2>/dev/null || true
docker rm amnezia-vpn-bot 2>/dev/null || true

echo "Starting bot container..."
docker run -d \
  --name amnezia-vpn-bot \
  --restart unless-stopped \
  amnezia-vpn-admin-bot

echo "Deployment complete!"
docker logs amnezia-vpn-bot
EOF

rm bot-deploy.tar.gz

echo ""
echo "✅ Bot deployed successfully to $SERVER_IP!"
echo ""
echo "To view logs:"
echo "  ssh $SERVER_USER@$SERVER_IP 'docker logs -f amnezia-vpn-bot'"
echo ""
echo "To stop bot:"
echo "  ssh $SERVER_USER@$SERVER_IP 'docker stop amnezia-vpn-bot'"
