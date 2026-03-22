# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    state = fields.Selection(selection_add=[
        ('sent', 'Sent'),
    ], ondelete={'sent': 'cascade'})

    # state = fields.Selection(selection=[
    #         ('draft', 'Draft'),
    #         ('accountant_approved', 'Approved by Accountant'),
    #         ('treasurer_approved', 'Approved by Treasurer'),
    #         ('posted', 'Posted'),
    #         ('cancel', 'Cancelled'),
    #     ], string='Status', required=True, readonly=True, copy=False, tracking=True,
    #     default='draft')

    def _send_approval(self):
        ''' draft -> sent '''
        self.write({'state': 'sent'})

    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get('default_company_id', self.env.company.id)
        domain = [('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]

        journal = None
        if self._context.get('default_currency_id'):
            currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
            journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal
