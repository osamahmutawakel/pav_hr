# -*- coding: utf-8 -*-
# Copyright (c) 2021, Farouk Muharram and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, getdate
from pav_hr.pav_hr.report.cumulative_attendance_report_with_ot.cumulative_attendance_report_with_ot import execute
from datetime import timedelta
from frappe.utils import getdate
from datetime import datetime


class DelayPenalty(Document):
	# def autoname(self):
	# 	from_date = formatdate(get_datetime_str(self.from_date), "yyyy-MM-dd")
	# 	to_date = formatdate(get_datetime_str(self.to_date), "yyyy-MM-dd")
	# 	self.name = "{}/{}".format(from_date, to_date)

	def before_submit(self):
		self.approve_disciplinary()
	
	def before_cancel(self):
		self.approve_disciplinary(submit=False)


	def approve_disciplinary(self, submit = True):
		for emp in self.get("employees"):
			# if emp.salary_component and (emp.hours > 0 or emp.absent_days > 0):
			# 	self.add_salaray(emp, submit)
			if emp.days_count > 0:
				self.create_ledger(emp, submit)
			

	def add_salaray(self, emp, submit = True):
		sal = frappe._dict(
			doctype='Additional Salary',
			employee=emp.employee,
			employee_name=emp.employee_name,
			salary_component=emp.salary_component,
			amount=emp.amount,
			payroll_date=self.from_date,
			delay_penalty=self.name,
		)

		if submit:
			frappe.get_doc(sal).submit()
		else:
			sals = frappe.get_list("Additional Salary", {"delay_penalty": self.name})
			for sal in sals:
				sal = frappe.get_doc('Additional Salary', sal.name)
				sal.cancel()
				sal.delete()
		self.update_salary_slip()


	def create_ledger(self, emp, submit = True):
		from hrms.hr.doctype.leave_application.leave_application import get_number_of_leave_days
		from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
		d1 = getdate(self.from_date)
		to = d1 + timedelta(days = emp.days_count)
		days = get_number_of_leave_days(emp.employee, self.leave_type, d1, to)
		while emp.days_count > days:
			to = to + timedelta(days = 1)
			days = get_number_of_leave_days(emp.employee, self.leave_type, d1, to)
				
		lwp = frappe.db.get_value("Leave Type", self.leave_type, "is_lwp")
		ledger = frappe._dict(
			doctype='Leave Ledger Entry',
			employee=emp.employee,
			employee_name=emp.employee_name,
			leave_type= self.leave_type,
			transaction_type= 'Leave Application',
			leaves=emp.days_count * -1,
			from_date=self.from_date,
			to_date=to,
			is_lwp=lwp,
			holiday_list=get_holiday_list_for_employee(emp.employee),
			is_carry_forward=0,
			is_expired=0,
			delay_penalty=self.name,
		)
		
		if submit:
			frappe.get_doc(ledger).submit()
		else:
			sals = frappe.get_list("Leave Ledger Entry", {"delay_penalty": self.name})
			for sal in sals:
				sal = frappe.get_doc('Leave Ledger Entry', sal.name)
				sal.is_expired = True
				sal.cancel()
				sal.delete()
	
	def update_salary_slip(self):
		for emp in self.get("employees"):
			if emp.salary_component and emp.hours > 0:
				doc = frappe.db.sql("""select name from `tabSalary Slip` where docstatus = 0 and employee =%s and payroll_entry = %s
				ORDER BY posting_date DESC LIMIT 1 """, [emp.employee, self.payroll_entry], as_dict=1)
				if doc:
					doc = frappe.get_doc('Salary Slip', doc[0]['name'])
					doc.validate()
					doc.save()

	@frappe.whitelist()
	def fill_employee(self):
		self.employees = None
		emps = self.get_employees()
	
	def get_employees(self):
		filters = {'from': self.from_date, 'to':self.to_date}
		f, emps = execute(filters)
		# leave_filters = LeaveFilters(self.from_date, self.to_date)
		leave_filters = frappe._dict(filters)
		attendance_list = get_attendance_list(leave_filters)
		in_active_emps=""
		for emp in emps:
			if emp and frappe.get_value("Employee",emp['name'],"status") != "Active":
				in_active_emps+="<b>"+emp['name']+"-"+emp['employee']+"</b><br>"
				continue
			if emp and emp['late_total'] and (int(emp['late_total'].split(':')[0]) >= 1 or int(emp['late_total'].split(":")[1]) >= 1):


				emp_atds=get_attendance_records(emp['name'],self.from_date,self.to_date)
					
				# frappe.msgprint(str(emp_atds))

				total_days_z=0
				total_hours_z=0.0
				late_hours="0:0:0"
				for atd in emp_atds :
					if atd.status == "Absent":
						total_days_z += 1	
					if atd.status == "Present" :
						filters_d = {'from': atd.attendance_date, 'to':atd.attendance_date,'employee':atd.employee}
						cumu= execute(filters_d)
						hours_cal=cumu[1][0]
						hours_cal=hours_cal['late_total'] if hours_cal and hours_cal['late_total'] is not None else "0:0:0"
						hh = flt(flt(hours_cal.split(":")[0])*60) +  flt(hours_cal.split(":")[1]) + flt(flt(hours_cal.split(":")[2])/60) 
						total_hours_z +=  hh 


				if total_hours_z< 60:
					total_hours_z=0.0

				if total_days_z >0 or total_hours_z > 60:		
					emp_last_gross_pay = get_employee_det(emp['name'])
					row = self.append('employees', {})
					row.employee = emp['name']
					row.employee_name = emp['employee']
					row.salary_component = self.salary_component
					
					row.last_gross_pay = flt(emp_last_gross_pay[0]["gross_pay"]) if len(emp_last_gross_pay) else 1222
					row.last_gross_pay_day = flt(emp_last_gross_pay[0]["gross_pay"] / 30) if len(emp_last_gross_pay) else 1222
					row.last_gross_pay_mint = flt(emp_last_gross_pay[0]["gross_pay"] / 30 / 6 / 60) if len(emp_last_gross_pay) else 1222
					
					
					row.late_hours =convert_minutes_to_hours(int(total_hours_z))

					# total_a = 0.0
					row.absent_days=total_days_z
					row.hours=total_hours_z
					row.hour_amount = flt(row.hours * row.last_gross_pay_mint , 2)
					row.absent_days_amount = flt(row.absent_days * row.last_gross_pay_day , 2) 
					row.amount = flt(row.hour_amount + row.absent_days_amount , 2)
		
		if in_active_emps != "":
			frappe.msgprint("You can't create Penalty for in-active employees:<br>"+in_active_emps)
				#get absent count from attendance_list
		
def convert_minutes_to_hours(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    seconds = 0

    time_string = f"{hours}:{remaining_minutes:02d}:{seconds}"

    return time_string				
def get_attendance_records(employee, from_date, to_date):
    sql_query = """
        SELECT employee, attendance_date, status
        FROM tabAttendance
        WHERE docstatus = 1 AND attendance_date >= %(from)s AND attendance_date <= %(to)s
        AND employee = %(employee)s
        ORDER BY employee, attendance_date
    """

    filters = {
        "from": from_date,
        "to": to_date,
        "employee": employee
    }

    records = frappe.db.sql(sql_query, filters, as_dict=True)

    return records				

def get_attendance_list(filters):
	attendance_list = frappe.db.sql("""select employee, attendance_date,
		status from tabAttendance 
		where docstatus = 1 and attendance_date >= %(from)s and attendance_date <= %(to)s
		order by employee, attendance_date""", filters, as_dict=1)

	att = {}
	for d in attendance_list:
		att.setdefault(d.employee, [])
		att[d.employee].append(d.status)

	return att

class LeaveFilters:
  def __init__(self, from_date, to_date):
    self.from_date = from_date
    self.to_date = to_date

def get_employee_det(emp):
	# """
	# select {field} from `tabSalary Structure Assignment`
	# where employee =%s ORDER BY from_date DESC LIMIT 1
	# """.format(field=field), emp, as_dict=1)
	return frappe.db.sql(
		"""
		select gross_pay from `tabSalary Slip`
		where employee =%s ORDER BY start_date DESC LIMIT 1
		""", emp, as_dict=1)

@frappe.whitelist()
def get_amount(employee, hours):
	emp_det = get_employee_det(employee)
	frappe.msgprint("123")
	if emp_det:
		hour_rate_per_salary = flt((emp_det[0]["gross_pay"] / 30 / 6 / 60))
		return flt((hour_rate_per_salary * flt(hours)), 2)
