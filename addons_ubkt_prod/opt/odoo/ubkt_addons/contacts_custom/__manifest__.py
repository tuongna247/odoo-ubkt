# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Contacts Custom',
    'version': '1.0',
    'summary': 'Contacts Custom',
    'description': """
    Contacts Custom""",
    "author": "TT",
    "website": "https://www.odoo.com",
    'depends': ['contacts', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ht_info_views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
