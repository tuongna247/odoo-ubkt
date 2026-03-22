# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Activity Notification",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "15.0.1",
    "category": "Discuss",
    "summary": "Activity Notifier Module, Send Activity Notification, Activity Notification Salesperson, Activity Notification Customer, Reminder For Activity, Fix Activity Notification, Schedule Activity And Notification, Notification Management Odoo",
    "description": """The main purpose of the activity notification is to announce the arrival of the meeting time. another purpose of this module to make one aware of facts or occurrences before the due date. This module will help to send a notification before and after the activity due date. You can notify your salesperson/customer before or after the activity is done. Suppose you want to notify your salesperson for a meeting before the due date of the meeting so you can set a schedule into 'schedule activity' in the chatter of any form of view.""",
    "depends": [
        'sh_activity_base'
    ],
    "data": [
        'data/data_sales_activity_notification.xml',
        'data/sales_activity_email_template.xml',
    ],
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "25",
    "currency": "EUR"
}
