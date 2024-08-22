import frappe
from frappe.utils import flt, getdate, add_months
from datetime import datetime, timedelta
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    message = filters.get('report_type'), 's Report'
    chart = get_chart_data(filters,columns,data)
    return columns, data, message, chart

def get_chart_data(filters, columns, data):
    labels = [d.get("period") for d in data]

    # Prepare datasets for total and completed tasks
    total_data, completed_data = [], []

    for entry in data:
        total_data.append(entry.get("total", 0))
        completed_data.append(entry.get("completed", 0))

    datasets = []
    if total_data:
        datasets.append({
            "name": _("Total Tasks"),
            "backgroundColor": "#f39c12",
            "values": total_data
        })
    if completed_data:
        datasets.append({
            "name": _("Completed Tasks"),
            "backgroundColor": "#00a65a",
            "values": completed_data
        })

    chart = {
        "type": "bar",  # or "line" depending on your needs
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "scales": {
                "x": {
                    "stacked": True 
                },
                "y": {
                    "beginAtZero": True
                }
            }
        }
    }

    return chart



def get_columns():
    return [
        {"fieldname": "period", "label": "Period", "fieldtype": "Data", "width": 150},
        {"fieldname": "total", "label": "Total (Pending + Created)", "fieldtype": "Int", "width": 150},
        {"fieldname": "completed", "label": "Completed", "fieldtype": "Int", "width": 100},
        {"fieldname": "clearance_rate", "label": "Clearance Rate (%)", "fieldtype": "Percent", "width": 150}
    ]

def get_data(filters):
    data = []
    from_date, to_date = get_date_range(filters)
    periodicity = filters.get('periodicity', 'Monthly')
    report_type = filters.get("report_type")

    if not from_date or not to_date:
        frappe.throw(_("Invalid date range"))

    if report_type == "Task":
        report_data = get_task_clearance_data(from_date, to_date, periodicity)
    elif report_type == "Matter":
        report_data = get_matter_clearance_data(from_date, to_date, periodicity)
    elif report_type == "Case":
        report_data = get_case_clearance_data(from_date, to_date, periodicity)
    else:
        frappe.throw(_("Invalid report type"))

    data.extend(format_clearance_data(report_data))
    return data

def get_date_range(filters):
    fiscal_or_date = filters.get("fiscal_or_date")
    from_date = to_date = None

    if fiscal_or_date == "Fiscal Year":
        year = int(filters.get("year"))
        from_date = datetime(year, 1, 1)
        to_date = datetime(year, 12, 31)
    else:
        from_date = getdate(filters.get("from_date"))
        to_date = getdate(filters.get("to_date")) + timedelta(days=1)

    return from_date, to_date

def format_clearance_data(data):
    formatted_data = []
    for entry in data:
        formatted_data.append({
            "period": entry.get("period"),
            "total": entry.get("total"),
            "completed": entry.get("completed"),
            "clearance_rate": entry.get("clearance_rate")
        })
    return formatted_data

def get_periods(from_date, to_date, periodicity):
    if periodicity == 'Monthly':
        return get_monthly_periods(from_date, to_date)
    elif periodicity == 'Quarterly':
        return get_quarterly_periods(from_date, to_date)
    elif periodicity == 'Half-Yearly':
        return get_half_yearly_periods(from_date, to_date)
    elif periodicity == 'Yearly':
        return [(from_date, to_date)]
    else:
        frappe.throw(_("Invalid periodicity"))

def get_monthly_periods(from_date, to_date):
    periods = []
    start_date = from_date
    end_date = to_date
    while start_date <= end_date:
        next_date = add_months(start_date, 1) - timedelta(days=1)
        periods.append((start_date, min(next_date, end_date)))
        start_date = next_date + timedelta(days=1)
    return periods

def get_quarterly_periods(from_date, to_date):
    periods = []
    start_date = from_date
    end_date = to_date
    while start_date <= end_date:
        next_date = add_months(start_date, 3) - timedelta(days=1)
        periods.append((start_date, min(next_date, end_date)))
        start_date = next_date + timedelta(days=1)
    return periods

def get_half_yearly_periods(from_date, to_date):
    periods = []
    start_date = from_date
    end_date = to_date
    while start_date <= end_date:
        next_date = add_months(start_date, 6) - timedelta(days=1)
        periods.append((start_date, min(next_date, end_date)))
        start_date = next_date + timedelta(days=1)
    return periods

def get_period_label(period_from_date, period_to_date, periodicity):
    if periodicity == 'Monthly':
        return f"{period_from_date.strftime('%b %Y')}"
    else:
        return f"{period_from_date.strftime('%b %Y')} - {period_to_date.strftime('%b %Y')}"

# Task Clearance Data
def get_task_clearance_data(from_date, to_date, periodicity):
    data = []
    periods = get_periods(from_date, to_date, periodicity)
    
    for period_from_date, period_to_date in periods:
        total = get_task_total(period_from_date, period_to_date)
        completed = get_task_completed(period_from_date, period_to_date)
        clearance_rate = (completed / total * 100) if total else 0
        data.append({
            "period": get_period_label(period_from_date, period_to_date, periodicity),
            "total": total,
            "completed": completed,
            "clearance_rate": clearance_rate
        })

    return data

def get_task_total(from_date, to_date):
    pending_before = frappe.db.count("Task", filters={
        'status': ['not in', ['Cancelled', 'Completed']],
        'creation': ['<', from_date]
    })
    created_in_period = frappe.db.count("Task", filters={
        'status': ['!=', 'Cancelled'],
        'creation': ['between', [from_date, to_date]]
    })
    return pending_before + created_in_period

def get_task_completed(from_date, to_date):
    return frappe.db.count("Task", filters={
        'status': ['=', 'Completed'],
        'completed_on': ['between', [from_date, to_date]]
    })

# Matter Clearance Data
def get_matter_clearance_data(from_date, to_date, periodicity):
    data = []
    periods = get_periods(from_date, to_date, periodicity)
    
    for period_from_date, period_to_date in periods:
        total = get_matter_total(period_from_date, period_to_date)
        completed = get_matter_completed(period_from_date, period_to_date)
        clearance_rate = (completed / total * 100) if total else 0
        data.append({
            "period": get_period_label(period_from_date, period_to_date, periodicity),
            "total": total,
            "completed": completed,
            "clearance_rate": clearance_rate
        })

    return data

def get_matter_total(from_date, to_date):
    pending_before = frappe.db.count("Matter", filters={
        'status': ['not in', ['Cancelled', 'Completed']],
        'creation': ['<', from_date]
    })
    created_in_period = frappe.db.count("Matter", filters={
        'status': ['!=', 'Cancelled'],
        'creation': ['between', [from_date, to_date]]
    })
    return pending_before + created_in_period

def get_matter_completed(from_date, to_date):
    return frappe.db.count("Matter", filters={
        'status': ['=', 'Completed'],
        'modified': ['between', [from_date, to_date]]
    })

# Case Clearance Data
def get_case_clearance_data(from_date, to_date, periodicity):
    data = []
    periods = get_periods(from_date, to_date, periodicity)
    
    for period_from_date, period_to_date in periods:
        total = get_case_total(period_from_date, period_to_date)
        completed = get_case_completed(period_from_date, period_to_date)
        clearance_rate = (completed / total * 100) if total else 0
        data.append({
            "period": get_period_label(period_from_date, period_to_date, periodicity),
            "total": total,
            "completed": completed,
            "clearance_rate": clearance_rate
        })

    return data

def get_case_total(from_date, to_date):
    pending_before = frappe.db.count("Case", filters={
        'status': ['not in', ['Disposed', 'NOC']],
        'creation': ['<', from_date]
    })
    created_in_period = frappe.db.count("Case", filters={
        'status': ['!=', 'Cancelled'],
        'creation': ['between', [from_date, to_date]]
    })
    return pending_before + created_in_period

def get_case_completed(from_date, to_date):
    return frappe.db.count("Case", filters={
        'status': ['=', 'Disposed'],
        'date_of_disposal': ['between', [from_date, to_date]]
    })
