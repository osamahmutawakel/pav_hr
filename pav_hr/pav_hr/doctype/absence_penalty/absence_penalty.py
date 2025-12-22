# -*- coding: utf-8 -*-
# Copyright (c) 2022, Farouk Muharram and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt

class AbsencePenalty(Document):
	def before_submit(self):
		self.approve_disciplinary()
	
	def before_cancel(self):
		self.approve_disciplinary(submit=False)

	def approve_disciplinary(self, submit = True):
		for emp in self.get("absence_penalty_employee"):
			self.add_salaray(emp, submit)
			
	def add_salaray(self, emp, submit = True):
		sal = frappe._dict(
			doctype='Additional Salary',
			employee=emp.employee,
			employee_name=emp.employee_name,
			salary_component=self.salary_component,
			amount=emp.amount,
			payroll_date=self.from_date,
			absence_penalty=self.name,
		)

		if submit:
			frappe.get_doc(sal).submit()
		else:
			sals = frappe.get_list("Additional Salary", {"absence_penalty": self.name})
			for sal in sals:
				sal = frappe.get_doc('Additional Salary', sal.name)
				sal.cancel()
				sal.delete()

	@frappe.whitelist()
	def get_absence_penalty(self):
		from pav_hr.pav_hr.utils import get_penalty_minuts

		emp_filters = {'company': self.company, 'default_shift': self.shift_type, }
		emps = frappe.db.get_list("Employee", filters=emp_filters, fields=['name', 'employee_name', 'holiday_list', 'default_shift'],
		 order_by='name',)


		shift = frappe.get_doc("Shift Type", self.shift_type)
		if shift.penalty_enable == 0 or not shift.penalty_calculation:
			frappe.throw("Please set penalty enable and penalty calculation in Shift Type {0}".format(shift))

		filters = {'company': self.company, 'from': self.from_date, 'to': self.to_date}
		penalty_minuts_map = get_penalty_minuts(filters, emps, shift)
		

		for emp in emps:
			if penalty_minuts_map:
				m = penalty_minuts_map.get(emp.name, 0) 
				
				if m > 0:
					row = self.append('absence_penalty_employee', {})
					row.employee = emp['name']
					row.employee_name = emp['employee_name']
					minutes = penalty_minuts_map.get(emp.name, 0) 
					# row.penalty_hours = flt((minutes / 60), 2) if minutes > 0 else 0
					row.penalty_hours = flt((minutes / 60), 2) if minutes >= 60 else flt((minutes / 100), 2)
					row.amount = get_amount(emp['name'], minutes, 'base')

def get_amount(employee, minuts, field_name):
	from pav_hr.pav_hr.doctype.delay_penalty.delay_penalty import get_employee_det
	emp_det = get_employee_det(field_name, employee)
	if emp_det:
		hour_rate_per_salary = flt((emp_det[0][field_name] / 30 / 8 / 60))
		return flt((hour_rate_per_salary * flt(minuts)), 2)