import frappe

def after_install():
	"""Run after app installation"""
	fix_employee_image_field()
	create_custom_fields()
	frappe.db.commit()

def fix_employee_image_field():
	"""Fix Employee image field list view issue"""
	try:
		# Check if image field has in_list_view enabled
		if frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": "image"}):
			image_field = frappe.get_doc("Custom Field", {"dt": "Employee", "fieldname": "image"})
			if image_field.in_list_view:
				image_field.in_list_view = 0
				image_field.save(ignore_permissions=True)
	except Exception:
		pass

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