import frappe
from frappe.model.document import Document

class AttendanceDevice(Document):
	def before_save(self):
		if not self.device_name:
			self.device_name = f"ZKTeco Device {self.serial_number}"