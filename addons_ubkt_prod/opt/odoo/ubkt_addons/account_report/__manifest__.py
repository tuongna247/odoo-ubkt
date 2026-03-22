# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Report',
    'version': '1.0',
    'summary': 'Account Report',
    'description': """
    Project Portal""",
    "author": "NPH",
    "website": "#",
    'depends': ['account', 'om_account_daily_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cashbook_modify.xml',
        'report/report_cashbook_modify.xml',
        'report/report_cashbook_modify_initial_balance.xml',
        'report/reports.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
