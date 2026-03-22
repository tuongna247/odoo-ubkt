# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
# import logging
# _logger = logging.getLogger(__name__)

class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):

        activity_quick = self._context.get('mail_activity_quick_update')
        default_use_template = self._context.get('default_use_template')

        if True != activity_quick:
            if default_use_template and self.model != 'hr.expense.sheet' and not self.partner_ids:
                raise UserError(_("No recipient found. Please input Recipients!"))

        ret = super(MailComposer, self)._action_send_mail(auto_commit)
        return ret
