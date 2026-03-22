# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_phone = fields.Char('Work Phone', default="", store=True)

    working_mode = fields.Selection(selection=[
            ('', ''),
            ('full_time', 'Full time'),
            ('part_time', 'Part time'),
            ('volunteer', 'Volunteer'),
            ('consultant', 'Consultant'),
        ], string='Working Mode', store=True, tracking=True, default='')

    hobby = fields.Char(string='Hobby/Other')

    is_foreign = fields.Boolean(string='Foreign', default=False, store=True)

    @api.model
    def create(self, vals):
        if self.env.context.get('benefactor_flag') == True:
            vals = self.set_default_department_b4save(vals)

        rec =  super(HrEmployee, self).create(vals)

        return rec

    def write(self, vals):
        if self.env.context.get('benefactor_flag') == True:
            vals = self.set_default_department_b4save(vals)
        
        rec = super(HrEmployee, self).write(vals)

        return rec

    def set_default_department_b4save(self, vals):
        data = self.create_employee_department('Benefactor')

        vals['department_id'] = data.id

        return vals

    def create_employee_department(self, name = 'Benefactor'):
        
        data = self.get_employee_department(True)
        
        if data.id <= 0:
            data.create({'name': name, 'is_benefactor': True})
            data = self.get_employee_department(True)
        
        return data

    def get_employee_department(self, is_benefactor = True):
        domain = [
                ('is_benefactor', '=', is_benefactor)
            ]
            
        data = self.env['hr.department'].sudo().search(domain, limit=1)
        return data        
