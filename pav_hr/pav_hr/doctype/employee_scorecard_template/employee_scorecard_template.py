# Copyright (c) 2022, Partner and contributors
# For license information, please see license.txt

from wsgiref import validate
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate , get_last_day

class EmployeeScorecardTemplate(Document):
	def validate(self):
		
		self.validate_kpis()
		self.validate_total()

	def validate_total(self):
		if flt(self.total_of_max_scores_job_performance +
		self.total_of_max_scores_execution_of_instructions +
		self.total_of_max_scores_personal_qualities != 100):
			frappe.throw(_("Total of Max Scores must be equal to 100"))
		
	def validate_kpis(self):
		max_total = 0
		job_performance = 0
		execution_of_instructions = 0
		personal_qualities = 0

		for i in self.get("job_performance"):
			job_performance =  job_performance  + i.max_score
		self.total_of_max_scores_job_performance = job_performance

		for i in self.get("execution_of_instructions"):
			execution_of_instructions =  execution_of_instructions  + i.max_score
		self.total_of_max_scores_execution_of_instructions = execution_of_instructions
						
		for i in self.get("personal_qualities"):
			personal_qualities =  personal_qualities  + i.max_score
		self.total_of_max_scores_personal_qualities = personal_qualities
		

