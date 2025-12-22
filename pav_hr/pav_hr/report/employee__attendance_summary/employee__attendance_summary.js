// Copyright (c) 2016, Farouk Muharram and contributors
// For license information, please see license.txt
/* eslint-disable  Employee  Attendance Summary*/
frappe.query_reports["Employee  Attendance Summary"] = {
	"filters": [

		{
			fieldname: 'employee',
			label: __('Employee'),
			fieldtype: 'Link',
			options: 'Employee'
		},
		{
			"fieldname":"start_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		}
		,
		{
			"fieldname":"group_by_emp",
			"label": __("group_by_emp"),
			"fieldtype": "Check",
			"default": false,
			"reqd": 0
		}
		,
	],
	  "formatter": function (value, row, column, data, default_formatter) {
		//value = $(`<span style='font-weight:bold'>${value}</span>`);
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "late_entry")
		{
			if (data.late_entry)
			{
				value = "<span style='background-color: #e12b2b; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}
		if (column.fieldname == "early_exit")
		{
			if (data.early_exit)
			{
				value = "<span style='background-color:#e12b2b; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}
		if (column.fieldname == "delay_total")
		{
			if (data.delay_total)
			{
				value = "<span style='background-color:#d00404; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}
		if (column.fieldname == "early_entry")
		{
			if (data.early_entry)
			{
				value = "<span style='background-color:#30b530; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}
		if (column.fieldname == "late_exit")
		{
			if (data.late_exit)
			{
				value = "<span style='background-color:#30b530; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}
		if (column.fieldname == "early_total")
		{
			if (data.early_total)
			{
				value = "<span style='background-color:green; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}





		if (column.fieldname == "max_over")
		{
			if (data.max_over && data.max_over!="Over Time Total" )
			{
				value = "<span style='background-color:#30b530;  color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}


		if (column.fieldname == "min_over")
		{
			if (data.min_over && data.min_over!="Over Time Total" )
			{
				value = "<span style='background-color:#30b530;  color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}


		if (column.fieldname == "workinghours")
		{
			if (data.workinghours)
			{
				value = "<span style='background-color:purple; color:white;'><b>&nbsp;" + value + "&nbsp;</b></span>";
			}
		}
		return value;
	}
};

