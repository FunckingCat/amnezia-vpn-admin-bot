# Quick Start Guide

## 1. Test Pincode Generation

```bash
python3 scripts/test_pincode.py
```

This shows the current valid pincode.

## 2. Test Bot Locally (Optional)

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```

## 3. Deploy to Server

```bash
./scripts/deploy-to-server.sh
```

## 4. Verify Deployment

```bash
ssh root@YOUR_SERVER_IP 'docker logs amnezia-vpn-bot'
```

## 5. Get Current Pincode

```bash
python3 scripts/test_pincode.py
```

## 6. Test with Telegram

1. Open your bot in Telegram
2. Send `/start`
3. Enter the current pincode from step 5
4. Receive configuration

## Project Structure

```
src/
├── presentation/     # Telegram bot interface
├── business/         # Core business logic
│   ├── pincode_manager.py
│   ├── wireguard_manager.py
│   └── config_generator.py
├── service/          # Service layer
│   └── vpn_service.py
└── config_loader.py  # Configuration

scripts/              # Deployment and utilities
config/              # Configuration files
main.py              # Entry point
```

## Troubleshooting

### Bot doesn't start
```bash
ssh root@YOUR_SERVER 'docker logs amnezia-vpn-bot'
```

### Wrong pincode
```bash
python3 scripts/test_pincode.py
```

### Import errors
Make sure you're in the project root:
```bash
cd /path/to/amnezia-vpn-admin-bot
python main.py
```

## Monitoring

### Watch logs in real-time
```bash
ssh root@YOUR_SERVER 'docker logs -f amnezia-vpn-bot'
```

### Check running containers
```bash
ssh root@YOUR_SERVER 'docker ps'
```

### View active VPN clients
```bash
ssh root@YOUR_SERVER 'docker exec amnezia-awg wg show'
```

## Development Workflow

1. Edit code in `src/` directory
2. Test locally: `python main.py`
3. Deploy: `./scripts/deploy-to-server.sh`
4. Monitor: Check logs
