# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from .project_constants import *
import logging
_logger = logging.getLogger(__name__)

class ConstructionInfo(models.Model):
    # _inherit = 'project.task'
    _name = "project.task"
    _inherit = ['project.task', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Project Task"

    construction_info = fields.Boolean(string='Construction Info', default=False, store=True)
    attachment_flag = fields.Boolean(string='Document Files', default=False, store=True)

    # Feedback info
    # Opinion of the deacon board - the construction board
    opinion_deacon_board = fields.Text(string='Board Remark', ondelete='restrict', tracking=True)
    # Opinion of the advisor
    opinion_advisor = fields.Text(string='Advisor Remark', ondelete='restrict', tracking=True)
    # Opinion of the pastor
    opinion_pastor = fields.Text(string='Pastor Remark', ondelete='restrict', tracking=True)

    state_id = fields.Many2one(related='partner_id.state_id', store=True, readonly=True)
    city = fields.Char(related='partner_id.city', store=True, readonly=True)
    approval_id = fields.Many2one('res.users', string='Approval', required=True, store=True, copy=True, 
        ondelete='restrict', help="Select a approval user ")

    approval_state = fields.Selection(selection=[
            ('open', 'Open'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ], string='Approval Status', store=True, copy=False, tracking=True, readonly=True,
        default='open')

    attachment_id = fields.Many2many('ir.attachment', 'email_project_template_attachment_rel', 'email_project_template_id',
                                      'attachment_id', string="The attachment files", copy=False)

    consult_state = fields.Selection(selection=[
            ('responded', 'Responded'),
            ('wait_response', 'Waiting for response'),
            ('no_reponse', 'No response'),
        ], string='Consult. Status', store=True, copy=False, tracking=True,
        default='wait_response')

    display_consult_state = fields.Boolean(string='', 
            compute='_display_consult_state', default=False, store=False)

    def action_send_mail(self):
        _logger.info('[Debug] action_send_mail Start')
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()

        template_id = self._find_mail_template()
        # lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)

        _logger.info('[Debug] template ' + str(template))


        ctx = {
            'default_model': 'project.task',
            # 'mail_post_autofollow': True,
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            # 'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            # 'custom_layout': 'mail.mail_notification_light',
            'force_email': True,
            'model_description': '',
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

    def _find_mail_template(self):
        _logger.info('[Debug] _find_mail_template Start')
        # default email
        template_id = self.env['ir.model.data']._xmlid_to_res_id('project_custom.email_project_custom', raise_if_not_found=False)
        
        # Template Opinion of the pastor
        if self.stage_id.id == STAGE_ID_PASTOR: 
            template_id = self.env['ir.model.data']._xmlid_to_res_id('project_custom.email_template_project_task_approval', raise_if_not_found=False)
        # Template consultations
        elif self.stage_id.id == STAGE_ID_CONSULT:
            template_id = self.env['ir.model.data']._xmlid_to_res_id('project_custom.email_template_project_task_consult', raise_if_not_found=False)

        return template_id

    def _notify_compute_recipients(self, message, msg_vals):
        """ Compute recipients to notify based on subtype and followers. This
        method returns data structured as expected for ``_notify_recipients``. """
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

        for pid, active, pshare, notif, groups in res:
            if pid:
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

    def _compute_access_url(self):
        super(ConstructionInfo, self)._compute_access_url()
        for task in self:
            task.access_url = '/my/project_tasks/%s' % (task.id)

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=True):
        _logger.info('[Debug] ConstructionInfo _get_share_url Start')
        return super(ConstructionInfo, self)._get_share_url(redirect=False)

    def _get_portal_return_action(self):
        """ Return the action used to display tasks when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('project.view_task_form2')

    def display_confirm(self):
        return (self.approval_state == 'open')

    def _display_consult_state(self):
        self.display_consult_state = (self.stage_id.id == STAGE_ID_CONSULT)

    def _approve_project(self, message):
        self.write({'approval_state': 'approved', 'opinion_pastor': message})

    def _reject_project(self, message):
        self.write({'approval_state': 'rejected', 'opinion_pastor': message})
