#!/usr/bin/env python3
"""
ADMS Server for ZKTeco Device Integration with ERPNext
Handles device connectivity, data storage, and ERPNext synchronization
"""

import os
import sys
import time
import json
import logging
import sqlite3
import requests
from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import List, Dict, Optional
from dataclasses import dataclass
from zk import ZK
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, request

# Configuration
@dataclass
class Config:
    # Database
    DATABASE_URL: str = "sqlite:///adms_logs.db"
    
    # ERPNext API
    ERPNEXT_URL: str = "http://localhost:8000"
    ERPNEXT_API_KEY: str = ""
    ERPNEXT_API_SECRET: str = ""
    
    # Device Configuration
    DEVICES: List[Dict] = None
    
    # Polling
    POLL_INTERVAL: int = 30  # seconds
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "adms_server.log"

# Database Models
Base = declarative_base()

class AttendanceLog(Base):
    __tablename__ = 'attendance_logs'
    
    id = Column(Integer, primary_key=True)
    device_ip = Column(String(15), nullable=False)
    user_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String(10), nullable=False)  # IN/OUT
    synced_to_erpnext = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        UniqueConstraint('device_ip', 'user_id', 'timestamp', name='unique_attendance'),
    )

# Database Manager
class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.lock = Lock()
    
    def add_log(self, device_ip: str, user_id: str, timestamp: datetime, status: str) -> bool:
        """Add attendance log, return True if new record"""
        with self.lock:
            try:
                log = AttendanceLog(
                    device_ip=device_ip,
                    user_id=user_id,
                    timestamp=timestamp,
                    status=status
                )
                self.session.add(log)
                self.session.commit()
                return True
            except Exception:
                self.session.rollback()
                return False  # Duplicate or error
    
    def get_unsynced_logs(self) -> List[AttendanceLog]:
        """Get logs not synced to ERPNext"""
        return self.session.query(AttendanceLog).filter_by(synced_to_erpnext=False).all()
    
    def mark_synced(self, log_id: int):
        """Mark log as synced"""
        with self.lock:
            log = self.session.query(AttendanceLog).get(log_id)
            if log:
                log.synced_to_erpnext = True
                self.session.commit()
    
    def get_all_logs(self) -> List[Dict]:
        """Get all logs as dict"""
        logs = self.session.query(AttendanceLog).all()
        return [{
            'id': log.id,
            'device_ip': log.device_ip,
            'user_id': log.user_id,
            'timestamp': log.timestamp.isoformat(),
            'status': log.status,
            'synced_to_erpnext': log.synced_to_erpnext,
            'created_at': log.created_at.isoformat()
        } for log in logs]

# ERPNext API Client
class ERPNextClient:
    def __init__(self, url: str, api_key: str, api_secret: str):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {api_key}:{api_secret}',
            'Content-Type': 'application/json'
        })
    
    def push_attendance(self, user_id: str, timestamp: datetime, status: str, device_ip: str) -> bool:
        """Push attendance to ERPNext"""
        try:
            # Find employee by device_user_id
            employee_response = self.session.get(
                f"{self.url}/api/resource/Employee",
                params={'filters': json.dumps([['device_user_id', '=', user_id]])}
            )
            
            if employee_response.status_code != 200:
                logging.warning(f"Failed to find employee for user_id {user_id}")
                return False
            
            employees = employee_response.json().get('data', [])
            if not employees:
                logging.warning(f"No employee found for device user_id {user_id}")
                return False
            
            employee = employees[0]['name']
            
            # Create Employee Checkin
            checkin_data = {
                'employee': employee,
                'time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'log_type': status,
                'device_id': device_ip
            }
            
            response = self.session.post(
                f"{self.url}/api/resource/Employee Checkin",
                json=checkin_data
            )
            
            if response.status_code in [200, 201]:
                logging.info(f"Successfully pushed attendance for {employee}")
                return True
            else:
                logging.error(f"Failed to push attendance: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"ERPNext API error: {e}")
            return False

# Device Manager
class DeviceManager:
    def __init__(self, devices: List[Dict], db_manager: DatabaseManager):
        self.devices = devices
        self.db_manager = db_manager
        self.connections = {}
    
    def connect_device(self, device: Dict) -> Optional[ZK]:
        """Connect to a ZKTeco device"""
        try:
            zk = ZK(device['ip'], port=device.get('port', 4370), timeout=5)
            conn = zk.connect()
            logging.info(f"Connected to device {device['ip']}")
            return conn
        except Exception as e:
            logging.error(f"Failed to connect to {device['ip']}: {e}")
            return None
    
    def fetch_attendance_logs(self, device: Dict) -> List[Dict]:
        """Fetch attendance logs from device"""
        conn = self.connect_device(device)
        if not conn:
            return []
        
        try:
            attendances = conn.get_attendance()
            logs = []
            
            for att in attendances:
                logs.append({
                    'device_ip': device['ip'],
                    'user_id': str(att.user_id),
                    'timestamp': att.timestamp,
                    'status': 'IN' if att.status == 1 else 'OUT'
                })
            
            conn.disconnect()
            logging.info(f"Fetched {len(logs)} logs from {device['ip']}")
            return logs
            
        except Exception as e:
            logging.error(f"Error fetching logs from {device['ip']}: {e}")
            if conn:
                conn.disconnect()
            return []
    
    def fetch_all_devices(self) -> List[Dict]:
        """Fetch logs from all devices"""
        all_logs = []
        for device in self.devices:
            logs = self.fetch_attendance_logs(device)
            all_logs.extend(logs)
        return all_logs

# Main ADMS Server
class ADMSServer:
    def __init__(self, config: Config):
        self.config = config
        self.db_manager = DatabaseManager(config.DATABASE_URL)
        self.erpnext_client = ERPNextClient(
            config.ERPNEXT_URL, 
            config.ERPNEXT_API_KEY, 
            config.ERPNEXT_API_SECRET
        ) if config.ERPNEXT_API_KEY else None
        self.device_manager = DeviceManager(config.DEVICES or [], self.db_manager)
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def fetch_and_store_logs(self):
        """Fetch logs from devices and store in database"""
        logs = self.device_manager.fetch_all_devices()
        new_count = 0
        
        for log in logs:
            if self.db_manager.add_log(
                log['device_ip'], 
                log['user_id'], 
                log['timestamp'], 
                log['status']
            ):
                new_count += 1
        
        if new_count > 0:
            logging.info(f"Stored {new_count} new attendance logs")
        
        return new_count
    
    def sync_to_erpnext(self):
        """Sync unsynced logs to ERPNext"""
        if not self.erpnext_client:
            return 0
        
        unsynced_logs = self.db_manager.get_unsynced_logs()
        synced_count = 0
        
        for log in unsynced_logs:
            for attempt in range(self.config.RETRY_ATTEMPTS):
                if self.erpnext_client.push_attendance(
                    log.user_id, 
                    log.timestamp, 
                    log.status, 
                    log.device_ip
                ):
                    self.db_manager.mark_synced(log.id)
                    synced_count += 1
                    break
                else:
                    if attempt < self.config.RETRY_ATTEMPTS - 1:
                        time.sleep(self.config.RETRY_DELAY)
        
        if synced_count > 0:
            logging.info(f"Synced {synced_count} logs to ERPNext")
        
        return synced_count
    
    def run_cycle(self):
        """Run one complete cycle"""
        try:
            new_logs = self.fetch_and_store_logs()
            synced_logs = self.sync_to_erpnext()
            logging.debug(f"Cycle complete: {new_logs} new, {synced_logs} synced")
        except Exception as e:
            logging.error(f"Error in cycle: {e}")
    
    def start(self):
        """Start the ADMS server"""
        self.running = True
        logging.info("ADMS Server started")
        
        while self.running:
            self.run_cycle()
            time.sleep(self.config.POLL_INTERVAL)
    
    def stop(self):
        """Stop the ADMS server"""
        self.running = False
        logging.info("ADMS Server stopped")

# Flask API
def create_flask_app(adms_server: ADMSServer) -> Flask:
    app = Flask(__name__)
    
    @app.route('/api/fetch', methods=['POST'])
    def manual_fetch():
        """Manually trigger fetch from all devices"""
        try:
            new_logs = adms_server.fetch_and_store_logs()
            synced_logs = adms_server.sync_to_erpnext()
            return jsonify({
                'success': True,
                'new_logs': new_logs,
                'synced_logs': synced_logs
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        """Get all stored logs"""
        try:
            logs = adms_server.db_manager.get_all_logs()
            return jsonify({'success': True, 'logs': logs})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/status', methods=['GET'])
    def get_status():
        """Get server status"""
        unsynced_count = len(adms_server.db_manager.get_unsynced_logs())
        return jsonify({
            'success': True,
            'running': adms_server.running,
            'devices_configured': len(adms_server.config.DEVICES or []),
            'unsynced_logs': unsynced_count
        })
    
    return app

# Configuration loader
def load_config(config_file: str = "adms_config.json") -> Config:
    """Load configuration from file"""
    config = Config()
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Default devices if none configured
    if not config.DEVICES:
        config.DEVICES = [
            {"ip": "192.168.1.201", "port": 4370},
            {"ip": "192.168.1.202", "port": 4370},
            {"ip": "192.168.1.203", "port": 4370},
            {"ip": "192.168.1.204", "port": 4370}
        ]
    
    return config

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ADMS Server for ZKTeco Integration')
    parser.add_argument('--config', default='adms_config.json', help='Configuration file')
    parser.add_argument('--api-only', action='store_true', help='Run only Flask API')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    args = parser.parse_args()
    
    config = load_config(args.config)
    adms_server = ADMSServer(config)
    
    if args.api_only:
        # Run only Flask API
        app = create_flask_app(adms_server)
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        # Run main server with optional API
        if args.daemon:
            # Run in background
            server_thread = Thread(target=adms_server.start, daemon=True)
            server_thread.start()
            
            # Start Flask API in main thread
            app = create_flask_app(adms_server)
            app.run(host='0.0.0.0', port=5000, debug=False)
        else:
            # Run main server only
            try:
                adms_server.start()
            except KeyboardInterrupt:
                adms_server.stop()

if __name__ == "__main__":
    main()