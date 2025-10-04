# Migration to REST API

## Overview

The bot has been refactored to use **Amnezia WG Easy REST API** instead of SSH + docker exec commands.

## Why Migrate?

✅ **Better Performance** - No SSH overhead
✅ **Cleaner Code** - REST API is simpler than shell commands
✅ **More Features** - Web UI for management
✅ **Better Security** - No SSH password needed
✅ **Easier Debugging** - Standard HTTP responses

## Migration Steps

### Step 1: Backup Current Setup

```bash
# Backup current WireGuard configuration
ssh root@YOUR_SERVER 'docker exec amnezia-awg cat /opt/amnezia/awg/wg0.conf' > wg0.conf.backup

# Export all client keys
ssh root@YOUR_SERVER 'docker exec amnezia-awg wg show' > clients.backup
```

### Step 2: Stop Old Container

```bash
ssh root@YOUR_SERVER 'docker stop amnezia-awg'
ssh root@YOUR_SERVER 'docker rm amnezia-awg'
```

### Step 3: Deploy Amnezia WG Easy

Choose your preferred variant:

#### Option A: w0rng/amnezia-wg-easy (Recommended)

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

#### Option B: Xetera/amnezia-wg-easy (Cross-platform)

```bash
docker run -d \
  --name=amnezia-wg-easy \
  -e LANG=en \
  -e WG_HOST=YOUR_SERVER_IP \
  -e PASSWORD=YOUR_ADMIN_PASSWORD \
  -e WG_PORT=42619 \
  -v ~/.amnezia-wg-easy:/etc/wireguard \
  -p 42619:42619/udp \
  -p 51821:51821/tcp \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --sysctl="net.ipv4.ip_forward=1" \
  --restart unless-stopped \
  ghcr.io/deckersu/amnezia-wg-easy:latest
```

### Step 4: Update Configuration

Edit `config/credentials.properties`:

**Old format (SSH-based):**
```properties
bot.token=YOUR_BOT_TOKEN
server.ip=72.56.67.251
server.user=root
server.password=YOUR_SSH_PASSWORD
```

**New format (API-based):**
```properties
bot.token=YOUR_BOT_TOKEN
api.url=http://72.56.67.251:51821
api.password=YOUR_WEB_UI_PASSWORD
```

### Step 5: Verify Web UI Access

Open in browser: `http://YOUR_SERVER_IP:51821`

- Username: `admin`
- Password: `YOUR_ADMIN_PASSWORD`

You should see the wg-easy web interface.

### Step 6: Test API Access

```bash
curl -u admin:YOUR_PASSWORD http://YOUR_SERVER_IP:51821/api/wireguard/client
```

Should return JSON array of clients (empty at first).

### Step 7: Deploy Updated Bot

```bash
./scripts/deploy-to-server.sh
```

### Step 8: Test Bot

1. Get current pincode: `python3 scripts/test_pincode.py`
2. Open Telegram bot
3. Send `/start`
4. Enter pincode
5. Verify you receive configuration

## What Changed in Code

### Old Architecture (SSH-based)

```
Bot → SSH → Docker exec → wg commands
```

**Files:**
- `wireguard_manager.py` - SSH operations
- Required: sshpass, SSH access

### New Architecture (API-based)

```
Bot → HTTP REST API → wg-easy
```

**Files:**
- `amnezia_api_client.py` - Low-level API client
- `wireguard_api_manager.py` - High-level manager
- `qr_generator.py` - QR code generation
- No SSH required!

## API Endpoints Used

```
GET  /api/wireguard/client              # List all clients
POST /api/wireguard/client              # Create new client
GET  /api/wireguard/client/{id}/configuration  # Get config
GET  /api/wireguard/client/{id}/qrcode.svg     # Get QR code
DELETE /api/wireguard/client/{id}       # Delete client
POST /api/wireguard/client/{id}/enable  # Enable client
POST /api/wireguard/client/{id}/disable # Disable client
```

## Advantages of New Setup

### 1. No SSH Required
- Removed `sshpass` dependency
- No SSH password in config
- Better security

### 2. Web UI Included
- Manage clients via browser
- Visual monitoring
- Easy troubleshooting

### 3. Cleaner Code
```python
# Old way
stdout, _, _ = self.ssh_exec(f"docker exec {self.container_name} wg genkey")
private_key = stdout.strip()

# New way
client = self.api_client.create_client(name)
```

### 4. Better Error Handling
- HTTP status codes
- JSON error responses
- Standard REST patterns

### 5. More Features Available
- Enable/disable clients
- Client statistics
- Traffic monitoring
- Last handshake times

## Troubleshooting

### API Returns 401 Unauthorized

Check password:
```bash
curl -u admin:YOUR_PASSWORD http://YOUR_SERVER_IP:51821/api/session
```

### Cannot Connect to API

Check if web UI is accessible:
```bash
curl http://YOUR_SERVER_IP:51821
```

Verify container is running:
```bash
docker ps | grep amnezia-wg-easy
```

### Port Already in Use

Check what's using port 51821:
```bash
netstat -tulpn | grep 51821
```

Stop conflicting service or change port in docker run command.

### Old Clients Not Visible

The old container data is separate. You need to:
1. Manually recreate important clients via web UI, or
2. Import old configuration (manual process)

## Configuration Comparison

### Old Setup (amnezia-awg)

**Pros:**
- Deployed by Amnezia mobile app
- Simple initial setup

**Cons:**
- No web UI
- No REST API
- Requires SSH access
- Manual client management

### New Setup (amnezia-wg-easy)

**Pros:**
- Full REST API
- Web UI included
- No SSH needed
- Easy client management
- Better monitoring

**Cons:**
- Need to manually deploy
- Different container

## Rollback Plan

If you need to rollback:

1. Stop new container:
```bash
docker stop amnezia-wg-easy
docker rm amnezia-wg-easy
```

2. Restore old container:
```bash
# Redeploy using Amnezia mobile app
```

3. Restore old bot code:
```bash
git checkout <previous-commit>
```

## Docker Compose Example

Create `docker-compose.yml`:

```yaml
version: '3'
services:
  amnezia-wg-easy:
    image: ghcr.io/w0rng/amnezia-wg-easy
    container_name: amnezia-wg-easy
    environment:
      - LANG=en
      - WG_HOST=YOUR_SERVER_IP
      - PASSWORD=YOUR_ADMIN_PASSWORD
      - PORT=51821
      - WG_PORT=42619
    volumes:
      - ~/.amnezia-wg-easy:/etc/wireguard
    ports:
      - "42619:42619/udp"
      - "51821:51821/tcp"
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
      - net.ipv4.ip_forward=1
    devices:
      - /dev/net/tun:/dev/net/tun
    restart: unless-stopped
```

Then:
```bash
docker-compose up -d
```

## Security Considerations

### Web UI Access

**Secure the web UI:**

1. Use reverse proxy with HTTPS (nginx/Caddy)
2. Restrict access by IP if possible
3. Use strong password
4. Consider VPN-only access

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name vpn.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:51821;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### API Access

The bot connects to API via:
- HTTP (local network) - OK for same server
- HTTPS (internet) - Use reverse proxy

## Next Steps

1. ✅ Backup current setup
2. ✅ Deploy amnezia-wg-easy
3. ✅ Update config file
4. ✅ Test API access
5. ✅ Deploy updated bot
6. ✅ Test end-to-end
7. 📝 Document your admin password
8. 🔐 Secure web UI with HTTPS
9. 📊 Monitor via web UI

## Support Resources

- **wg-easy docs**: https://wg-easy.github.io/wg-easy/latest/
- **amnezia-wg-easy (w0rng)**: https://github.com/w0rng/amnezia-wg-easy
- **amnezia-wg-easy (Xetera)**: https://github.com/Xetera/amnezia-wg-easy

## Summary

The migration brings:
- ✅ Modern REST API
- ✅ Web UI for management
- ✅ No SSH dependency
- ✅ Cleaner architecture
- ✅ Better security
- ✅ More features

**Total migration time: ~15 minutes**

Ready to migrate? Follow the steps above! 🚀
