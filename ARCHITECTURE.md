# Architecture Documentation

## Overview

The Amnezia VPN Admin Bot follows a **three-tier layered architecture** with clear separation of concerns:

1. **Presentation Layer** - User interface (Telegram)
2. **Service Layer** - Business logic aggregation
3. **Business Logic Layer** - Core functionality

## Layer Breakdown

### 1. Presentation Layer

**Location:** `src/presentation/telegram_bot.py`

**Responsibility:**
- Handle Telegram bot commands and messages
- Manage user interaction flow
- Format and send responses
- Handle file uploads and QR codes

**Key Components:**
- `TelegramBot` class
  - `start_command()` - /start handler
  - `handle_message()` - Message router
  - `_handle_pincode()` - Pincode validation flow
  - `_create_vpn_config()` - Configuration creation flow

**Dependencies:**
- `VPNService` (service layer)
- `telegram` library

**Design Principles:**
- No business logic
- Simple input/output handling
- User-friendly error messages
- Async/await for Telegram API

### 2. Service Layer

**Location:** `src/service/vpn_service.py`

**Responsibility:**
- Aggregate business logic components
- Provide clean API for presentation layer
- Coordinate operations across business modules
- Handle high-level errors

**Key Components:**
- `VPNService` class
  - `validate_pincode()` - Validate user pincode
  - `create_vpn_client()` - Create complete VPN configuration
  - `get_current_pincode_info()` - Get pincode details
  - `get_active_peers()` - List active connections

**Dependencies:**
- `PincodeManager` (business layer)
- `WireGuardManager` (business layer)
- `ConfigGenerator` (business layer)

**Design Principles:**
- Facade pattern
- Single point of entry for business operations
- Orchestrates business logic
- Returns complete result objects

### 3. Business Logic Layer

**Location:** `src/business/`

**Responsibility:**
- Implement core business rules
- Handle specific technical operations
- No knowledge of presentation layer

#### 3.1 PincodeManager

**File:** `pincode_manager.py`

**Responsibility:**
- Generate time-based pincodes
- Validate pincodes
- Provide pincode information

**Methods:**
- `generate_pincode()` - Generate current pincode
- `validate_pincode(pincode)` - Check if pincode is valid
- `get_current_info()` - Get detailed info about current pincode

**Algorithm:**
```
Day (03) + Month (10) + Hour (23) = "031023"
Transform each digit: digit + 1 (except 9)
Result: "142134"
```

#### 3.2 WireGuardManager

**File:** `wireguard_manager.py`

**Responsibility:**
- SSH connection to VPN server
- WireGuard operations
- IP address management
- Cryptographic key generation

**Methods:**
- `ssh_exec(command)` - Execute SSH command
- `get_next_available_ip()` - Find free IP address
- `generate_keypair()` - Create WireGuard keys
- `get_server_info()` - Retrieve server configuration
- `add_peer(...)` - Add new peer to server
- `get_active_peers()` - List active connections

**Technical Details:**
- Uses `sshpass` for SSH authentication
- Executes commands in Docker container
- Parses WireGuard configuration files
- Manages IP allocation (10.8.1.1-254)

#### 3.3 ConfigGenerator

**File:** `config_generator.py`

**Responsibility:**
- Generate client configuration files
- Create QR codes
- Format configuration output

**Methods:**
- `generate_client_config(...)` - Create .conf file
- `create_qr_code(config)` - Generate QR code PNG
- `generate_config_filename(username)` - Create filename

**Configuration Format:**
```ini
[Interface]
PrivateKey = ...
Address = ...
DNS = ...
Jc/Jmin/Jmax/S1/S2/H1-H4 = ...

[Peer]
PublicKey = ...
PresharedKey = ...
AllowedIPs = ...
Endpoint = ...
PersistentKeepalive = ...
```

## Data Flow

### Creating VPN Configuration

```
User Input (Pincode)
    ↓
[Presentation] telegram_bot.handle_message()
    ↓
[Presentation] telegram_bot._handle_pincode()
    ↓
[Service] vpn_service.validate_pincode()
    ↓
[Business] pincode_manager.validate_pincode()
    ↓
[Service] vpn_service.create_vpn_client()
    ↓
[Business] wireguard_manager.get_next_available_ip()
    ↓
[Business] wireguard_manager.generate_keypair()
    ↓
[Business] wireguard_manager.get_server_info()
    ↓
[Business] wireguard_manager.add_peer()
    ↓
[Business] config_generator.generate_client_config()
    ↓
[Business] config_generator.create_qr_code()
    ↓
[Service] Returns complete result
    ↓
[Presentation] Send files to user
```

## Dependency Injection

### Configuration Loading

**File:** `src/config_loader.py`

Loads configuration from `config/credentials.properties`:
```python
config = {
    'bot.token': '...',
    'server.ip': '...',
    'server.user': '...',
    'server.password': '...'
}
```

### Initialization Flow

**File:** `main.py`

```python
1. Load configuration
2. Create VPNService (with config)
   ├─ Create PincodeManager
   ├─ Create WireGuardManager (with config)
   └─ Create ConfigGenerator (with config)
3. Create TelegramBot (with token and vpn_service)
4. Start bot
```

## Error Handling

### Presentation Layer
- Catches all exceptions
- Shows user-friendly error messages
- Logs errors for debugging

### Service Layer
- Validates inputs
- Propagates business errors
- Adds context to errors

### Business Layer
- Raises specific exceptions
- Validates operations
- Returns detailed error info

## Testing Strategy

### Unit Tests
- Test each business component independently
- Mock SSH operations
- Test pincode algorithm

### Integration Tests
- Test service layer orchestration
- Test with mock Telegram updates
- Test configuration generation

### Manual Tests
```bash
python scripts/test_pincode.py
```

## Extension Points

### Adding New Features

1. **New Business Logic:**
   - Add new manager to `src/business/`
   - Implement specific functionality
   - Keep it independent

2. **Expose in Service:**
   - Add method to `VPNService`
   - Coordinate new business logic
   - Return complete results

3. **Add UI:**
   - Add handler to `TelegramBot`
   - Call service methods
   - Format response

### Example: Adding Client Removal

```python
# Business Layer
class WireGuardManager:
    def remove_peer(self, public_key):
        # Implementation

# Service Layer
class VPNService:
    def remove_vpn_client(self, public_key):
        return self.wireguard_manager.remove_peer(public_key)

# Presentation Layer
class TelegramBot:
    async def remove_command(self, update, context):
        # Get public_key from user
        result = self.vpn_service.remove_vpn_client(public_key)
        # Send confirmation
```

## Design Patterns Used

1. **Layered Architecture** - Separation of concerns
2. **Facade Pattern** - VPNService as single entry point
3. **Dependency Injection** - Config passed to components
4. **Factory Pattern** - Key and config generation
5. **Strategy Pattern** - Pincode algorithm

## Benefits of This Architecture

1. **Maintainability** - Easy to find and modify code
2. **Testability** - Each layer can be tested independently
3. **Extensibility** - Easy to add new features
4. **Separation of Concerns** - Each component has single responsibility
5. **Reusability** - Business logic can be used elsewhere
6. **Clarity** - Clear flow of data and dependencies

## Technology Stack

- **Language:** Python 3.11
- **Bot Framework:** python-telegram-bot
- **QR Codes:** qrcode + Pillow
- **SSH:** sshpass
- **VPN:** AmneziaWG (WireGuard fork)
- **Deployment:** Docker

## Security Considerations

1. **Configuration** - Sensitive data in config file (not in code)
2. **SSH** - Password-based (consider key-based)
3. **Pincode** - Time-based (changes hourly)
4. **Keys** - Generated uniquely per client
5. **Preshared Key** - Additional WireGuard encryption

## Performance Considerations

1. **SSH Operations** - Blocking, consider async in future
2. **QR Generation** - Memory-efficient BytesIO
3. **Configuration Parsing** - Cached server info
4. **IP Allocation** - Simple linear search (adequate for <254 clients)
