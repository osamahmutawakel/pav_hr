// Copyright (c) 2022, Farouk Muharram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Checkin Tool', {
	refresh: function(frm) {
		if(frm.doc.__islocal){
			frm.trigger('half_day');
		}
	},
	half_day: function(frm) {
		if(frm.doc.shift){
			frappe.call({
				method: "pav_hr.pav_hr.doctype.employee_checkin_tool.employee_checkin_tool.get_time",
				args: {
					shift: frm.doc.shift, 
					half_day: frm.doc.half_day
				},
				freeze: true,
				callback: function(r) {
					frm.set_value('time_in', r.message.start_time);
					frm.set_value('time_out', r.message.end_time);

				}
			})
		}
	},
	get_employee: function(frm) {
		frappe.call({
			method: "pav_hr.pav_hr.doctype.employee_checkin_tool.employee_checkin_tool.get_employee",
			freeze:true,
			args: {department: frm.doc.department},
			callback: function(r) {
				console.log(r.message);
				r.message.forEach(element => {
					let new_row = frm.add_child("employee_checkin_tool_employee");
					new_row.employee = element["name"];
					new_row.employee_name = element["employee_name"];
				});
				frm.refresh_field("employee_checkin_tool_employee");
			} 
			
		})
	}
	
});
