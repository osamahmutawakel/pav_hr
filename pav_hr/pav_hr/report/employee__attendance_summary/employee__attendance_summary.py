
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (flt, cstr)
from datetime import datetime, timedelta, time
from pav.pav.report.cumulative_attendance_report_with_ot.cumulative_attendance_report_with_ot import get_shift, \
	convert_to_minutes

from hrms.hr.utils import get_holidays_for_employee

def delay(max, min):
	return max - min if max and min and max > min else None


def delayTotal(max, min):
	if max and min:
		return max + min
	elif max and not min:
		return max
	elif min and not max:
		return min


def execute(filters=None):
	if not filters: filters = {}
	formatted_data = []
	columns = get_columns()
	data = get_data(filters)
	shift = get_shift()

	t = timedelta(00, 00, 00)
	g_emp_total = timedelta(00, 00, 00)
	over_emp_total=timedelta(00,00,00)

	if filters.get("group_by_emp"):
		return  excute_group_by(filters)

	for emp in data:

		for date in data[emp]:
			min_time = None
			max_time = None
			min_over = None
			max_over = None
			startLate = None
			endLate = None
			tLate = None
			startEr = None
			endEr = None
			tEr = None
			for d in data[emp][date]:


				emp_holdy=frappe.get_value('Employee',emp,'holiday_list')
				list_holdy=frappe.get_doc('Holiday List',emp_holdy)
				list_of_holdy=list_holdy.holidays

				holdy_list=is_holiday(d[1],list_of_holdy)
				# frappe.throw(str(holdy_list))

				if holdy_list==False:
					if d[7] == "NOT NULL" and not min_time:
						min_time = d[3]
						max_time = d[4]
						startLate = delay(d[3], d[5])

						entry_period = None
						exit_period = None
						for sh in shift:

							entry_period = convert_to_minutes(sh[1])
							exit_period = convert_to_minutes(sh[2])
							t = convert_to_minutes(sh[1])
							if sh[0] == d[2]:
								d6 = delay(d[6], t)



						ex_day=frappe.get_list("Shift Exceptions Days",
							filters={
								"shift_type":d[2],
								"day":str(frappe.utils.data.get_weekday(d[1])),
								"docstatus":1
						},
						limit=1,
					fields=['*']
						)
						attendance_request_day=frappe.get_list("Attendance Request",
							filters={
								"employee":emp,
								"from_date":[">=",d[1]],
								"to_date":["<=",d[1]],
								"docstatus":1
						},
						limit=1,
					fields=['*']
						)
						# Present On Leave Half Day Work From Home"
						if len(ex_day) > 0:
							d[6]=ex_day[0]['shift_end']
							d[5]=ex_day[0]["shift_start"]

						d6 = d[6]
						if len(ex_day) > 0:

							if d[4] >= delayTotal(d[6], exit_period):
								endLate=endLate
							else:
								endLate=delay(ex_day[0]['shift_end'],d[4])
							if d[3] < delayTotal(d[5], entry_period):
								startLate=startLate
							else:
								startLate = delay(d[3], ex_day[0]['shift_start'])



							if d[3] < ex_day[0]['shift_start']:
								min_over = ex_day[0]['shift_start']- d[3]
							if d[4] > ex_day[0]['shift_end']:
								max_over = d[4] - ex_day[0]['shift_end']
						else:

							if d[4] >= delayTotal(d[6], exit_period):
								endLate = endLate
							else:
								endLate = delay(d6, d[4])

							startLate=delay(d[3],d[5])



							if d[3] < d[5]:
								min_over = d[5] - d[3]

							if d[4] > d[6]:
								max_over = d[4] - d[6]


							# k="po"



						tLate = delayTotal(startLate, endLate)

						startEr = delay(d[5], d[3])
						endEr = delay(d[4], d[6])
						tEr = delayTotal(startEr, endEr)
						if len(attendance_request_day) > 0 :
							tLate=timedelta(00,00,00)
							startLate=timedelta(00,00,00)
							endLate=timedelta(00,00,00)


					if filters.get("employee"):
						if tLate:
							g_emp_total=delayTotal(g_emp_total,tLate)
						if max_over:
							over_emp_total=delayTotal(over_emp_total,max_over)
						if min_over:
							over_emp_total=delayTotal(over_emp_total,min_over)


				basic_total = max_time - min_time if max_time and min_time and max_time > min_time else timedelta(00, 00,
																												00)
				over_total = (
					max_over - min_over if max_over and min_over and max_over > min_over else timedelta(00, 00, 00))
				tHours = basic_total + over_total


				formatted_data.append({
					"name": emp,
					"employee": d[0],
					"date": str(d[1] )+ " "+str(frappe.utils.data.get_weekday(d[1])),
					"min_time": min_time,
					"max_time": max_time,
					"basic_total": basic_total,
					"min_over": min_over,
					"max_over": max_over,
					"over_total": over_total,
					"late_entry": startLate,
					"early_exit": endLate,
					"late_total": tLate,
					"early_entry": startEr,
					"late_exit": endEr,
					"early_total": tEr,
					"working_hours": tHours,
				})


	if filters.get("employee"):
		formatted_data.append({
			"name": "",
			"employee": "",
			"date": "Late Total",
			"min_time": g_emp_total,
			"max_time": "",
			"basic_total": "",
			"min_over": "",
			"max_over": "",
			"over_total": "",
			"late_entry": "",
			"early_exit": "",
			"late_total": "",
			"early_entry": "",
			"late_exit": "",
			"early_total": "",
			"working_hours": "",

		})
		formatted_data.append({
			"name":  "",
			"employee": "",
			"date": "Over Time Total",
			"min_time": over_emp_total,
			"max_time": "",
			"basic_total": "",
			"min_over": "",
			"max_over": "",
			"over_total": "",
			"late_entry": "",
			"early_exit": "",
			"late_total": "",
			"early_entry": "",
			"late_exit": "",
			"early_total": "",
			"working_hours": "",

		})


	formatted_data.extend([{}])
	return columns, formatted_data




def get_data_group_by(filters):
	list_ = frappe.db.sql('''SELECT employee, employee_name, date(time) as ckin_date, shift, TIME(min(time)) as in_time,
		TIME(max(time)) as out_time, TIME(MAX(shift_start)) as shift_start, TIME(MAX(shift_end)) as shift_end, 
		IF(ISNULL(shift), 'NULL', 'NOT NULL') as shift_nullable
		FROM `tabEmployee Checkin` {0} GROUP BY employee, date(time), shift_nullable'''.format(get_conditions(filters)), as_list=1)

	result = {}
	for d in list_:
		result.setdefault(d[0], [])
		result[d[0]].append([d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8]])

	return result


def is_holiday(date,h_list):

	flag=False
	for d in h_list:
		if d.holiday_date == date:
			flag=True
	
	return flag 


def get_columns_group_by():
	return [
		{
			"fieldname": "name",
			"label": _("Employee "),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"fieldname": "employee",
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"width": 170
		},
		{
			"fieldname": "late_entry",
			"label": _("Late Entry"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "early_exit",
			"label": _("Early Exit"),
			"fieldtype": "Data",
			"width": 80
		},
		      {
			"fieldname": "late_total",
			"label": _("Late Total"),
			"fieldtype": "Data",
			"width": 85
		},
		 {
			"fieldname": "early_entry",
			"label": _("Early Entry"),
			"fieldtype": "Data",
			"width": 80
		 },
		 		{
			"fieldname": "late_exit",
			"label": _("Late Exit"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "early_total",
			"label": _("Early Total"),
			"fieldtype": "Data",
			"width": 85
		},
		 {
			"fieldname": "working_hours",
			"label": _("Working Hours"),
			"fieldtype": "Data",
			"width": 120
		},
	]

def excute_group_by(filters):
	formatted_data = []
	columns = get_columns_group_by()
	data = get_data_group_by(filters)
	shift = get_shift()
	for emp in data:
		basic_total = None
		over_total = None
		startLate = None
		endLate = None
		tLate = None
		startEr = None
		endEr = None
		tEr = None
		i = 0
		for d in data[emp]:


			emp_holdy=frappe.get_value('Employee',emp,'holiday_list')
			list_holdy=frappe.get_doc('Holiday List',emp_holdy)
			list_of_holdy=list_holdy.holidays
			holdy_list=is_holiday(d[1],list_of_holdy)



			if d[7] == "NOT NULL":
				temp = delay(d[4], d[3])
				basic_total = delayTotal(basic_total, temp)

				d3 = d[3]
				d6 = d[6]
				emp_shift=None
				for sh in shift:
					if sh[0] == d[2]:
						emp_shift=sh

				entry_period = convert_to_minutes(emp_shift[1])
				exit_period = convert_to_minutes(emp_shift[2])

				ex_day = frappe.get_list("Shift Exceptions Days",
											filters={
												"shift_type": emp_shift[2],
												"day": str(frappe.utils.data.get_weekday(d[1])),
												"docstatus": 1
											},
											limit=1,
											fields=['*']
											)
				attendance_request_day=frappe.get_list("Attendance Request",
					filters={
					"employee":emp,
					"from_date":[">=",d[1]],
					"to_date":["<=",d[1]],
					"docstatus":1
					},
					limit=1,
					fields=['*']
					)
				if len(attendance_request_day) <=0 :
				
					if ex_day and len(ex_day) > 0:
						d[5] = ex_day[0]["shift_start"]
						d[6] = ex_day[0]["shift_end"]


					if d[3] < delayTotal(d[5], entry_period):
						startLate = startLate
					else:
						temp = delay(d3, d[5])
						startLate = delayTotal(startLate, temp)

					if d[4] >= delayTotal(d[6], exit_period):
						endLate = endLate
					else:
						temp = delay(d6, d[4])
						endLate = delayTotal(endLate, temp)

					temp = delay(d[5], d[3])
					startEr = delayTotal(startEr, temp)
					temp = delay(d[4], d[6])
					endEr = delayTotal(endEr, temp)

					if len(attendance_request_day) >0 :
						startLate=timedelta(00,00,00)
						endLate=timedelta(00,00,00)
					if holdy_list :
						startLate=timedelta(00,00,00)
						endLate=timedelta(00,00,00)
						


			elif d[7] == "NULL":
				temp = delay(d[4], d[3])
				over_total = delayTotal(over_total, temp)


		tLate = delayTotal(startLate, endLate)
		tEr = delayTotal(startEr, endEr)
		tHours = delayTotal(basic_total, over_total)
		formatted_data.append({
			"name": emp,
			"employee": d[0],
			"late_entry": to_hours_gruop_by(startLate) if startLate else startLate,
			"early_exit": to_hours_gruop_by(endLate) if endLate else endLate,
			"late_total": to_hours_gruop_by(tLate) if tLate else tLate,
			"early_entry": to_hours_gruop_by(startEr) if startEr else startEr,
			"late_exit": to_hours_gruop_by(endEr) if endEr else endEr,
			"early_total": to_hours_gruop_by(tEr) if tEr else tEr,
			"working_hours": to_hours_gruop_by(tHours) if tHours else tHours,
		})

	formatted_data.extend([{}])
	return columns, formatted_data


def get_conditions(filters):
	condition = " where date(time)>= '%s' and date(time)<= '%s' " % (filters.get("start_date"), filters.get("end_date"))
	if filters.get("employee"):
		condition += " AND employee ='%s' " % (filters.get('employee'))
	return condition


def get_data(filters):
	list_ = frappe.db.sql('''SELECT employee, employee_name, date(time) as ckin_date, shift, TIME(min(time)) as in_time,
		TIME(max(time)) as out_time, TIME(MAX(shift_start)) as shift_start, TIME(MAX(shift_end)) as shift_end, 
		IF(ISNULL(shift), 'NULL', 'NOT NULL') as shift_nullable
		FROM `tabEmployee Checkin` {0} GROUP BY employee, date(time), shift_nullable'''.format(get_conditions(filters)),
						  as_list=1)

	result = {}
	for d in list_:
		result.setdefault(d[0], {}).setdefault(cstr(d[2]), [])
		result[d[0]][cstr(d[2])].append([d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8]])
	return result


def to_hours(duration):
	if duration:
		totsec = duration.total_seconds()
		return totsec // 3600




def to_hours_gruop_by(duration):
	if duration:
		totsec = duration.total_seconds()
		h = totsec//3600
		m = (totsec%3600) // 60
		sec =(totsec%3600)%60
		return "%d:%d:%d" %(h,m,sec)
	else:
		return timedelta(00,00,00)
def to_hours(duration):
	result = timedelta(00, 00, 00)
	if duration:
		totsec = duration.total_seconds()
		h = totsec // 3600
		m = (totsec % 3600) // 60
		if h <= 0 and m <= 0:
			return None
		else:
			return flt("%d.%d" % (h, m), 2)


def get_overtime_total(filters):
	emps = get_data(filters)
	t1 = timedelta(hours=16, minutes=00)
	t2 = timedelta(hours=20, minutes=00)
	result = []
	for emp in emps:
		total_1 = timedelta(00, 00, 00)
		total_2 = timedelta(00, 00, 00)
		for date in emps[emp]:
			for d in emps[emp][date]:
				if d[7] == "NULL":
					if d[3] < t2 and d[4] <= t2:
						if d[3] < t1:
							d[3] = timedelta(hours=16, minutes=00)
						temp = delay(d[4], d[3])
						total_1 = delayTotal(total_1, temp)
					elif d[3] < t2 and d[4] > t2:
						if d[3] < t1:
							d[3] = timedelta(hours=16, minutes=00)

						temp = delay(t2, d[3])
						total_1 = delayTotal(total_1, temp)
						temp = delay(d[4], t2)
						total_2 = delayTotal(total_2, temp)
					elif d[3] > t2:
						temp = delay(d[4], d[3])
						total_2 = delayTotal(total_2, temp)

		result.append([emp, to_hours(total_1), to_hours(total_2)])
	return result


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": _("Employee "),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 190
		},
		{
			"fieldname": "employee",
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "status",
			"label": _("Attendance Status"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "min_time",
			"label": _("CheckIn"),
			"fieldtype": "Data",
			"width": 75
		},
		{
			"fieldname": "max_time",
			"label": _("CheckOut"),
			"fieldtype": "Data",
			"width": 75
		},

		{
			"fieldname": "min_over",
			"label": _("Over Time CheckIn"),
			"fieldtype": "Data",
			"width": 75
		},
		{
			"fieldname": "max_over",
			"label": _("Over Time CheckOut"),
			"fieldtype": "Data",
			"width": 75
		},

		{
			"fieldname": "late_entry",
			"label": _("Late Entry"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "early_exit",
			"label": _("Early Exit"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"label": _("Total"),
			"fieldtype": "Time",
			"fieldname": "basic_total",
			"width": 75

		},
		{
			"label": _("Total"),
			"fieldtype": "Over Time",
			"fieldname": "over_total",
			"width": 175

		},
		{
			"fieldname": "late_total",
			"label": _("Late Total"),
			"fieldtype": "Data",
			"width": 85
		},
		{
			"fieldname": "early_entry",
			"label": _("Early Entry"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "late_exit",
			"label": _("Late Exit"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "early_total",
			"label": _("Early Total"),
			"fieldtype": "Data",
			"width": 85
		},
		{
			"fieldname": "working_hours",
			"label": _("Working Hours"),
			"fieldtype": "Data",
			"width": 120
		},
	]


def get_att_conditions(filters):
    conditions = " where docstatus=1 and employee ='" + \
        filters.get("employee") + "'"
    conditions += " and attendance_date>='" + \
        filters.get("fromdate") + "' and attendance_date<='" + \
        filters.get("todate") + "'"
    return conditions

