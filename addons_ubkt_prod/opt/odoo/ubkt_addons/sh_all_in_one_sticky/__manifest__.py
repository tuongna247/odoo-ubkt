# Part of Softhealer Technologies.
{
    "name" : "All in one Sticky",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "license": "OPL-1",
    "summary": "Set Fix Header Module, Form View Freeze Header, Set Permanent Header, Website Sticky Header, Freeze form view status bar,Sticky list view header,Fix list view footer,Sticky chatter header,Freeze list view inside form view Odoo",
    "description": """This module provides a sticky form view status bar, sticky list view header, sticky list view footer, sticky chatter header & sticky list view inside form view.""",
    "version":"15.0.4",
    "depends" : [
                "web",
                "base_setup"
            ],
    "application" : True,
    "data" : [
         "views/res_config_view.xml",
         "data/web_assets_back_sticky.xml",
            ],
    'assets': {
       
        'web.assets_backend': [
            '/sh_all_in_one_sticky/list_sticky/static/src/js/list_renderer.js',
            ],
    },
    "images": ['static/description/background.png',],
    "auto_install":False,
    "installable" : True,
    "price": 25,
    "currency": "EUR"
}
