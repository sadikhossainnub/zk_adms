# ADMS Server for ZKTeco Integration

A comprehensive Linux-based ADMS (Attendance Device Management Service) server that integrates ZKTeco attendance devices with ERPNext.

## Features

- **Multi-device Support**: Connect to multiple ZKTeco devices over LAN
- **Local Database**: SQLite storage with duplicate prevention
- **ERPNext Integration**: Automatic sync via REST API with retry logic
- **Flexible Deployment**: Run as systemd service or cron job
- **REST API**: Manual control and monitoring endpoints
- **Comprehensive Logging**: Detailed logs for troubleshooting

## Architecture

```
ZKTeco Devices → ADMS Server → Local SQLite DB → ERPNext API
                     ↓
                 Flask API (Optional)
```

## Installation

### Prerequisites

```bash
# Install Python dependencies
sudo apt update
sudo apt install python3 python3-pip sqlite3

# Install required Python packages
pip3 install pyzk SQLAlchemy Flask requests
```

### Quick Setup

1. **Clone/Download the ADMS server files**
2. **Run the setup script**:
   ```bash
   chmod +x setup_adms.sh
   ./setup_adms.sh
   ```
3. **Configure your settings** (see Configuration section)

## Configuration

### 1. Edit `adms_config.json`

```json
{
  "DATABASE_URL": "sqlite:///adms_logs.db",
  "ERPNEXT_URL": "http://your-erpnext-server:8000",
  "ERPNEXT_API_KEY": "your_api_key",
  "ERPNEXT_API_SECRET": "your_api_secret",
  "DEVICES": [
    {"ip": "192.168.1.201", "port": 4370},
    {"ip": "192.168.1.202", "port": 4370},
    {"ip": "192.168.1.203", "port": 4370},
    {"ip": "192.168.1.204", "port": 4370}
  ],
  "POLL_INTERVAL": 30,
  "RETRY_ATTEMPTS": 3,
  "RETRY_DELAY": 5,
  "LOG_LEVEL": "INFO",
  "LOG_FILE": "adms_server.log"
}
```

### 2. ERPNext API Setup

1. **Create API Key in ERPNext**:
   - Go to: Settings → API Access
   - Create new API Key and Secret
   - Update `adms_config.json` with credentials

2. **Ensure Employee Setup**:
   - Each Employee must have `device_user_id` field populated
   - This field maps to the user ID on ZKTeco devices

### 3. ZKTeco Device Configuration

Configure each device with:
- **Server IP**: Your ADMS server IP
- **Port**: 4370 (default ZK port)
- **Communication**: TCP/IP

**Example Device Settings**:
```
IP Address: 192.168.1.201
Subnet Mask: 255.255.255.0
Gateway: 192.168.1.1
Server IP: 192.168.1.100  # Your ADMS server
Port: 4370
```

## Deployment Options

### Option 1: Systemd Service (Recommended)

```bash
# Install services
sudo systemctl enable adms-server.service
sudo systemctl enable adms-api.service

# Start services
sudo systemctl start adms-server
sudo systemctl start adms-api

# Check status
sudo systemctl status adms-server
sudo journalctl -u adms-server -f
```

### Option 2: Cron Job

```bash
# Add to crontab (runs every 5 minutes)
crontab -e
*/5 * * * * /path/to/adms_cron.py

# View logs
tail -f adms_cron.log
```

### Option 3: Manual Execution

```bash
# Run main server
python3 adms_server.py

# Run with API
python3 adms_server.py --daemon

# Run API only
python3 adms_server.py --api-only
```

## Database Schema

### AttendanceLog Table

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| device_ip | String | Device IP address |
| user_id | String | Device user ID |
| timestamp | DateTime | Attendance timestamp |
| status | String | IN/OUT |
| synced_to_erpnext | Boolean | Sync status |
| created_at | DateTime | Record creation time |

**Unique Constraint**: (device_ip, user_id, timestamp)

## API Endpoints

### Manual Fetch
```bash
POST http://localhost:5000/api/fetch
```
Triggers immediate fetch from all devices.

**Response**:
```json
{
  "success": true,
  "new_logs": 5,
  "synced_logs": 3
}
```

### Get All Logs
```bash
GET http://localhost:5000/api/logs
```
Returns all stored attendance logs.

### Server Status
```bash
GET http://localhost:5000/api/status
```
Returns server status and statistics.

**Response**:
```json
{
  "success": true,
  "running": true,
  "devices_configured": 4,
  "unsynced_logs": 2
}
```

## Monitoring and Troubleshooting

### Log Files

- **Main Server**: `adms_server.log`
- **Cron Jobs**: `adms_cron.log`
- **Systemd**: `journalctl -u adms-server`

### Common Issues

1. **Device Connection Failed**
   ```
   Error: Failed to connect to 192.168.1.201
   ```
   - Check device IP and network connectivity
   - Verify device is powered on
   - Check firewall settings

2. **ERPNext Sync Failed**
   ```
   Error: Failed to find employee for user_id 123
   ```
   - Ensure Employee has `device_user_id` field set
   - Verify ERPNext API credentials
   - Check ERPNext server accessibility

3. **Database Errors**
   ```
   Error: Database locked
   ```
   - Check file permissions
   - Ensure only one instance is running

### Performance Tuning

- **Poll Interval**: Adjust based on attendance frequency
- **Retry Settings**: Increase for unreliable networks
- **Database**: Use PostgreSQL/MySQL for high volume

## Network Setup Example

### Network Topology
```
Internet
    |
Router/Switch (192.168.1.1)
    |
    ├── ADMS Server (192.168.1.100)
    ├── ERPNext Server (192.168.1.50)
    ├── ZKTeco Device 1 (192.168.1.201)
    ├── ZKTeco Device 2 (192.168.1.202)
    ├── ZKTeco Device 3 (192.168.1.203)
    └── ZKTeco Device 4 (192.168.1.204)
```

### Firewall Configuration

```bash
# Allow ZKTeco device communication
sudo ufw allow from 192.168.1.0/24 to any port 4370
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Allow ERPNext communication
sudo ufw allow out 8000
```

## Security Considerations

1. **Network Security**:
   - Use VPN for remote access
   - Implement network segmentation
   - Regular security updates

2. **API Security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Monitor API access logs

3. **Database Security**:
   - Regular backups
   - Encrypt sensitive data
   - Restrict file permissions

## Backup and Recovery

### Database Backup
```bash
# SQLite backup
cp adms_logs.db adms_logs_backup_$(date +%Y%m%d).db

# Automated backup script
0 2 * * * cp /path/to/adms_logs.db /backup/adms_logs_$(date +\%Y\%m\%d).db
```

### Configuration Backup
```bash
# Backup configuration
tar -czf adms_backup_$(date +%Y%m%d).tar.gz adms_config.json *.service *.py
```

## Development and Testing

### Test Device Connection
```python
from zk import ZK

zk = ZK('192.168.1.201', port=4370, timeout=5)
conn = zk.connect()
print("Connected successfully")
conn.disconnect()
```

### Test ERPNext API
```bash
curl -X GET "http://localhost:8000/api/resource/Employee" \
  -H "Authorization: token api_key:api_secret"
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Log Rotation**: Implement log rotation to prevent disk space issues
2. **Database Cleanup**: Archive old records periodically
3. **Device Health Check**: Monitor device connectivity
4. **Performance Monitoring**: Track sync performance and errors

### Monitoring Script Example
```bash
#!/bin/bash
# Check ADMS server health
curl -s http://localhost:5000/api/status | jq '.running' || echo "ADMS API not responding"
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request with tests
4. Update documentation

---

For additional support, check the logs and ensure all configuration parameters are correctly set.