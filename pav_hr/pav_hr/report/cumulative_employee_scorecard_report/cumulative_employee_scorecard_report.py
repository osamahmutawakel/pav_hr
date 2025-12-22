# Copyright (c) 2022, Partner and contributors
# For license information, please see license.txt

# from msilib.schema import Condition
# from asyncio.windows_events import NULL
import frappe
from frappe import _
from frappe.utils import flt
import erpnext


def execute(filters=None):
	if not filters: filters = {}
	conditions, filters = get_conditions(filters)
	columns = get_columns(filters,conditions)
	data = get_data(conditions,filters)
	if not data:
		return columns, [], None, None
	# frappe.throw(_(get_months(conditions,filters)))
	return columns, data
	
def get_columns(filters=None,conditions=None):
	columns= [
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::140",
		_("Employee Scorecard Template") + ":Link/Employee Scorecard Template:200",
		_("Employment Type") + ":Link/Employment Type:120",
		_("Branch") + ":Link/Branch:120",
		_("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120",
		# _("Job Performance") + "::60",
		# _("Execution of instructions") + "::60",
		# _("Personal qualities") + "::60",
	]
	month_year = get_months(conditions,filters)
	if month_year:
		for i in month_year:
			columns.append(_(i['month']+' '+i['year']) + "::60")

	columns.append(_("Total Resualt") + "::60")
	columns.append(_("Grade")  + "::150")

	return columns


def get_conditions(filters):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "and docstatus = {0}".format(doc_status[filters.get("docstatus")])
	if filters.get("from_date"): conditions += " and from_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and to_date <= %(to_date)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	if filters.get("branch"): conditions += " and branch = %(branch)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	if filters.get("employment_type"): conditions += " and employment_type = %(employment_type)s"
	if filters.get("employee_scorecard_template"): conditions += " and employee_scorecard_template = %(employee_scorecard_template)s"

	return conditions, filters

def get_emp_scorecard(employee,conditions,filters):
		filters["employee"] = employee
		conditions += " and employee = %(employee)s"
		map = frappe.db.sql(""" select
	 	employee  , month  , year , total_resualt
		from `tabEmployee Scorecard`  where 1=1 %s  """ % conditions, filters , as_dict=1)

		return map
		
def get_data(conditions,filters):

	data = frappe.db.sql("""select AVG(total_job_performance) as job_performance,
	 AVG(total_execution_of_instructions) as execution_of_instructions,
	AVG(total_personal_qualities) as personal_qualities  ,
	AVG(total_resualt) as total_resualt  ,
	 employee  , employee_name  , employee_scorecard_template
	, branch , department , employment_type , designation
	from `tabEmployee Scorecard`  where 1=1 %s  Group by employee""" % conditions, filters , as_dict=1)
	month_year = get_months(conditions,filters)

	for d in data:
		for k in month_year:
			map = get_emp_scorecard(d['employee'],conditions,filters)
			for n in map:
				if k['month'] == n['month'] and k['year'] == n['year']:
					d[str(k['month']+"_"+k['year']).lower()] = n["total_resualt"]
				# else:
				# 	d[str(k['month']+"_"+k['year']).lower()] = "NULL"
	for i in data:
		i['grade'] = validate_grade(i['total_resualt'])

	return data

def get_months(conditions,filters):
	months = frappe.db.sql("""select DISTINCT month , year
	from `tabEmployee Scorecard`  where 1=1 %s Order by from_date """ % conditions, filters , as_dict=1)
	# new_list = {}
	# # for i in months:
	# # 	new_list.append(str(i['month']) + '-' + str(i['year']))
	return months


def validate_grade(total_resualt):
	if 50 >= flt(total_resualt) >= 0:
		grade = "Weak"
	elif 64 >= flt(total_resualt) >= 51:
		grade = "Average"
	elif 74 >= flt(total_resualt) >= 65:
		grade = "Good"
	elif 90 >= flt(total_resualt) >= 75:
		grade = "Very Good"
	elif 100 >= flt(total_resualt) >= 91:
		grade = "Excellent"
	
	return grade
	