# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools, exceptions
from odoo.exceptions import AccessError
from .project_constants import *
import logging
_logger = logging.getLogger(__name__)

class FinancePromotion(models.Model):
    _inherit = 'project.task'

    def _is_project_only_user(self):
        return self.env.user.has_group('project_custom.group_project_only_user')

    name_seq = fields.Char('Code', readonly=True, store=True, default=lambda x: _('New'))

    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    # benefactor = fields.Many2one('res.partner', string="Benefactor")

    def _benefactor_context(self):
        return {'benefactor_flag': True}

    benefactor = fields.Many2one(
        comodel_name='hr.employee',
        string="Benefactor", store=True,
        context=_benefactor_context,
        tracking=True,
        help="Select a benefactor ")

    finance_promotion = fields.Boolean(string='Finance Promotion', default=False, store=True)
    task_payment_count = fields.Integer(compute='_compute_task_payment_count', string='Payments')

    # Finance Info
    total_estimate_church = fields.Float(
        string='Total estimate of church construction',
        digits=(25, 0))

    total_amount_spent = fields.Float(string='Total amount spent', digits=(25, 0))
    up_to_date = fields.Date(string='Up to date', store=True)
    amount_wantage = fields.Float(string='Amount wantage', digits=(25, 0))
    child_god_donate = fields.Float(string='Children of God donate', digits=(25, 0))
    benefactor_donate = fields.Float(string='Benefactor donate', digits=(25, 0))
    
    # Construction data
    total_land_area = fields.Float(string='Total land area (m2)', compute='_compute_land_area', readonly=True)
    land_length = fields.Float(string='Land Length (m)', default=0)
    land_width = fields.Float(string='Land Width (m)', default=0)
    land_origin = fields.Text(string='Land Origin')
    land_owner = fields.Many2one('res.partner', string="Land Owner")
    authorized_person = fields.Text(string='Authorized person to sign the pledge')

    total_church_area = fields.Float(string='Total church area (m2)', compute='_compute_church_area', readonly=True)
    church_length = fields.Float(string='Church Length (m)', default=0)
    church_width = fields.Float(string='Church Width (m)', default=0)
    main_materials = fields.Text(string='Main building materials (foundation, wall, door, roof...)')

    approved_data_entry = fields.Boolean(string='Approved Data', default=False, store=True, readonly=True, tracking=True, copy=False)
    user_has_data_entry_approval = fields.Boolean(string='Has Data Entry Approval', compute='_compute_user_has_data_entry_approval')

    def _compute_user_has_data_entry_approval(self):
        for task in self:
            task.user_has_data_entry_approval = self.env.user.data_entry_approval

    @api.onchange('land_length')
    def _onchange_land_length(self):
        self.total_land_area = self.cal_area(self.land_length, self.land_width)

    @api.onchange('land_width')
    def _onchange_land_width(self):
        self.total_land_area = self.cal_area(self.land_length, self.land_width)

    @api.onchange('church_length')
    def _onchange_church_length(self):
        self.total_church_area = self.cal_area(self.church_length, self.church_width)

    @api.onchange('church_width')
    def _onchange_church_width(self):
        self.total_church_area = self.cal_area(self.church_length, self.church_width)
    
    def cal_area(self, length, width):
        return length * width

    def _compute_land_area(self):
        self.total_land_area = self.cal_area(self.land_length, self.land_width)
    
    def _compute_church_area(self):
        self.total_church_area = self.cal_area(self.church_length, self.church_width)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if not self.approved_data_entry:
            if self.stage_id.id != STAGE_ID_INPUT_NEW:
                self.stage_id = self._origin.stage_id.id
                raise exceptions.UserError("Profile has not been approved!")

    @api.model
    def create(self, vals):
        if not vals.get('name_seq') or vals['name_seq'] == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('project.task') or _('New')

        return super(FinancePromotion, self).create(vals)
    
    def write(self, vals):
        if 'approved_data_entry' in vals and not vals.get('approved_data_entry'):
            if 'stage_id' in vals and vals.get('stage_id') != STAGE_ID_INPUT_NEW :
                raise exceptions.UserError("Profile has not been approved!")

        rec = super(FinancePromotion, self).write(vals)

        return rec

    def action_create_payment(self):
        ''' Open the account.payment wizard to pay the selected journal entries.
        :return: An action opening the account.payment wizard.
        '''
        if self._is_project_only_user():
            raise AccessError(_("You are not allowed to access Payments."))

        lang = self.env.context.get('lang')

        return {
            'name': _('Create Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.payment',
                'project_task_id': self.id,
                'benefactor': self.benefactor.id,
                'lang': lang
            },
            'target': 'self',
            'type': 'ir.actions.act_window',
        }

    def open_payment_view(self):
        if self._is_project_only_user():
            raise AccessError(_("You are not allowed to access Payments."))

        lang = self.env.context.get('lang')

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'views': [(self.env.ref('account_custom.account_payment_list_view_form_extend').id, 'list')],
            'name': _('Payments'),
            'context': {
                'active_model': 'account.payment',
                'project_task_id': self.id,
                'benefactor': self.benefactor.id,
                'lang': lang
            },
            'domain': [('project_task_id', '=', self.id)],
            'target': 'current',
        }

    def _compute_task_payment_count(self):
        task_payment_count = self.env['account.payment'].search_count([('project_task_id', '=', self.id)])
        self.task_payment_count = task_payment_count

    def action_approve_data_entry(self):
        self.write({'approved_data_entry': True})
