// Copyright (c) 2023, hr and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Employee Scorecard Template', {
// Copyright (c) 2022, Partner and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Scorecard Template', {

	setup: function(frm) {
		frm.set_query("kpi", "job_performance", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['category', '=' ,'Job Performance KPI']
				]
			};
		});
		frm.set_query("kpi", "execution_of_instructions", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['category', '=' ,'Execution of instructions KPI']
				]
			};
		});
		frm.set_query("kpi", "personal_qualities", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['category', '=' ,'Personal qualities KPI']
				]
			};
		});
	},

	
// Personal qualities KPI
});
