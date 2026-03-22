# -*- coding: utf-8 -*-

from odoo import models, fields


class HTInformation(models.Model):
    _inherit = 'res.partner'

    is_foreign = fields.Boolean(string='Foreign', default=False, store=True)

    total_this_year = fields.Integer(string='This Year')
    total_last_year = fields.Integer(string='Last Year')
    total_last_two_year = fields.Integer(string='2 Year Before')

    meet_this_year = fields.Integer(string='This Year')
    meet_last_year = fields.Integer(string='Last Year')
    meet_last_two_year = fields.Integer(string='2 Year Before')

