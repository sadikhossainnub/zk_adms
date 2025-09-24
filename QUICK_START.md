# ADMS Server - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip3 install --user pyzk SQLAlchemy Flask requests
```

### 2. Configure Settings
Edit `adms_config.json`:
```json
{
  "ERPNEXT_URL": "http://your-server:8000",
  "ERPNEXT_API_KEY": "your_api_key",
  "ERPNEXT_API_SECRET": "your_api_secret",
  "DEVICES": [
    {"ip": "192.168.1.201", "port": 4370},
    {"ip": "192.168.1.202", "port": 4370}
  ]
}
```

### 3. Test Setup
```bash
./test_adms.py
```

### 4. Run Server
```bash
# Option A: Run directly
./adms_server.py

# Option B: Run as service
./setup_adms.sh

# Option C: Run with API
./adms_server.py --daemon
```

## 📱 Device Configuration

Configure each ZKTeco device:
- **Server IP**: Your ADMS server IP
- **Port**: 4370
- **Protocol**: TCP/IP

## 👥 Employee Setup

In ERPNext Employee master:
1. Set "Device User ID" field
2. Match with ZKTeco device user ID

## 🔍 Monitoring

### Check Status
```bash
curl http://localhost:5000/api/status
```

### View Logs
```bash
tail -f adms_server.log
```

### Manual Sync
```bash
curl -X POST http://localhost:5000/api/fetch
```

## 🛠 Troubleshooting

### Device Not Connecting
- Check IP and network connectivity
- Verify device is powered on
- Test with: `ping device_ip`

### No Attendance Data
- Verify Employee "Device User ID" is set
- Check device user enrollment
- Review logs for errors

### ERPNext Sync Issues
- Verify API credentials
- Check ERPNext server accessibility
- Review Employee Checkin permissions

## 📊 Example Network Setup

```
Router (192.168.1.1)
├── ADMS Server (192.168.1.100)
├── ERPNext Server (192.168.1.50)
├── ZK Device 1 (192.168.1.201)
└── ZK Device 2 (192.168.1.202)
```

## 🔄 Production Deployment

### Systemd Service
```bash
sudo ./setup_adms.sh
sudo systemctl start adms-server
sudo systemctl enable adms-server
```

### Cron Job (Alternative)
```bash
crontab -e
# Add: */5 * * * * /path/to/adms_cron.py
```

## 📈 Monitoring Commands

```bash
# Service status
sudo systemctl status adms-server

# View logs
sudo journalctl -u adms-server -f

# API status
curl http://localhost:5000/api/status

# Database stats
sqlite3 adms_logs.db "SELECT COUNT(*) FROM attendance_logs;"
```

## 🆘 Support

- Check `ADMS_SERVER_README.md` for detailed documentation
- Review log files for error messages
- Test individual components with `test_adms.py`

---

**Need help?** Check the comprehensive documentation in `ADMS_SERVER_README.md`