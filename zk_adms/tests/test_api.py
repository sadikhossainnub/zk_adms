import frappe
import unittest
from zk_adms.api import get_or_create_device, process_attendance_data

class TestZKTECOAPI(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
	
	def test_device_creation(self):
		"""Test device auto-creation"""
		sn = "TEST123456"
		device = get_or_create_device(sn)
		self.assertEqual(device.serial_number, sn)
		self.assertEqual(device.status, "Online")
	
	def test_attendance_processing(self):
		"""Test attendance data processing"""
		sn = "TEST123456"
		test_data = "001\t2024-01-01 09:00:00\t0\t1\n002\t2024-01-01 18:00:00\t1\t1"
		
		# This would require an employee with device_user_id = "001"
		process_attendance_data(sn, test_data)
		
		# Check if ZK Log entries were created
		logs = frappe.get_all("ZK Log", filters={"device_serial": sn})
		self.assertEqual(len(logs), 2)