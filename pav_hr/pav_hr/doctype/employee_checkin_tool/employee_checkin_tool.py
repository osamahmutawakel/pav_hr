# Copyright (c) 2022, Farouk Muharram and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta, datetime

class EmployeeCheckinTool(Document):
	def on_submit(self):
		self.employee_chechin()


	def employee_chechin(self):		
		start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
		end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
		delta = end_date - start_date 
		
		temp= filter(None, self.time_in.split(":"))
		in_time = list(temp)

		temp= filter(None, self.time_out.split(":"))
		out_time = list(temp)

		for i in range(delta.days + 1):
			date = start_date + timedelta(days=i)
			in_date = date.replace(hour=int(in_time[0]), minute=int(in_time[1]))
			out_date = date.replace(hour=int(out_time[0]), minute=int(out_time[1]))
			for emp in self.employee_checkin_tool_employee:
				args = frappe._dict({
				"doctype": "Employee Checkin",
				"employee": emp.employee,
				"employee_name": emp.employee_name,
				"shift": self.shift,
				})
				todo = frappe.get_doc(args)
				todo.time = in_date
				todo.log_type = 'IN'
				todo.insert()
				todo = frappe.get_doc(args)
				todo.time = out_date
				todo.log_type = 'OUT'
				todo.insert()

@frappe.whitelist()
def get_time(shift, half_day):
	half_day = int(half_day)
	times = frappe.db.get_value('Shift Type', shift, ['start_time', 'end_time'], as_dict = 1)
	if half_day and half_day == 1:
		times.end_time = times.start_time + timedelta(hours=2, minutes=30)
	return times

@frappe.whitelist()
def get_employee(department = None):
	employees = []
	if department:
		employees = frappe.db.get_list('Employee', {'department': department}, ['name', 'employee_name'])
	else:
		employees = frappe.db.get_list('Employee', fields= ['name', 'employee_name'])
	return employees