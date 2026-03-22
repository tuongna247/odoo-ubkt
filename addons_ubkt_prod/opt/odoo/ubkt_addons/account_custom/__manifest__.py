# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Custom',
    'version': '1.0',
    'summary': 'Account Custom',
    'description': """
    Account Custom""",
    "author": "TT",
    "website": "https://www.odoo.com",
    'depends': ['account', 'hr', 'project_custom'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment_menu.xml',
        'report/paperformat.xml',
        'report/account_report.xml',
        'report/account_report_templates.xml',
        'data/account_custom.xml',
        'data/mail_template_data.xml',
        'data/mail_templates.xml',
        'views/account_payment_views.xml',
        'views/account_payment_filter_views.xml',
        'views/account_portal_templates.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
