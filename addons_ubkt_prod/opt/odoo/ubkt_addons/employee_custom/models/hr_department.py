# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class HRDepartment(models.Model):
    _inherit = 'hr.department'

    name = fields.Char('Department Name', required=True, translate=True)
    is_benefactor = fields.Boolean(string='For Benefactor', default=False, store=True)
