{
    "name": "Format separator number",
    "version": "15.0",
    "summary": "Auto format decimal separator when user typing",
    "category": "Web",
    "depends": ["web"],
    "author": "CM",
    "website": "https://www.odoo.com",
    "data": [
        # "views/web_format_number.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'format_number/static/src/js/format_number.js',
        ]
    },
    "installable": True,
    'license': 'LGPL-3',
}
