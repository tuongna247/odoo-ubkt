# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Custom',
    'version': '1.0',
    'summary': 'Project Custom',
    'description': """
    Project Custom""",
    "author": "TT",
    "website": "https://www.odoo.com",
    'depends': ['project'],
    'data': [
        'security/groups.xml',
        'report/project_report.xml',
        'report/project_report_templates.xml',
        'data/mail_template_data.xml',
        'data/project_task.xml',
        # 'security/ir.model.access.csv',
        'views/extend_project_views.xml',
        'views/finance_promotion_views.xml',
        'views/icm_form_views.xml',
        'views/construction_info_views.xml',
        'views/project_portal_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_custom/static/src/js/custom_attachment_image_widget.js',
        ],
    },
    'application': True,
    'license': 'LGPL-3',
}
