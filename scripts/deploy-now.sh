#!/bin/bash

set -e

SERVER_IP="72.56.67.251"
SERVER_PASSWORD="pJ1BB7AiU+_tyM"

echo "Deploying to $SERVER_IP..."

echo "Creating deployment package..."
tar czf bot-deploy.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    src/ \
    config/ \
    main.py \
    requirements.txt \
    Dockerfile

echo "Uploading files..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no bot-deploy.tar.gz root@$SERVER_IP:/tmp/

echo "Deploying on server..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP << 'EOF'
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
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 5000:5000 \
  amnezia-vpn-admin-bot python main.py --mode both --api-port 5000

echo "Deployment complete!"
sleep 3
docker logs amnezia-vpn-bot
EOF

rm bot-deploy.tar.gz

echo ""
echo "✅ Bot deployed successfully to $SERVER_IP!"
echo ""
echo "Telegram bot is running"
echo "REST API available at: http://$SERVER_IP:5000"
echo ""
echo "To view logs:"
echo "  ssh root@$SERVER_IP 'docker logs -f amnezia-vpn-bot'"
echo ""
echo "To test API:"
echo "  curl http://$SERVER_IP:5000/health"
echo "  curl http://$SERVER_IP:5000/pincode/current"
