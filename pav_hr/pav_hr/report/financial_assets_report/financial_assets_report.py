,# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_column(filters)
	data = []
	cond = ""
	if filters.get("item_code"):
		cond +=' and a.item_code= %(item_code)s' 
	if filters.get("asset_name"):
		cond +=' and a.asset_name= %(asset_name)s' 
	if filters.get("custodian"):
		cond +=' and a.custodian= %(custodian)s'
	if filters.get("asset_category"):
		cond +=' and a.asset_category= %(asset_category)s'
	if filters.get("location"):
		cond +=' and a.location= %(location)s'
	if filters.get("department"):
		cond +=' and a.department= %(department)s'

	data=frappe.db.sql("""
	    select
			*, IF(`p`.`currency` = "YER", 0, `pi`.`rate`) as `rate` 
		from
			`tabAsset` AS `a`
		LEFT JOIN
			`tabPurchase Invoice` AS `p`
		ON
			`p`.`name` = `a`.`purchase_invoice`
		Inner JOIN
			`tabPurchase Invoice Item` AS `pi`
		ON
			`pi`.`parent` = `p`.`name`
		WHERE 
			`a`.`purchase_date` BETWEEN %(from_date)s AND %(to_date)s AND a.docstatus = 1 AND p.docstatus = 1 AND `pi`.`item_code` = `a`.`item_code`
		
			{0}
		""".format(cond), filters, as_dict=True, debug=1)

	data2=frappe.db.sql("""
	    select
			*, IF(`p`.`currency` = "YER", 0, `pi`.`rate`) as `rate` 
		from
			`tabAsset` AS `a`
		LEFT JOIN
			`tabPurchase Receipt` AS `p`
		ON
			`p`.`name` = `a`.`purchase_invoice`
		Inner JOIN
			`tabPurchase Receipt Item` AS `pi`
		ON
			`pi`.`parent` = `p`.`name`
		WHERE 
			`a`.`purchase_date` BETWEEN %(from_date)s AND %(to_date)s AND a.docstatus = 1 AND p.docstatus = 1		
		
			{0}
		""".format(cond), filters, as_dict=True, debug=1)
	data.extend(data2)
	return columns, data
	
def get_column(filters):
	columns = [
	
		
		{
			"fieldname":"item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",

		},
		{
			"fieldname":"asset_name",
			"label": _("Asset Name"),
			"fieldtype": "Link",
			"options": "Asset",

		},
		{
			"fieldname":"purchase_invoice",
			"label": _("Purchase Invoice"),
			"fieldtype": "Link",
			"options": "Purchase Invoice",

		},
		{
			"fieldname":"employee_name",
			"label": _("Employee Name"),
			"fieldtype": "Data",

		},
		{
			"fieldname":"asset_category",
			"label": _("Asset Category"),
			"fieldtype": "Link",
			"options": "Asset Category",

		},
		{
			"fieldname":"location",
			"label": _("Location"),
			"fieldtype": "Link",
			"options": "Location",

		},
		{
			"fieldname":"department",
			"label": _("Department"),
			"fieldtype": "Link",
			"options": "Department",

		},
		{
			"fieldname":"gross_purchase_amount",
			"label": _("ِAsset Gross Purchase Amount"),
			"fieldtype": "Currency",
		},
		{
			"fieldname":"net_rate",
			"label": _("Purchase Amount USD"),
			"fieldtype": "Currency",
		},
		{
			"fieldname":"base_net_rate",
			"label": _("Purchase Amount YER"),
			"fieldtype": "Currency",
		},


	]
	

	return columns

	
	
	
	
	
	
