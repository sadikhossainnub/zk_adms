import frappe

def after_install():
	"""Run after app installation"""
	create_custom_fields()
	frappe.db.commit()

def create_custom_fields():
	"""Create custom fields for Employee doctype"""
	if not frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": "device_user_id"}):
		custom_field = frappe.new_doc("Custom Field")
		custom_field.dt = "Employee"
		custom_field.fieldname = "device_user_id"
		custom_field.fieldtype = "Data"
		custom_field.label = "Device User ID"
		custom_field.insert_after = "employee_number"
		custom_field.description = "User ID from ZKTeco attendance device"
		custom_field.insert(ignore_permissions=True)