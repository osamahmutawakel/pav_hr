// Copyright (c) 2022, Partner and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Scorecard', {

	setup: function(frm){
		frm.get_field("job_performance").grid.cannot_add_rows = true;
		frm.set_df_property('job_performance', 'cannot_delete_rows', 1);
		frm.get_field("execution_of_instructions").grid.cannot_add_rows = true;
		frm.set_df_property('execution_of_instructions', 'cannot_delete_rows', 1);
		frm.get_field("personal_qualities").grid.cannot_add_rows = true;
		frm.set_df_property('personal_qualities', 'cannot_delete_rows', 1);

		frm.set_query("reference", function(){
			return {
				filters: {
					"docstatus": 1
				}
			};
		});
	},

	employee: function(frm){
		if (!frm.doc.employee) return;

		// جلب قالب التقييم المحدد للموظف
		frappe.db.get_value("Employee", frm.doc.employee, "scorecard_template")
			.then(r => {
				if (r && r.message && r.message.scorecard_template) {
					frm.set_value("employee_scorecard_template", r.message.scorecard_template);
				} else {
					frm.set_value("employee_scorecard_template", '');
				}
			});
	},

	employee_scorecard_template: function(frm) {
		if (!frm.doc.employee_scorecard_template) {
			// تفريغ الجداول في حال تم مسح القالب
			frm.clear_table("job_performance");
			frm.clear_table("execution_of_instructions");
			frm.clear_table("personal_qualities");
			frm.refresh_fields(["job_performance", "execution_of_instructions", "personal_qualities"]);
			return;
		}

		frappe.call({
			method: "pav_hr.pav_hr.doctype.employee_scorecard.employee_scorecard.fetch_employee_scorecard_template",
			args: {
				source_name: frm.doc.employee_scorecard_template
			},
			callback: function(r) {
				if (r.message) {
					// تفريغ الجداول القديمة وتعبئتها من القالب دون المساس بالموظف
					frm.clear_table("job_performance");
					frm.clear_table("execution_of_instructions");
					frm.clear_table("personal_qualities");

					const tables = ["job_performance", "execution_of_instructions", "personal_qualities"];
					tables.forEach(table_field => {
						if (r.message[table_field]) {
							r.message[table_field].forEach(row => {
								let child = frm.add_child(table_field);
								Object.assign(child, row);
								delete child.name; // لضمان توليد اسم فريد جديد للصف
							});
						}
					});

					frm.refresh_fields(tables);
				}
			}
		});
	}
});

frappe.ui.form.on('Employee Scorecard Details', {
	current_score: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(flt(row.current_score) > flt(row.max_score)){
			frappe.msgprint(__("<b>Current Score</b> for row <b>{0}</b> must be less than <b>{1}</b>", [row.idx, row.max_score]));
			frappe.model.set_value(cdt, cdn, "current_score", 0);
		}
	}
});
