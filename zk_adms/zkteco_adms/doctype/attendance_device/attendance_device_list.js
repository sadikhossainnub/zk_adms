frappe.listview_settings['Attendance Device'] = {
	add_fields: ["status", "last_sync_time"],
	get_indicator: function(doc) {
		if (doc.status === "Online") {
			return [__("Online"), "green", "status,=,Online"];
		} else {
			return [__("Offline"), "red", "status,=,Offline"];
		}
	}
};