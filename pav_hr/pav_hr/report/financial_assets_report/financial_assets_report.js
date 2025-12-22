// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Financial Assets Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1 ,
	 		"default": frappe.datetime.month_start()
	 	},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_end(),
		},
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",

		},
		{
			"fieldname":"asset_name",
			"label": __("Asset Name"),
			"fieldtype": "Link",
			"options": "Asset",

		},
		{
			"fieldname":"custodian",
			"label": __("Custodian"),
			"fieldtype": "Link",
			"options": "Employee",

		},
		{
			"fieldname":"asset_category",
			"label": __("Asset Category"),
			"fieldtype": "Link",
			"options": "Asset Category",

		},
		{
			"fieldname":"location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "Location",

		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",

		},
	],

	// "formatter": function (value, row, column, data, default_formatter) {
	// 	//value = $(`<span style='font-weight:bold'>${value}</span>`);
	// 	value = default_formatter(value, row, column, data);

	// 	// if (column.fieldname == "asset_name" ) 
	// 	// {
	// 	// console.log(data.in_iime );
	// 	// debugger;
	// 		if (data.gross_purchase_amount != base_net_rate) 
	// 		{
	// 				value = "<span style='background-color: #e12b2b; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
	// 		}
	// 	// }
		// return value;

		// 	}
};

