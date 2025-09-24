#!/usr/bin/env python3
"""
ADMS Cron Script - Run attendance sync as a cron job
Usage: Add to crontab: */5 * * * * /path/to/adms_cron.py
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adms_server import ADMSServer, load_config

def main():
    """Run one sync cycle"""
    try:
        # Load configuration
        config_file = os.path.join(os.path.dirname(__file__), 'adms_config.json')
        config = load_config(config_file)
        
        # Setup logging for cron
        log_file = os.path.join(os.path.dirname(__file__), 'adms_cron.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Create server instance
        server = ADMSServer(config)
        
        # Run one cycle
        logging.info("Starting ADMS cron cycle")
        server.run_cycle()
        logging.info("ADMS cron cycle completed")
        
    except Exception as e:
        logging.error(f"ADMS cron error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()