### ZKTeco ADMS

ZKTeco Biometric Attendance Device Integration for ERPNext v15

This app provides seamless integration with ZKTeco attendance devices using the ADMS protocol, automatically syncing attendance data to ERPNext Employee Checkin records.

## Features

- **Device Management**: Auto-register ZKTeco devices and monitor their status
- **Real-time Sync**: Automatic attendance data synchronization
- **Employee Mapping**: Map device user IDs to ERPNext employees
- **Debug Logging**: Raw log storage for troubleshooting
- **Status Monitoring**: Track device online/offline status with heartbeat

### Installation

1. Install the app using bench:
```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/your-repo/zk_adms --branch main
bench install-app zk_adms
bench restart
```

2. The app will automatically:
   - Create required doctypes (Attendance Device, ZK Log)
   - Add "Device User ID" field to Employee doctype
   - Set up the `/iclock/` API endpoint

### ZKTeco Device Configuration

Configure your ZKTeco device with these settings:

- **Server IP**: Your ERPNext server IP address
- **Port**: 7788
- **Path**: `/iclock/`
- **Protocol**: ADMS

**Example Device Settings:**
```
Server IP: 192.168.1.100
Port: 7788
Path: /iclock/
Protocol: ADMS
```

### Employee Setup

1. Go to Employee master
2. Set the "Device User ID" field to match the user ID on your ZKTeco device
3. Save the employee record

### Usage

1. **Monitor Devices**: Go to ZKTeco ADMS workspace to view connected devices
2. **View Logs**: Check ZK Log for raw attendance data from devices
3. **Attendance Records**: Processed attendance appears in Employee Checkin

### API Endpoints

- `POST/GET /iclock/`: Main ADMS endpoint for device communication
- Supports both attendance data (`/iclock/cdata`) and heartbeat (`/iclock/getrequest`)

### Troubleshooting

1. **Device Not Connecting**:
   - Check network connectivity
   - Verify server IP and port settings
   - Check ERPNext site is accessible

2. **Attendance Not Syncing**:
   - Verify "Device User ID" is set for employees
   - Check ZK Log for raw data
   - Review error logs in ERPNext

3. **Device Shows Offline**:
   - Devices are marked offline after 5 minutes of no communication
   - Check device network settings and connectivity

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/zk_adms
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

MIT
