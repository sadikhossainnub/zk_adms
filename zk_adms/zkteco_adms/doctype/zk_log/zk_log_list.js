frappe.listview_settings['ZK Log'] = {
	add_fields: ["processed", "punch_type"],
	get_indicator: function(doc) {
		if (doc.processed) {
			return [__("Processed"), "green", "processed,=,1"];
		} else {
			return [__("Pending"), "orange", "processed,=,0"];
		}
	}
};