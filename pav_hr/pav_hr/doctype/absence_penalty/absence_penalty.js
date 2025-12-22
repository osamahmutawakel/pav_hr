// Copyright (c) 2022, Farouk Muharram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Absence Penalty', {
	refresh(frm){
		frm.set_query("salary_component", function() {
			return {
				filters: {
					"type": 'Deduction'
				}
			}
		});
	},
	get_employee: function(frm){
		frm.events.get_absence_penalty(frm);
	},
	get_absence_penalty: function (frm) {
		 if (frm.doc.shift_type, frm.doc.company, frm.doc.from_date, frm.doc.to_date){
			frm.clear_table('absence_penalty_employee');
			frappe.call({
				doc: frm.doc,
				method: 'get_absence_penalty',
				freeze:true,
				callback: function(r) {
					if (r.docs[0].absence_penalty_employee){
						frm.save();
						frm.refresh_fields();
					
					 }
				} 
				
			})
		 }
	},

});