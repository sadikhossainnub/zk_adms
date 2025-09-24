# ZKTeco Device Configuration Guide

## Device Network Settings

Configure your ZKTeco attendance device with the following settings:

### Basic Configuration
- **Server IP**: `192.168.1.100` (Replace with your ERPNext server IP)
- **Port**: `7788`
- **Path**: `/iclock/`
- **Protocol**: `ADMS`

### Advanced Settings
- **Upload Interval**: `1` minute (for real-time sync)
- **Heartbeat Interval**: `30` seconds
- **Max Records**: `1000` (per upload batch)

## Device Menu Navigation

### For ZKTeco K40/K50 Series:
1. Press **MENU** → **System** → **Communication**
2. Set **Server IP** to your ERPNext server IP
3. Set **Port** to `7788`
4. Set **Path** to `/iclock/`
5. Enable **Auto Upload**
6. Save settings and restart device

### For ZKTeco F18/F19 Series:
1. Access web interface at device IP
2. Go to **Communication** → **Network Settings**
3. Configure server settings as above
4. Enable **Real-time Upload**

## Testing Connection

1. Check device display for connection status
2. In ERPNext, go to **ZKTeco ADMS** workspace
3. Look for your device in **Attendance Device** list
4. Status should show **Online** with recent **Last Sync Time**

## Troubleshooting

### Device Shows "Connection Failed"
- Verify network connectivity: `ping [server_ip]`
- Check firewall settings on server
- Ensure ERPNext site is accessible from device network

### Device Connects but No Data
- Verify `/iclock/` endpoint is accessible
- Check ERPNext error logs
- Ensure employees have **Device User ID** set

### Data Sync Issues
- Check **ZK Log** for raw data from device
- Verify employee **Device User ID** matches device user ID
- Review **Employee Checkin** for processed records

## Example cURL Test

Test the endpoint manually:

```bash
# Test heartbeat
curl -X GET "http://your-server:7788/iclock/?SN=TEST123456"

# Test data upload
curl -X POST "http://your-server:7788/iclock/?SN=TEST123456" \
  -d "001	2024-01-01 09:00:00	0	1"
```

Expected response: `OK`