#!/bin/bash

# ADMS Server Setup Script
# This script sets up the ADMS server for ZKTeco integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADMS_USER="frappe"
ADMS_GROUP="frappe"

echo "=== ADMS Server Setup ==="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as the frappe user."
   exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."

# Check if virtual environment exists, create if not
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies in virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install -r "$SCRIPT_DIR/requirements_adms.txt"
deactivate

# Make scripts executable
echo "Setting up permissions..."
chmod +x "$SCRIPT_DIR/adms_server.py"
chmod +x "$SCRIPT_DIR/adms_cron.py"

# Create log directory
mkdir -p "$SCRIPT_DIR/logs"

# Setup configuration
if [ ! -f "$SCRIPT_DIR/adms_config.json" ]; then
    echo "Configuration file not found. Please edit adms_config.json with your settings."
    exit 1
fi

echo "Configuration found at: $SCRIPT_DIR/adms_config.json"

# Test database connection
echo "Testing database setup..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from adms_server import DatabaseManager, load_config
config = load_config('$SCRIPT_DIR/adms_config.json')
db = DatabaseManager(config.DATABASE_URL)
print('Database setup successful')
"

echo "=== Setup Options ==="
echo "1. Setup as systemd service (recommended)"
echo "2. Setup as cron job"
echo "3. Manual setup only"
read -p "Choose setup option (1-3): " choice

case $choice in
    1)
        echo "Setting up systemd services..."
        
        # Copy service files (requires sudo)
        echo "The following commands require sudo privileges:"
        sudo cp "$SCRIPT_DIR/adms-server.service" /etc/systemd/system/
        sudo cp "$SCRIPT_DIR/adms-api.service" /etc/systemd/system/
        
        # Update service files with correct paths
        sudo sed -i "s|/home/primetechbd/frappe-bench/apps/zk_adms|$SCRIPT_DIR|g" /etc/systemd/system/adms-server.service
        sudo sed -i "s|/home/primetechbd/frappe-bench/apps/zk_adms|$SCRIPT_DIR|g" /etc/systemd/system/adms-api.service
        
        # Set correct user
        sudo sed -i "s|User=frappe|User=$USER|g" /etc/systemd/system/adms-server.service
        sudo sed -i "s|Group=frappe|Group=$USER|g" /etc/systemd/system/adms-server.service
        sudo sed -i "s|User=frappe|User=$USER|g" /etc/systemd/system/adms-api.service
        sudo sed -i "s|Group=frappe|Group=$USER|g" /etc/systemd/system/adms-api.service
        
        # Reload systemd and enable services
        sudo systemctl daemon-reload
        sudo systemctl enable adms-server.service
        sudo systemctl enable adms-api.service
        
        echo "Systemd services installed. Use the following commands:"
        echo "  Start ADMS server: sudo systemctl start adms-server"
        echo "  Start ADMS API: sudo systemctl start adms-api"
        echo "  Check status: sudo systemctl status adms-server"
        echo "  View logs: sudo journalctl -u adms-server -f"
        ;;
        
    2)
        echo "Setting up cron job..."
        
        # Add cron job for every 5 minutes
        (crontab -l 2>/dev/null; echo "*/5 * * * * $SCRIPT_DIR/adms_cron.py") | crontab -
        
        echo "Cron job added. ADMS will run every 5 minutes."
        echo "View cron logs: tail -f $SCRIPT_DIR/adms_cron.log"
        ;;
        
    3)
        echo "Manual setup completed."
        echo "Run manually: python3 $SCRIPT_DIR/adms_server.py"
        ;;
        
    *)
        echo "Invalid choice. Manual setup completed."
        ;;
esac

echo ""
echo "=== Next Steps ==="
echo "1. Edit $SCRIPT_DIR/adms_config.json with your ERPNext API credentials"
echo "2. Configure your ZKTeco devices to connect to this server"
echo "3. Ensure Employee records have 'device_user_id' field populated"
echo ""
echo "=== Device Configuration ==="
echo "Configure your ZKTeco devices with:"
echo "  Server IP: $(hostname -I | awk '{print $1}')"
echo "  Port: 7788 (for ADMS protocol via existing proxy)"
echo "  Path: /iclock/"
echo ""
echo "=== API Endpoints ==="
echo "  Manual fetch: POST http://localhost:5000/api/fetch"
echo "  View logs: GET http://localhost:5000/api/logs"
echo "  Server status: GET http://localhost:5000/api/status"
echo ""
echo "Setup completed successfully!"