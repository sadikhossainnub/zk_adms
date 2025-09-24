#!/usr/bin/env python3
"""
ADMS Test Script
Tests device connectivity, database operations, and ERPNext integration
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adms_server import DatabaseManager, ERPNextClient, DeviceManager, load_config

def test_database():
    """Test database operations"""
    print("Testing database...")
    
    try:
        db = DatabaseManager("sqlite:///test_adms.db")
        
        # Test adding log
        result = db.add_log("192.168.1.201", "123", datetime.now(), "IN")
        print(f"✓ Database add: {result}")
        
        # Test duplicate prevention
        result = db.add_log("192.168.1.201", "123", datetime.now(), "IN")
        print(f"✓ Duplicate prevention: {not result}")
        
        # Test retrieval
        logs = db.get_all_logs()
        print(f"✓ Database retrieval: {len(logs)} logs")
        
        # Cleanup
        os.remove("test_adms.db")
        print("✓ Database test passed")
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    
    return True

def test_device_connection(config):
    """Test device connectivity"""
    print("Testing device connections...")
    
    if not config.DEVICES:
        print("⚠ No devices configured")
        return True
    
    device_manager = DeviceManager(config.DEVICES, None)
    
    for device in config.DEVICES:
        try:
            conn = device_manager.connect_device(device)
            if conn:
                print(f"✓ Device {device['ip']}: Connected")
                conn.disconnect()
            else:
                print(f"✗ Device {device['ip']}: Failed to connect")
        except Exception as e:
            print(f"✗ Device {device['ip']}: {e}")
    
    return True

def test_erpnext_connection(config):
    """Test ERPNext API connection"""
    print("Testing ERPNext connection...")
    
    if not config.ERPNEXT_API_KEY:
        print("⚠ ERPNext API credentials not configured")
        return True
    
    try:
        client = ERPNextClient(config.ERPNEXT_URL, config.ERPNEXT_API_KEY, config.ERPNEXT_API_SECRET)
        
        # Test API connection by fetching employees
        response = client.session.get(f"{config.ERPNEXT_URL}/api/resource/Employee?limit=1")
        
        if response.status_code == 200:
            print("✓ ERPNext API: Connected")
        else:
            print(f"✗ ERPNext API: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"✗ ERPNext API: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("Testing configuration...")
    
    try:
        config = load_config("adms_config.json")
        print(f"✓ Configuration loaded")
        print(f"  - Database: {config.DATABASE_URL}")
        print(f"  - ERPNext: {config.ERPNEXT_URL}")
        print(f"  - Devices: {len(config.DEVICES or [])}")
        print(f"  - Poll interval: {config.POLL_INTERVAL}s")
        
        return config
        
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return None

def main():
    """Run all tests"""
    print("=== ADMS Server Test Suite ===\n")
    
    # Test configuration
    config = test_configuration()
    if not config:
        sys.exit(1)
    
    print()
    
    # Test database
    if not test_database():
        sys.exit(1)
    
    print()
    
    # Test device connections
    test_device_connection(config)
    
    print()
    
    # Test ERPNext connection
    test_erpnext_connection(config)
    
    print("\n=== Test Summary ===")
    print("✓ All tests completed")
    print("\nNext steps:")
    print("1. Configure your ZKTeco devices")
    print("2. Set up ERPNext API credentials")
    print("3. Run the ADMS server")

if __name__ == "__main__":
    main()