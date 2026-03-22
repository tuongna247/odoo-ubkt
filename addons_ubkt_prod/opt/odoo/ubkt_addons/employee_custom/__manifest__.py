# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Employee Custom',
    'version': '1.0',
    'summary': 'Employee Custom',
    'description': """
    Employee Custom""",
    "author": "TT",
    "website": "https://www.odoo.com",
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
