// Copyright (c) 2022, Partner and contributors
// For license information, please see license.txt
// var added_row = null;

frappe.ui.form.on('Employee Scorecard', {

	setup: function(frm){
		frm.get_field("job_performance").grid.cannot_add_rows = true;
		frm.set_df_property('job_performance', 'cannot_delete_rows', 1);
		frm.get_field("execution_of_instructions").grid.cannot_add_rows = true;
		frm.set_df_property('execution_of_instructions', 'cannot_delete_rows', 1);
		frm.get_field("personal_qualities").grid.cannot_add_rows = true;
		frm.set_df_property('personal_qualities', 'cannot_delete_rows', 1);
	
		
		// frm.set_query("kpi", "job_performance", function(doc, cdt, cdn) {
		// 	let d = locals[cdt][cdn];
		// 	return {
		// 		filters: [
		// 			['category', '=' ,'Job Performance KPI']
		// 		]
		// 	};
		// });
		// frm.set_query("kpi", "execution_of_instructions", function(doc, cdt, cdn) {
		// 	let d = locals[cdt][cdn];
		// 	return {
		// 		filters: [
		// 			['category', '=' ,'Execution of instructions KPI']
		// 		]
		// 	};
		// });
		// frm.set_query("kpi", "personal_qualities", function(doc, cdt, cdn) {
		// 	let d = locals[cdt][cdn];
		// 	return {
		// 		filters: [
		// 			['category', '=' ,'Personal qualities KPI']
		// 		]
		// 	};
		// });
		// frm.set_query("employee_scorecard_template",function(){
		// 	return {
		// 		filters:{
		// 			"docstatus": 1
		// 		}
		// 	}
		// });
		frm.set_query("reference",function(){
			return {
				filters:{
					"docstatus": 1
				}
			}
		});
		
	},
	employee:function(frm){
		frappe.call({
			method: "frappe.client.get_value",
			args:{
				doctype: "Employee",
				filters: {"name": frm.doc.employee},
				fieldname: "scorecard_template"
			},
			callback:function(x) {
				if(x && x.message.scorecard_template){
					frm.set_value("employee_scorecard_template", x.message.scorecard_template);
				
				}
				  else{
				  frm.set_value("employee_scorecard_template",'');
				}
			}
		});
	},
	employee_scorecard_template: function(frm) {

		erpnext.utils.map_current_doc({
			method: "pav_hr.pav_hr.doctype.employee_scorecard.employee_scorecard.fetch_employee_scorecard_template",
			source_name: frm.doc.employee_scorecard_template,
			frm: frm
		});
		
	}
});

frappe.ui.form.on('Employee Scorecard Details', {
	refresh(frm) {
		// your code here
	},
	current_score:function(frm,cdt,cdn){
	    var row = locals[cdt][cdn];
	    if(row.current_score > row.max_score){
	        frappe.msgprint("<b>Current Score</b> for row <b>"+row.idx+"</b> must be less than <b>"+row.max_score+"</b>");
	        frappe.model.set_value(cdt, cdn,"current_score",0);
	    }
	    
	}
})




