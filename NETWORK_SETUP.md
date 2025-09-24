# Network Setup for Local Devices → Cloud ERPNext

## Option 1: Port Forwarding (Easiest)

### Router Configuration:
1. Access your router admin panel
2. Go to Port Forwarding/Virtual Server
3. Add rule:
   - External Port: 7788
   - Internal IP: [Cloud Server IP]
   - Internal Port: 7788
   - Protocol: TCP

### Device Configuration:
```
Server IP: [Your Public IP Address]
Port: 7788
Path: /iclock/
Protocol: ADMS
```

### Find Your Public IP:
```bash
curl ifconfig.me
```

## Option 2: Nginx Reverse Proxy

### On Cloud Server - Add to nginx config:
```nginx
server {
    listen 7788;
    server_name your-domain.com;
    
    location /iclock/ {
        proxy_pass http://localhost:8000/iclock/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Device Configuration:
```
Server IP: your-domain.com
Port: 7788
Path: /iclock/
```

## Option 3: Cloudflare Tunnel (No Port Forwarding)

### Install cloudflared on cloud server:
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel create zkteco
cloudflared tunnel route dns zkteco zkteco.yourdomain.com

# Configure tunnel
echo "tunnel: [tunnel-id]
credentials-file: /root/.cloudflared/[tunnel-id].json
ingress:
  - hostname: zkteco.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404" > ~/.cloudflared/config.yml

# Run tunnel
cloudflared tunnel run zkteco
```

### Device Configuration:
```
Server IP: zkteco.yourdomain.com
Port: 443
Path: /iclock/
```

## Testing Connection

### From local network:
```bash
# Test if cloud server is reachable
telnet [cloud-server-ip] 7788

# Test API endpoint
curl -X GET "http://[cloud-server-ip]:7788/iclock/?SN=TEST123"
```

### Expected Response:
```
OK
```

## Firewall Configuration

### On Cloud Server:
```bash
# Allow port 7788
sudo ufw allow 7788/tcp

# Or for specific IP range
sudo ufw allow from 192.168.1.0/24 to any port 7788
```

## Troubleshooting

1. **Connection Timeout:**
   - Check firewall rules
   - Verify port forwarding
   - Test with telnet

2. **Device Shows "Server Error":**
   - Check ERPNext logs: `bench logs`
   - Verify `/iclock/` endpoint works
   - Check device network settings

3. **No Data Sync:**
   - Verify device sends data to correct path
   - Check ZK Log in ERPNext for raw data
   - Ensure employees have Device User ID set