# Amnezia VPN Admin Telegram Bot

Automated Telegram bot for creating AmneziaVPN client configurations using **REST API** with pincode authentication.

## Architecture

The bot uses a clean, layered architecture with **REST API integration**:

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                  │
│      (Telegram Bot Interface)               │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│           Service Layer                     │
│    (Business Logic Aggregation)             │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         Business Logic Layer                │
│  - Pincode Management                       │
│  - REST API Client                          │
│  - QR Code Generation                       │
└──────────────┬──────────────────────────────┘
               │
               │ HTTP REST API
               ▼
┌─────────────────────────────────────────────┐
│         Amnezia WG Easy                     │
│  (WireGuard + Web UI + REST API)            │
└─────────────────────────────────────────────┘
```

## Key Features

- **REST API Integration** - No SSH required
- **Web UI** - Manage clients via browser
- **Layered Architecture** - Clean separation of concerns
- **Pincode Protection** - Dynamic 6-digit pincode
- **Automated Client Creation** - Generate keys and configs
- **QR Code Generation** - Instant mobile setup
- **Multiple Output Formats** - .conf files and QR codes

## Prerequisites

- Docker installed on VPN server
- **Amnezia WG Easy** container running (not standard Amnezia container)
- Telegram Bot Token
- Python 3.11+ (for local development)

## Quick Start

### 1. Deploy Amnezia WG Easy

If you're migrating from standard Amnezia container, see [MIGRATION_TO_API.md](MIGRATION_TO_API.md).

```bash
docker run -d \
  --name=amnezia-wg-easy \
  -e LANG=en \
  -e WG_HOST=YOUR_SERVER_IP \
  -e PASSWORD=YOUR_ADMIN_PASSWORD \
  -e PORT=51821 \
  -e WG_PORT=42619 \
  -v ~/.amnezia-wg-easy:/etc/wireguard \
  -p 42619:42619/udp \
  -p 51821:51821/tcp \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --sysctl="net.ipv4.ip_forward=1" \
  --device=/dev/net/tun:/dev/net/tun \
  --restart unless-stopped \
  ghcr.io/w0rng/amnezia-wg-easy
```

### 2. Configure Bot

Edit `config/credentials.properties`:

```properties
bot.token=YOUR_TELEGRAM_BOT_TOKEN
api.url=http://YOUR_SERVER_IP:51821
api.password=YOUR_WEB_UI_PASSWORD
```

### 3. Test API Connection

```bash
python3 scripts/test_api.py
```

### 4. Deploy Bot

```bash
./scripts/deploy-to-server.sh
```

### 5. Use Bot

1. Get current pincode: `python3 scripts/test_pincode.py`
2. Open Telegram bot
3. Send `/start`
4. Enter pincode
5. Receive configuration

## Project Structure

```
amnezia-vpn-admin-bot/
├── src/
│   ├── presentation/              # Telegram bot UI
│   │   └── telegram_bot.py
│   ├── business/                  # Core business logic
│   │   ├── pincode_manager.py     # Pincode generation
│   │   ├── amnezia_api_client.py  # Low-level API client
│   │   ├── wireguard_api_manager.py # High-level manager
│   │   └── qr_generator.py        # QR code creation
│   ├── service/                   # Service orchestration
│   │   └── vpn_service.py
│   └── config_loader.py
├── scripts/                       # Utility scripts
│   ├── deploy.sh
│   ├── deploy-to-server.sh
│   ├── test_pincode.py
│   └── test_api.py               # API connection test
├── config/
│   └── credentials.properties
├── main.py                        # Entry point
└── requirements.txt
```

## API Endpoints Used

The bot uses these REST API endpoints:

```
GET  /api/wireguard/client                    # List clients
POST /api/wireguard/client                    # Create client
GET  /api/wireguard/client/{id}/configuration # Get config
GET  /api/wireguard/client/{id}/qrcode.svg   # Get QR code
DELETE /api/wireguard/client/{id}             # Delete client
POST /api/wireguard/client/{id}/enable        # Enable client
POST /api/wireguard/client/{id}/disable       # Disable client
```

## Advantages Over SSH Approach

### Before (SSH-based)
```python
ssh_exec("docker exec amnezia-awg wg genkey")
ssh_exec("docker exec amnezia-awg wg set wg0 peer ...")
```

**Issues:**
- Requires SSH access
- Complex shell command parsing
- SSH password in config
- Requires sshpass
- Error handling difficult

### After (API-based)
```python
client = api_client.create_client(name)
config = api_client.get_client_config(client_id)
```

**Benefits:**
✅ No SSH required
✅ Clean HTTP responses
✅ Standard error handling
✅ Web UI included
✅ Better security
✅ Easier debugging

## Web UI Access

Access the web interface at: `http://YOUR_SERVER_IP:51821`

- Username: `admin`
- Password: `YOUR_WEB_UI_PASSWORD`

Features:
- Visual client management
- Real-time statistics
- Traffic monitoring
- QR code generation
- Config downloads

## Pincode Algorithm

```
Current: Day 03, Month 10, Hour 23
String: "031023"
Transform: Each digit +1 (except 9)
Result: "142134"
```

Changes every hour for security.

## Development

### Local Testing

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# Test pincode
python3 scripts/test_pincode.py

# Test API
python3 scripts/test_api.py

# Run bot
python main.py
```

### Adding Features

Follow the layered architecture:

1. **API Client** (`amnezia_api_client.py`) - Add API method
2. **Manager** (`wireguard_api_manager.py`) - Add business logic
3. **Service** (`vpn_service.py`) - Expose functionality
4. **Presentation** (`telegram_bot.py`) - Add UI handler

## Troubleshooting

### API Connection Failed

```bash
# Check if web UI is accessible
curl http://YOUR_SERVER_IP:51821

# Test API authentication
curl -u admin:PASSWORD http://YOUR_SERVER_IP:51821/api/session

# Check container
docker ps | grep amnezia-wg-easy
docker logs amnezia-wg-easy
```

### Bot Not Responding

```bash
docker logs amnezia-vpn-bot
docker restart amnezia-vpn-bot
```

### Wrong Pincode

```bash
python3 scripts/test_pincode.py
```

## Migration from Old Setup

If you're using the old SSH-based container, see detailed migration guide:

📖 [MIGRATION_TO_API.md](MIGRATION_TO_API.md)

Summary:
1. Backup current setup
2. Deploy amnezia-wg-easy
3. Update config file
4. Deploy bot
5. Test

## Security

### Securing Web UI

Use reverse proxy with HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name vpn.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:51821;
    }
}
```

### Best Practices

- ✅ Use strong web UI password
- ✅ Enable HTTPS for web UI
- ✅ Restrict web UI access by IP
- ✅ Regular backups
- ✅ Monitor logs
- ✅ Keep Docker images updated

## Documentation

- **ARCHITECTURE.md** - Technical architecture details
- **MIGRATION_TO_API.md** - Migration from SSH to API
- **QUICKSTART.md** - Quick start guide
- **PROJECT_STRUCTURE.txt** - Visual structure
- **REFACTORING_SUMMARY.md** - Refactoring history

## Support

- **Amnezia WG Easy**: https://github.com/w0rng/amnezia-wg-easy
- **WG Easy Docs**: https://wg-easy.github.io/wg-easy/latest/
- **AmneziaVPN**: https://amnezia.org

## License

MIT

## Contributing

1. Fork the repository
2. Create feature branch
3. Follow layered architecture
4. Add tests
5. Submit pull request

---

**Built with ❤️ using modern REST API architecture**
