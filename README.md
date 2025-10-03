# Amnezia VPN Admin Telegram Bot

Automated Telegram bot for creating AmneziaVPN client configurations with pincode authentication.

## Architecture

The project follows a clean, layered architecture:

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
│  - WireGuard Integration                    │
│  - Configuration Generation                 │
└─────────────────────────────────────────────┘
```

## Project Structure

```
amnezia-vpn-admin-bot/
├── src/
│   ├── presentation/
│   │   └── telegram_bot.py         # Telegram bot handlers and UI
│   ├── business/
│   │   ├── pincode_manager.py      # Pincode generation and validation
│   │   ├── wireguard_manager.py    # WireGuard/SSH operations
│   │   └── config_generator.py     # Configuration and QR code generation
│   ├── service/
│   │   └── vpn_service.py          # Main service layer
│   └── config_loader.py            # Configuration loader
├── scripts/
│   ├── deploy.sh                   # Local deployment
│   ├── deploy-to-server.sh         # Remote deployment
│   └── test_pincode.py             # Pincode tester
├── config/
│   └── credentials.properties      # Server credentials
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container definition
└── README.md                       # This file
```

## Features

- **Layered Architecture**: Clean separation of concerns
- **Pincode Protection**: Dynamic 6-digit pincode based on current date/time
- **Automated Client Creation**: Generates WireGuard keys and configurations
- **QR Code Generation**: Instant QR codes for mobile setup
- **Configuration Files**: Downloads .conf files for desktop clients
- **IP Management**: Automatic IP address assignment
- **Username Tracking**: Client names with timestamps

## Installation

### Prerequisites

- Docker installed on VPN server
- AmneziaVPN already deployed
- Telegram Bot Token
- Python 3.11+ (for local development)

### Setup

1. **Clone Repository**
```bash
git clone <repo-url>
cd amnezia-vpn-admin-bot
```

2. **Configure Credentials**

Edit `config/credentials.properties`:
```properties
bot.token=YOUR_BOT_TOKEN
server.ip=YOUR_SERVER_IP
server.user=root
server.password=YOUR_SERVER_PASSWORD
```

3. **Deploy to Server**

```bash
./scripts/deploy-to-server.sh
```

### Local Development

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```

## Usage

### For End Users

1. Open Telegram bot
2. Send `/start`
3. Get current pincode from admin
4. Enter 6-digit pincode
5. Receive configuration file and QR code
6. Import to AmneziaWG app

### For Administrators

**Check Current Pincode:**
```bash
python3 scripts/test_pincode.py
```

**View Bot Logs:**
```bash
ssh root@YOUR_SERVER 'docker logs -f amnezia-vpn-bot'
```

**Deploy Updates:**
```bash
./scripts/deploy-to-server.sh
```

## Code Organization

### Presentation Layer (`src/presentation/`)

Handles all Telegram bot interactions:
- Command handlers (`/start`)
- Message handlers (pincode validation)
- User feedback and error messages
- File and QR code delivery

### Business Logic Layer (`src/business/`)

Core business logic components:

**PincodeManager:**
- Generates time-based pincodes
- Validates user input
- Provides current pincode information

**WireGuardManager:**
- SSH connection to VPN server
- WireGuard operations (peer management)
- IP address allocation
- Key generation

**ConfigGenerator:**
- Client configuration file generation
- QR code creation
- Configuration formatting

### Service Layer (`src/service/`)

Aggregates business logic and provides clean API:

**VPNService:**
- Coordinates all business operations
- Provides high-level methods for presentation layer
- Manages dependencies between components
- Error handling and orchestration

## Pincode Algorithm

```
Current: Day 03, Month 10, Hour 23
String: "031023"
Transform: Each digit +1 (except 9)
Result: "142134"
```

## Configuration Details

### AmneziaWG Parameters

The bot preserves server obfuscation settings:
- `Jc`, `Jmin`, `Jmax`: Junk packet parameters
- `S1`, `S2`: Packet size randomization
- `H1-H4`: Header modification values

### Network Setup

- **Server Network**: 10.8.1.0/24
- **Server IP**: 10.8.1.0
- **Client IPs**: 10.8.1.1 - 10.8.1.254
- **DNS**: 8.8.8.8

## Development

### Adding New Features

1. **Business Logic**: Add to appropriate manager in `src/business/`
2. **Service Layer**: Expose through `VPNService` in `src/service/`
3. **Presentation**: Use service methods in `TelegramBot`

### Testing

```bash
python3 -m py_compile main.py src/**/*.py
python3 scripts/test_pincode.py
```

## Troubleshooting

### Bot Not Responding

```bash
docker logs amnezia-vpn-bot
docker restart amnezia-vpn-bot
```

### Import Errors

Ensure you're running from project root:
```bash
cd /path/to/amnezia-vpn-admin-bot
python main.py
```

### Configuration Not Found

Check file location:
```bash
ls -la config/credentials.properties
```

## Security

- **Pincode**: Changes every hour
- **SSH**: Password-based (consider using keys)
- **Keys**: Unique per client
- **Preshared Key**: Additional encryption layer

## Contributing

Follow the layered architecture:
1. Keep presentation logic in `presentation/`
2. Keep business logic in `business/`
3. Expose functionality through `service/`
4. Update tests and documentation

## License

MIT
