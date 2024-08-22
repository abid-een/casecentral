// Copyright (c) 2024, 4C Solutions and contributors
// For license information, please see license.txt

frappe.query_reports["Clearance Rates"] = {
    "filters": [
        {
            "fieldname": "report_type",
            "label": __("Report Type"),
            "fieldtype": "Select",
            "options": ["Task", "Matter", "Case"],
            "default": "Task",
            "reqd":1
        },
        {
            "fieldname": "fiscal_or_date",
            "label": __("Fiscal Year/Date Range"),
            "fieldtype": "Select",
            "options": ["Fiscal Year", "Date Range"],
            "default": "Date Range",
            "reqd": 1,
            "on_change": function() {
                var fiscal_or_date = frappe.query_report.get_filter_value('fiscal_or_date');
                if (fiscal_or_date === "Fiscal Year") {
                    frappe.query_report.toggle_filter_display('year', false);
                    frappe.query_report.toggle_filter_display('periodicity', false);
                    frappe.query_report.toggle_filter_display('from_date', true);
                    frappe.query_report.toggle_filter_display('to_date', true);
                } else {
                    frappe.query_report.toggle_filter_display('year', true);
                    frappe.query_report.toggle_filter_display('periodicity', false);
                    frappe.query_report.toggle_filter_display('from_date', false);
                    frappe.query_report.toggle_filter_display('to_date', false);
                }
            }
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": Array.from({length: 21}, (v, i) => (new Date().getFullYear() - 10 + i).toString()),
            "default": new Date().getFullYear().toString(),
            "reqd": 1,
            "hidden": 1
        },
        {
            "fieldname": "periodicity",
            "label": __("Periodicity"),
            "fieldtype": "Select",
            "options": ["Monthly", "Quarterly", "Half-Yearly", "Yearly"],
            "default": "Monthly",
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "hidden": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "hidden": 1
        }
    ],

    onload: function(report) {
        var fiscal_or_date = frappe.query_report.get_filter_value('fiscal_or_date');
        if (fiscal_or_date === "Fiscal Year") {
            frappe.query_report.toggle_filter_display('year', false);
            frappe.query_report.toggle_filter_display('periodicity', false);
            frappe.query_report.toggle_filter_display('from_date', true);
            frappe.query_report.toggle_filter_display('to_date', true);
        } else {
            frappe.query_report.toggle_filter_display('year', true);
            frappe.query_report.toggle_filter_display('periodicity', false);
            frappe.query_report.toggle_filter_display('from_date', false);
            frappe.query_report.toggle_filter_display('to_date', false);
        }
    }
};
