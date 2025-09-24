import frappe  # type: ignore
from frappe import _  # type: ignore
from datetime import datetime
import json

@frappe.whitelist(allow_guest=True, methods=["POST", "GET"])
def iclock():
	"""Main ADMS endpoint for ZKTeco devices"""
	try:
		# Log the request for debugging
		frappe.logger().info(f"ADMS Request: {frappe.request.method} {frappe.request.url}")
		frappe.logger().info(f"Headers: {dict(frappe.request.headers)}")
		frappe.logger().info(f"Data: {frappe.request.get_data()}")
		
		# Get device serial number from SN parameter
		sn = frappe.form_dict.get('SN')
		if not sn:
			return "ERROR: No SN provided"
		
		# Handle different request types
		if frappe.request.method == "POST":
			return handle_post_request(sn)
		else:
			return handle_get_request(sn)
			
	except Exception as e:
		frappe.logger().error(f"ADMS Error: {str(e)}")
		return "ERROR"

def handle_post_request(sn):
	"""Handle POST requests (attendance data)"""
	try:
		# Ensure device exists
		device = get_or_create_device(sn)
		
		# Update device status and sync time
		device.status = "Online"
		device.last_sync_time = datetime.now()
		device.ip_address = frappe.local.request_ip
		device.save(ignore_permissions=True)
		
		# Process attendance data if present
		data = frappe.request.get_data(as_text=True)
		if data and data.strip():
			process_attendance_data(sn, data)
		
		return "OK"
		
	except Exception as e:
		frappe.logger().error(f"POST Error: {str(e)}")
		return "ERROR"

def handle_get_request(sn):
	"""Handle GET requests (heartbeat/status)"""
	try:
		# Ensure device exists
		device = get_or_create_device(sn)
		
		# Update device status and sync time
		device.status = "Online"
		device.last_sync_time = datetime.now()
		device.ip_address = frappe.local.request_ip
		device.save(ignore_permissions=True)
		
		return "OK"
		
	except Exception as e:
		frappe.logger().error(f"GET Error: {str(e)}")
		return "ERROR"

def get_or_create_device(sn):
	"""Get existing device or create new one"""
	if frappe.db.exists("Attendance Device", sn):
		return frappe.get_doc("Attendance Device", sn)
	else:
		device = frappe.new_doc("Attendance Device")
		device.serial_number = sn
		device.device_name = f"ZKTeco Device {sn}"
		device.status = "Online"
		device.last_sync_time = datetime.now()
		device.ip_address = frappe.local.request_ip
		device.insert(ignore_permissions=True)
		return device

def process_attendance_data(sn, data):
	"""Process attendance data from device"""
	try:
		lines = data.strip().split('\n')
		for line in lines:
			if not line.strip():
				continue
				
			# Parse attendance record
			# Format: USER_ID\tTIMESTAMP\tPUNCH_TYPE\tOTHER_DATA
			parts = line.split('\t')
			if len(parts) < 3:
				continue
				
			user_id = parts[0]
			timestamp_str = parts[1]
			punch_type = "IN" if parts[2] == "0" else "OUT"
			
			# Parse timestamp
			try:
				timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
			except:
				continue
			
			# Create ZK Log entry
			zk_log = frappe.new_doc("ZK Log")
			zk_log.device_serial = sn
			zk_log.user_id = user_id
			zk_log.timestamp = timestamp
			zk_log.punch_type = punch_type
			zk_log.raw_data = line
			zk_log.insert(ignore_permissions=True)
			
			# Find employee by device user ID
			employee = find_employee_by_device_id(user_id)
			if employee:
				# Create Employee Checkin
				checkin = frappe.new_doc("Employee Checkin")
				checkin.employee = employee
				checkin.time = timestamp
				checkin.log_type = punch_type
				checkin.device_id = sn
				checkin.insert(ignore_permissions=True)
				
				# Update ZK Log with checkin reference
				zk_log.employee_checkin = checkin.name
				zk_log.processed = 1
				zk_log.save(ignore_permissions=True)
			
	except Exception as e:
		frappe.logger().error(f"Data processing error: {str(e)}")

def find_employee_by_device_id(device_user_id):
	"""Find employee by device user ID"""
	# Check if Employee has device_user_id custom field
	if frappe.db.has_column("Employee", "device_user_id"):
		employee = frappe.db.get_value("Employee", {"device_user_id": device_user_id}, "name")
		if employee:
			return employee
	
	# Fallback: try to match by employee_number or name
	employee = frappe.db.get_value("Employee", {"employee_number": device_user_id}, "name")
	if employee:
		return employee
		
	return None