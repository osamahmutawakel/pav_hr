# Copyright (c) 2022, Partner and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, get_last_day


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
			job_performance += flt(i.current_score)
			if flt(i.current_score) > flt(i.max_score):
				frappe.throw(
					_("Job Performance Table <br> Row #{0}: Current Score {1} cannot be greater than Max Score {2}").format(
						i.idx, flt(i.current_score), flt(i.max_score)
					)
				)
		self.total_job_performance = job_performance
		self.total_resualt += job_performance

		for i in self.get("execution_of_instructions"):
			execution_of_instructions += flt(i.current_score)
			if flt(i.current_score) > flt(i.max_score):
				frappe.throw(
					_("Execution of Instructions Table <br> Row #{0}: Current Score {1} cannot be greater than Max Score {2}").format(
						i.idx, flt(i.current_score), flt(i.max_score)
					)
				)
		self.total_execution_of_instructions = execution_of_instructions
		self.total_resualt += execution_of_instructions

		for i in self.get("personal_qualities"):
			personal_qualities += flt(i.current_score)
			if flt(i.current_score) > flt(i.max_score):
				frappe.throw(
					_("Personal Qualities Table <br> Row #{0}: Current Score {1} cannot be greater than Max Score {2}").format(
						i.idx, flt(i.current_score), flt(i.max_score)
					)
				)
		self.total_personal_qualities = personal_qualities
		self.total_resualt += personal_qualities

	def validate_grade(self):
		res = flt(self.total_resualt)
		if res < 0:
			frappe.throw(_("Total Result cannot be negative."))
		elif res <= 50:
			self.grade = "Weak"
		elif res <= 64:
			self.grade = "Average"
		elif res <= 74:
			self.grade = "Good"
		elif res <= 90:
			self.grade = "Very Good"
		elif res <= 100:
			self.grade = "Excellent"
		else:
			frappe.throw(_("Total Result = {0}, it must be less than or equal to 100.").format(res))

	def validate_dates(self):
		months = {
			"Jan": "01",
			"Feb": "02",
			"Mar": "03",
			"Apr": "04",
			"May": "05",
			"Jun": "06",
			"Jul": "07",
			"Aug": "08",
			"Sep": "09",
			"Oct": "10",
			"Nov": "11",
			"Dec": "12",
		}
		if self.month and self.year:
			self.from_date = getdate(f"{self.year}-{months[self.month]}-01")
			self.to_date = get_last_day(self.from_date)

	def get_employee_programs(self):
		program_list = frappe.db.sql(
			"""
			select parent
			from `tabHR Training Employee`
			where employee = %s
			""",
			self.employee,
		)
		return program_list


@frappe.whitelist()
def fetch_employee_scorecard_template(source_name):
	template = frappe.get_doc("Employee Scorecard Template", source_name)
	return {
		"job_performance": [d.as_dict() for d in template.get("job_performance", [])],
		"execution_of_instructions": [d.as_dict() for d in template.get("execution_of_instructions", [])],
		"personal_qualities": [d.as_dict() for d in template.get("personal_qualities", [])],
	}

	return target_doc
