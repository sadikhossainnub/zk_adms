import frappe
from datetime import datetime, timedelta

def mark_offline_devices():
	"""Mark devices as offline if no heartbeat for 5 minutes"""
	cutoff_time = datetime.now() - timedelta(minutes=5)
	
	devices = frappe.get_all("Attendance Device", 
		filters={
			"status": "Online",
			"last_sync_time": ["<", cutoff_time]
		},
		fields=["name"]
	)
	
	for device in devices:
		doc = frappe.get_doc("Attendance Device", device.name)
		doc.status = "Offline"
		doc.save(ignore_permissions=True)
	
	if devices:
		frappe.logger().info(f"Marked {len(devices)} devices as offline")