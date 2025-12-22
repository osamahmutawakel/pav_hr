# Copyright (c) 2022, Farouk Muharram and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
from unittest import result
import frappe, erpnext
from frappe.utils import (flt, cstr, getdate)
from datetime import timedelta

#called from file delay penalty method fill_employee
def get_penalty_minuts(filters, emps, shift):
    from pav.pav.report.date_wise_employee_checkin.date_wise_employee_checkin import execute   
    
    from_date = getdate(filters.get('from'))
    to_date = getdate(filters.get('to'))
    
    holiday_list = [d.holiday_list for d in emps if d.holiday_list]
    default_holiday_list = frappe.get_cached_value('Company',  filters.get("company"),  "default_holiday_list")
    holiday_list.append(default_holiday_list)
    holiday_list = list(set(holiday_list))
    holiday_map = get_holiday(holiday_list)
    chks = get_checkin(filters)

    f, chks = execute(filters)
    filters["dates"] = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1)]
    day_hours = timedelta(hours=shift.hour_factor , minutes=00)
    min = timedelta(hours=0 , minutes=10)
    max = timedelta(hours=0 , minutes=30, seconds = 59)
    result = {}
    att_map = get_attendance_list(get_conditions(filters), filters)
    
    for emp in emps:
        result.setdefault(emp.name, 0)
        chk_date = []
        emp_att = att_map.get(emp.name)

        for chk in chks:
            if shift.single_checkin:
                field = "late_entry"
            else:
                field = "late_total"

            if chk and chk['name'] == emp.name:
                chk_date.append(chk['date'])
                if field in chk and chk[field]:
                    found = False
                    for penalty in shift.penalty_calculation:
                        if chk[field] >= penalty.from_time and chk[field] <= penalty.to_time:
                            result[emp.name] += penalty.penalty_minutes
                            found = True
                            break
                    
                    if not found:
                        result[emp.name] += get_minuts(chk[field])
                        # elif chk[field] >= min and chk[field] <= max:
                        #     seconds = chk[field].total_seconds()
                        #     minutes = (seconds % 3600) // 60
                        #     frappe.msgprint(str(chk[field]))
                        #     frappe.msgprint(str(minutes))
                        #     result[emp.name] += minutes
                        #     break
                    
        
        for date in filters['dates']:
            if date in chk_date:
                continue
            
            if holiday_map:
                emp_holiday_list = emp.holiday_list if emp.holiday_list else default_holiday_list
                if emp_holiday_list in holiday_map and date in holiday_map[emp_holiday_list]:
                    continue
            
           
            if emp_att:
                att_status = emp_att.get(str(date), None)
                if att_status and (att_status == 'On Leave' or att_status == 'Present') :
                    continue
            
            for penalty in shift.penalty_calculation:
                if day_hours >= penalty.from_time and day_hours <= penalty.to_time:
                    result[emp.name] += penalty.penalty_minutes
            
    return result

def get_minuts(duration):
    if duration:
        return int(duration.total_seconds() / 60) % 60
    else:
        return 0

def get_penalty_minuts1(filters, emps, shift):
    from pav.pav.report.date_wise_employee_checkin.date_wise_employee_checkin import execute   
    
    f, lates = execute(filters)
    result = {}
    for late in lates:
        for emp in emps:
            if late and late['name'] == emp.name and 'late_total' in late and late['late_total']:
                result.setdefault(late['name'], 0)

                for penalty in shift.penalty_calculation:
                    if late['late_total'] >= penalty.from_time and late['late_total'] <= penalty.to_time:
                        result[late['name']] += penalty.penalty_minutes
    return result

def get_absent(filters, emps, shift):
    from_date = getdate(filters.get('from_date'))
    to_date = getdate(filters.get('to_date'))
    filters["dates"] = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1)]
    
    att_map = get_attendance_list(get_conditions(filters), filters)
    holiday_list = [d.holiday_list for d in emps if d.holiday_list]
    default_holiday_list = frappe.get_cached_value('Company',  filters.get("company"),  "default_holiday_list")
    holiday_list.append(default_holiday_list)
    holiday_list = list(set(holiday_list))
    holiday_map = get_holiday(holiday_list)
    chks = get_checkin(filters)
    
    result = {}
    for emp in emps:
        absent = 0.0
        emp_att = None
        emp_chk = None

        if att_map:
            emp_att = att_map.get(emp['name'])
        if chks:
            emp_chk = chks.get(emp['name'])

        for date in filters['dates']:
            increase = 1.0
            if shift.single_checkin:
                if emp_chk:
                    day_chk = emp_chk.get(cstr(date))
                    if day_chk:
                        continue
            else:
                if emp_att:
                    att_status = emp_att.get(cstr(date), None)
                    if att_status and att_status != 'Absent':
                        continue
                    elif att_status and att_status != 'Half Day':
                        increase = 0.5
                    
            if holiday_map:
                emp_holiday_list = emp.holiday_list if emp.holiday_list else default_holiday_list
                if emp_holiday_list in holiday_map and date in holiday_map[emp_holiday_list]:
                    continue

            absent += increase

        result.setdefault(emp['name'], absent)
    
    return result

def get_shifts():
    data = frappe.db.sql(""" select sh.name, sh.penalty_enable, sh.single_checkin, p.from_time, p.to_time, p.penalty_minutes 
            from `tabShift Type` sh 
            join `tabPenalty Calculation` p on sh.name = p.parent and p.parenttype = 'Shift Type' 
            """, as_dict=1)

    result = {}
    for d in data:
        result.setdefault(d['name'], {'penalty_enable': d['penalty_enable'], 'single_checkin': d['single_checkin'],
            'penalty_calculation': []})
        result[d['name']]['penalty_calculation'].append({'from_time': d['from_time'], 'to_time': d['to_time'], 
        'penalty_minutes': d['penalty_minutes']})
    return result
        
def get_conditions(filters):
	conditions = ""
	if filters.get("employee"):
		conditions += " AND employee = %(employee)s "
	return conditions

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql("""select employee, attendance_date, status 
		from tabAttendance where docstatus = 1 {0} and attendance_date between %(from)s and %(to)s 
		order by employee, attendance_date""".format(conditions), filters, as_dict=1)

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(cstr(d.attendance_date), d.status)

	return att_map

def get_employee_details(filters):
	emp_map = frappe._dict()
	for d in frappe.db.sql("""select name, employee_name, designation, department, branch, company,
		holiday_list from tabEmployee where company = "%s" """ % (filters.get("company")), as_dict=1):
		emp_map.setdefault(d.name, d)

	return emp_map

def get_checkin(filters):
	condition = " where date(time)>= '%s' and date(time)<= '%s' " % (filters.get("from_date"), filters.get("to_date"))
	if filters.get("employee"):
		condition += " AND employee ='%s' " % (filters.get('employee'))

	list_ = frappe.db.sql('''SELECT employee, employee_name, date(time) as ckin_date, shift, TIME(min(time)) as in_time,
		TIME(max(time)) as out_time, TIME(MAX(shift_start)) as shift_start, TIME(MAX(shift_end)) as shift_end, 
		IF(ISNULL(shift), 'NULL', 'NOT NULL') as shift_nullable
		FROM `tabEmployee Checkin` {0} GROUP BY employee, date(time), shift_nullable'''.format(condition), as_list=1)

	result = {}
	for d in list_:
		result.setdefault(d[0], {}).setdefault(cstr(d[2]), [])
		result[d[0]][cstr(d[2])].append([d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8]])
	return result

def get_holiday(holiday_list):
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(d, frappe.db.sql_list('''select holiday_date from `tabHoliday` where parent=%s''', (d)))

	return holiday_map