# Copyright (c) 2022, Partner and contributors
# For license information, please see license.txt

from wsgiref import validate
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate , get_last_day

class EmployeeScorecard(Document):
	def on_submit(self):
		self.validate_grade()

	def validate(self):
		self.validate_ranges()
		self.validate_dates()
		self.validate_grade()
		

	def validate_ranges(self):
		self.total_resualt = 0
		job_performance = 0
		execution_of_instructions = 0
		personal_qualities = 0
		for i in self.get("job_performance"):
			job_performance =  job_performance  + i.current_score
			if flt(i.current_score) > flt(i.max_score):
				frappe.throw(_("Job Performance Table <br> Row {0}# Current Score {1} Could not be greater than Max Score {2}").format(flt(i.idx) ,flt(i.current_score) , flt(i.max_score)))
		self.total_job_performance = job_performance
		self.total_resualt = self.total_resualt + job_performance
		for i in self.get("execution_of_instructions"):
			execution_of_instructions =  execution_of_instructions  + i.current_score
			if flt(i.current_score) > flt(i.max_score):
				frappe.throw(_("Job Performance Table <br> Row {0}# Current Score {1} Could not be greater than Max Score {2}").format(flt(i.idx) ,flt(i.current_score) , flt(i.max_score)))
		self.total_execution_of_instructions = execution_of_instructions
		self.total_resualt = self.total_resualt + execution_of_instructions
		for i in self.get("personal_qualities"):
			personal_qualities =  personal_qualities  + i.current_score
			if flt(i.current_score) > flt(i.max_score):
				frappe.throw(_("Job Performance Table <br> Row {0}# Current Score {1} Could not be greater than Max Score {2}").format(flt(i.idx) ,flt(i.current_score) , flt(i.max_score)))
		self.total_personal_qualities = personal_qualities
		self.total_resualt = self.total_resualt + personal_qualities

	def validate_grade(self):
		if 50 >= flt(self.total_resualt) >= 0:
			self.grade = "Weak"
		elif 64 >= flt(self.total_resualt) >= 51:
			self.grade = "Average"
		elif 74 >= flt(self.total_resualt) >= 65:
			self.grade = "Good"
		elif 90 >= flt(self.total_resualt) >= 75:
			self.grade = "Very Good"
		elif 100 >= flt(self.total_resualt) >= 91:
			self.grade = "Excellent"
		elif  (flt(self.total_resualt) > 100):
				frappe.throw(_("Total Result = {0} , It must be less than 100 ").format(flt(self.total_resualt)))

	def validate_dates(self):
		months = {
			"Jan": '01',
			"Feb": '02',
			"Mar": '03',
			"Apr": '04',
			"May": '05',
			"Jun": '06',
			"Jul": '07',
			"Aug": '08',
			"Sep": '09',
			"Oct": '10',
			"Nov": '11',
			"Dec": '12'
		}
		if self.month and self.year:
			# if not self.from_date:
				self.from_date=getdate(self.year+'-'+months[self.month]+'-01')
			# if not self.to_date:
				self.to_date=get_last_day(self.from_date)
				
	def get_employee_programs(self):
		program_list = frappe.db.sql("""" 
		select parent
		from `tabHR Training Employee`
		where 
		employee =%s
		""",self.employee)
		return program_list


@frappe.whitelist()
def fetch_employee_scorecard_template(source_name, target_doc=None):
	target_doc = get_mapped_doc("Employee Scorecard Template", source_name, {

		"Employee Scorecard Template": {
			"doctype": "Employee Scorecard",
			"field_map": {
				"job_performance": "job_performance",
				"execution_of_instructions": "execution_of_instructions",
				"personal_qualities": "personal_qualities"
			}
		}
	}, target_doc)

	return target_doc






	