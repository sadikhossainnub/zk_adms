import frappe

def execute():
    """Fix Employee image field in_list_view property"""
    try:
        # Check if Employee doctype exists
        if not frappe.db.exists("DocType", "Employee"):
            return
        
        # Get Employee meta
        meta = frappe.get_meta("Employee")
        
        # Find image field and fix in_list_view if needed
        for field in meta.fields:
            if field.fieldname == "image" and field.fieldtype == "Attach Image" and field.in_list_view:
                # Update the field to remove in_list_view
                frappe.db.sql("""
                    UPDATE `tabDocField` 
                    SET in_list_view = 0 
                    WHERE parent = 'Employee' 
                    AND fieldname = 'image' 
                    AND fieldtype = 'Attach Image'
                """)
                
                # Also check custom fields
                frappe.db.sql("""
                    UPDATE `tabCustom Field` 
                    SET in_list_view = 0 
                    WHERE dt = 'Employee' 
                    AND fieldname = 'image' 
                    AND fieldtype = 'Attach Image'
                """)
                
                frappe.db.commit()
                break
                
        frappe.clear_cache(doctype="Employee")
        
    except Exception as e:
        frappe.log_error(f"Error fixing Employee image field: {str(e)}")