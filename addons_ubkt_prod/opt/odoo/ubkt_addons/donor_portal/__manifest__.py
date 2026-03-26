# -*- coding: utf-8 -*-
{
    'name': 'Donor Portal',
    'version': '1.0',
    'summary': 'Cổng thông tin dâng hiến - Người dâng hiến xem lịch sử dâng',
    'description': 'Cho phép người dâng hiến đăng nhập portal và xem toàn bộ lịch sử dâng hiến theo dự án.',
    'author': 'UBKT',
    'depends': ['portal', 'account_custom', 'project_custom'],
    'data': [
        'security/ir.model.access.csv',
        'views/donor_portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'donor_portal/static/src/css/donor_portal.css',
            'donor_portal/static/src/js/donor_map.js',
        ],
    },
    'application': False,
    'license': 'LGPL-3',
}
