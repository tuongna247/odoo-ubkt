# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    sign_signature = fields.Binary(string='Digital Signature')
    sign_stamp = fields.Binary(string='Digitial Stamp')
    sign_stamp_send = fields.Binary(string='Digitial Stamp (Send)')
    user_role = fields.Selection(selection=[
            ('', ''),
            ('pastor', 'Pastor'),
            ('accountant', 'Accountant'),
            ('treasurer', 'Treasurer'),
            ('delivered_person', 'Delivered Money Person'),
            ('received_person', 'Received Money Person'),
        ], string='Role', store=True, tracking=True, default='')
    
    is_approval = fields.Boolean(string='Is Approval')
    data_entry_approval = fields.Boolean(string='Data Entry Approval')
