# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from .translate_number import *
import logging
import math
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ['account.payment', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Account Payment"
    # _order = 'date_order desc, id desc'

    def _default_project_task_id(self):
        project_task_id = self.env.context.get('project_task_id')
        
        if project_task_id:
            project_task_id = int(str(project_task_id))
            return self.env['project.task'].search([
                ('id', '=', project_task_id)
            ], limit=1)

    def _default_benefactor(self):
        benefactor = self.env.context.get('benefactor')
        
        if benefactor:
            benefactor = int(str(benefactor))
            return self.env['hr.employee'].search([
                ('id', '=', benefactor)
            ], limit=1)

    def _default_approval(self, user_role):
        if user_role:
            domain = [('user_role', '=', user_role), ('is_approval', '=', True)]
            return self.env['hr.employee'].search(domain, limit=1)
    
    name_seq = fields.Char('Payment Code', readonly=True, copy=False, store=True, default=lambda x: _('New'))
    type_name = fields.Char('Type Name', compute='_compute_type_name')
    define_class = fields.Char('Define Class', compute='_compute_define_class')
    signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By', help='Name of the person that signed the Payment.', copy=False)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    
    project_task_id = fields.Many2one('project.task', string='Project ID', store=True,
        ondelete='cascade', default=_default_project_task_id, help="Select project id ", 
        domain="[('approved_data_entry', '=', True)]")

    approval_id = fields.Many2one('res.users', string='Approval', required=True, store=True, 
        ondelete='restrict', help="Select a approval user ", tracking=True)

    amount = fields.Monetary(string='Amount', readonly=True)
    exchange_rate = fields.Float(string='Exchange rate', default=1, digits=(20, 0))
    foreign_amount = fields.Float(string='Foreign amount', digits=(20, 2))

    pay_currency_id = fields.Many2one('res.currency', string='Payment Currency', store=True, readonly=False)

    paper_payment_code = fields.Char(string='Paper Code')

    is_advance = fields.Boolean(string="Advance Payment", store=True, tracking=True)
    receipt_attachment_ids = fields.Many2many(
        'ir.attachment', 'payment_receipt_rel', 'payment_id', 'att_id', string='Receipts'
    )

    def _benefactor_context(self):
        return {'benefactor_flag': True}

    benefactor_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Benefactor", store=True, readonly=False, ondelete='restrict',
        default=_default_benefactor,
        context=_benefactor_context,
        tracking=True,
        help="Select a benefactor ")

    is_foreign = fields.Boolean(related='benefactor_id.is_foreign', store=False, copy=False, index=False, readonly=True)

    delivered_person = fields.Many2one('res.users', string="Delivered Money Person")
    delivered_person_text = fields.Char(string="Delivered Money Person")
    received_person = fields.Many2one('res.users', string="Received Money Person")
    received_person_text = fields.Char(string="Received Money Person")
    description = fields.Char(string='Description')

    approved_accountant = fields.Boolean(string='Approved by Accountant', default=False, store=True, readonly=True, tracking=True, copy=False)
    accountant_id = fields.Many2one('res.users', string='', store=True, ondelete='restrict', help="Select a user ", tracking=True)
    approved_treasurer = fields.Boolean(string='Approved by Treasurer', default=False, store=True, readonly=True, tracking=True, copy=False)
    treasurer_id = fields.Many2one('res.users', string='', store=True, ondelete='restrict', help="Select a user ", tracking=True)

    partner_id_prj = fields.Many2one(related='project_task_id.partner_id', store=True, readonly=True)
    state_id = fields.Many2one(related='project_task_id.partner_id.state_id', store=True, readonly=True)
    city = fields.Char(related='project_task_id.partner_id.city', store=True, readonly=True)

    user_role = fields.Char(string='User role', compute='_get_user_role')

    def _get_user_role(self):
        user = self.env.user
        self.user_role = str(user.user_role)

    @api.onchange('foreign_amount')
    def _onchange_foreign_amount(self):
        self.amount = self.convert_money(self.foreign_amount, self.exchange_rate)

    @api.onchange('project_task_id')
    def _onchange_project_task_id(self):
        self.partner_id_prj = self.project_task_id.partner_id
        self.state_id = self.project_task_id.partner_id.state_id
        self.city = self.project_task_id.partner_id.city

    @api.onchange('exchange_rate')
    def _onchange_exchange_rate(self):
        self.amount = self.convert_money(self.foreign_amount, self.exchange_rate)
    
    def convert_money(self, number, exchange_rate):
        return number * exchange_rate

    def action_approval(self):
        _logger.info('DEBUG action_approval Start')
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()

        if self.state in ('posted', 'cancel'):
            raise UserError(_('The payment is posted/cancelled. Please refresh form!'))

        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)

        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        
        ctx = {
            'default_model': 'account.payment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def check_project(self):
        # Only payment type is Send
        if not self.project_task_id and self.payment_type == 'outbound' and not self.is_advance and not self.is_internal_transfer:
            raise UserError("Please input project ID")

    def action_accountant(self):
        self.check_project()
        self.write({'approved_accountant': True})

    def action_treasurer(self):
        self.check_project()
        self.write({'approved_treasurer': True})

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        domain = [('user_role', 'in', ('treasurer', 'delivered_person', 'received_person')), ('is_approval', '=', True)]
        records = self.env['res.users'].search(domain)

        treasurer_id = False
        for record in records:
            if record.is_approval == True:
                if record.user_role == 'treasurer':
                    treasurer_id = record
                if record.user_role == 'delivered_person':
                    self.delivered_person = record
                    if self.payment_type != 'inbound':
                        self.delivered_person_text = False
                    # self.received_person = False #Empty
                if record.user_role == 'received_person':
                    self.received_person = record
                    if self.payment_type != 'outbound':
                        self.received_person_text = False
                    # self.delivered_person = False #Empty

        if self.payment_type == 'inbound':
            self.received_person = treasurer_id
        else:
            self.delivered_person = treasurer_id
        
    @api.model
    def default_get(self, fields):
        vals = super(AccountPayment, self).default_get(fields)
        vals['currency_id'] = 23

        domain = [('user_role', 'in', ('pastor', 'accountant', 'treasurer', 'delivered_person', 'received_person')), ('is_approval', '=', True)]
        records = self.env['res.users'].search(domain)

        for record in records:
            if record.is_approval == True:
                if record.user_role == 'pastor':
                    vals['approval_id'] = record
                if record.user_role == 'accountant':
                    vals['accountant_id'] = record
                if record.user_role == 'treasurer':
                    vals['treasurer_id'] = record
                if record.user_role == 'delivered_person':
                    vals['delivered_person'] = record
                if record.user_role == 'received_person':
                    vals['received_person'] = record

        # if vals.get('payment_type') == 'inbound':
        #     vals['received_person'] = vals['treasurer_id']
        # else:
        #     vals['delivered_person'] = vals['treasurer_id']

        return vals

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = self.env['ir.model.data']._xmlid_to_res_id('account_custom.email_template_account_approval', raise_if_not_found=False)
        if force_confirmation_template:
            template_id = self.env['ir.model.data']._xmlid_to_res_id('account_custom.email_template_account_approval_confirm', raise_if_not_found=False)

        return template_id

    def get_portal_last_transaction(self):
        self.ensure_one()
        return self.transaction_ids._get_last()

    def has_to_be_paid(self, include_draft=False):
        return False

    def has_to_be_signed(self, include_draft=False):
        return (self.state in ('sent', 'draft') or (self.state == 'draft' and include_draft))

    def _compute_access_url(self):
        
        super(AccountPayment, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/account_payments/%s' % (order.id)

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=True):
        _logger.info('DEBUG account_payment _get_share_url Start')
        return super(AccountPayment, self)._get_share_url(False, False, None, True)

    def get_class_name(self):
        return self._name

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Payment') if record.state in ('draft', 'sent', 'posted') else _('Other')

    def _get_portal_return_action(self):
        """ Return the action used to display payments when returning from customer portal. """
        _logger.info('DEBUG _get_portal_return_action ')
        self.ensure_one()
        return self.env.ref('account.view_account_payment_tree')

    def display_confirm(self):
        return (self.state in ('sent', 'draft'))

    def _send_order_confirmation_mail(self):
        _logger.info('DEBUG _send_order_confirmation_mail ')
        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)
        template_id = self._find_mail_template(force_confirmation_template=True)
        if template_id:
            for order in self:
                order.with_context(force_send=True).message_post_with_template(template_id, composition_mode='comment', email_layout_xmlid="mail.mail_notification_paynow")

    @api.model
    def create(self, vals):
        payment_type = vals.get('payment_type')

        if not vals.get('name_seq') or vals['name_seq'] == _('New'):
            if 'inbound' == payment_type:
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('account.payment.receive') or _('New')
            elif 'outbound' == payment_type:
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('account.payment.send') or _('New')

        vals = self.convert_money_b4save(vals)
        rec =  super(AccountPayment, self).create(vals)

        return rec

    def write(self, vals):
        vals = self.convert_money_b4save(vals)

        payment_type = vals.get('payment_type')
        if not vals.get('name_seq') or vals['name_seq'] == _('New'):
            if 'inbound' == payment_type:
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('account.payment.receive') or _('New')
            elif 'outbound' == payment_type:
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('account.payment.send') or _('New')

        rec = super(AccountPayment, self).write(vals)

        return rec

    def convert_money_b4save(self, vals):
        exchange_rate = vals.get('exchange_rate')
        if exchange_rate is None:
            exchange_rate = self.exchange_rate

        foreign_amount = vals.get('foreign_amount')
        if foreign_amount is None:
            foreign_amount = self.foreign_amount

        vals['amount'] = self.convert_money(foreign_amount, exchange_rate)

        return vals

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (self.type_name, self.name_seq)

    def format_quantity(self, value, decimals=3, width=0, decimals_separator='.', thousands_separator=',', autoint=False, symbol='', position='after'):
        decimals = max(0,int(decimals))
        width    = max(0,int(width))
        value    = float(value)

        if autoint and math.floor(value) == value:
            decimals = 0
        if width == 0:
            width = ''

        if thousands_separator:
            formatstr = "{:"+str(width)+",."+str(decimals)+"f}"
        else:
            formatstr = "{:"+str(width)+"."+str(decimals)+"f}"


        ret = formatstr.format(value)
        ret = ret.replace(',','COMMA')
        ret = ret.replace('.','DOT')
        ret = ret.replace('COMMA',thousands_separator)
        ret = ret.replace('DOT',decimals_separator)

        if symbol:
            if position == 'after':
                ret = ret + symbol
            else:
                ret = symbol + ret
        return ret

    def _notify_compute_recipients(self, message, msg_vals):
        """ Compute recipients to notify based on subtype and followers. This
        method returns data structured as expected for ``_notify_recipients``. """
        _logger.info('DEBUG _notify_compute_recipients Start')
        msg_sudo = message.sudo()
        # get values from msg_vals or from message if msg_vals doen't exists
        pids = msg_vals.get('partner_ids', []) if msg_vals else msg_sudo.partner_ids.ids
        message_type = msg_vals.get('message_type') if msg_vals else msg_sudo.message_type
        subtype_id = msg_vals.get('subtype_id') if msg_vals else msg_sudo.subtype_id.id
        # is it possible to have record but no subtype_id ?
        recipients_data = []

        res = self.env['mail.followers']._get_recipient_data(self, message_type, subtype_id, pids)
        if not res:
            return recipients_data

        # author_id = msg_vals.get('author_id') or message.author_id.id
        for pid, active, pshare, notif, groups in res:
            # if pid and pid == author_id and not self.env.context.get('mail_notify_author'):  # do not notify the author of its own messages
            #     continue
            if pid:
                # if active is False:
                #     continue
                pdata = {'id': pid, 'active': active, 'share': pshare, 'groups': groups or []}
                if notif == 'inbox':
                    recipients_data.append(dict(pdata, notif=notif, type='user'))
                elif not pshare and notif:  # has an user and is not shared, is therefore user
                    recipients_data.append(dict(pdata, notif=notif, type='user'))
                elif pshare and notif:  # has an user but is shared, is therefore portal
                    recipients_data.append(dict(pdata, notif=notif, type='portal'))
                else:  # has no user, is therefore customer
                    recipients_data.append(dict(pdata, notif=notif if notif else 'email', type='customer'))

        return recipients_data

    def translate_money_string(self, value):
        number_string = translate(value)

        return number_string
