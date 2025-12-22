// Copyright (c) 2021, Farouk Muharram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delay Penalty', {
	get_employee: function(frm){
		    
		frm.events.fill_employee(frm);
	},
	fill_employee: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_employee',
			freeze:true,
			callback: function(r) {
				if (r.docs[0].employees){
					frm.save();
					frm.refresh_fields();
				 }
			} 
			
		})
	},

});

frappe.ui.form.on("Delay Penalty Employee", {
	salary_component: function(frm, cdt, cdn) {
		cur_frm.cscript.update_row_amount(frm, cdt, cdn);
	},
	hours: function(frm, cdt, cdn) {
		cur_frm.cscript.update_row_amount(frm, cdt, cdn);
	},
});

cur_frm.cscript.update_row_amount = function(frm, cdt, cdn){
	var u = locals[cdt][cdn];

	if (u.employee && u.salary_component && u.hours > 0){
		frappe.call({
			method: "pav_hr.pav_hr.doctype.delay_penalty.delay_penalty.get_amount",
			freeze:true,
			args: {
				'hours': u.hours,
				"employee": u.employee,
			},
			callback: function(msg) {
				if (msg.message){
					frappe.model.set_value(u.doctype, u.name, "amount", msg.message);
				}
			}
		});
	}

}
