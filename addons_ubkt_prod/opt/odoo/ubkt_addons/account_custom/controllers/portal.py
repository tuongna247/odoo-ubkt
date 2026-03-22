# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
import logging
_logger = logging.getLogger(__name__)

class CustomerPortalInherit(portal.CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        _logger.info('DEBUG _prepare_home_portal_values Start')
        values = super()._prepare_home_portal_values(counters)
        # partner = request.env.user.partner_id

        AccountPayment = request.env['account.payment']
        payment_approval_count = AccountPayment.search_count([
            ('state', 'in', ['draft', 'sent', 'posted']) 
        ])

        values.update({
            'payment_approval_count': payment_approval_count,
        })
        return values

    #
    # Account Payment
    #
    @http.route(['/my/payment_approvals', '/my/payment_approvals/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payment_approvals(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        _logger.info('DEBUG portal_my_payment_approvals Start')

        values = self._prepare_portal_layout_values()
        # partner = request.env.user.partner_id
        AccountPayment = request.env['account.payment']

        domain = [
            ('state', 'in', ['draft', 'sent', 'posted']) 
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('account.payment', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = AccountPayment.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/payment_approvals",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = AccountPayment.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_payment_approvals_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'payment_approvals': quotations.sudo(),
            'page_name': 'payment_approval',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/payment_approvals',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("account_custom.portal_my_payment_approvals", values)

    @http.route(['/my/account_payments/<int:order_id>'], type='http', auth="public", website=True)
    def portal_account_payment_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        _logger.info('DEBUG portal_account_payment_page Start')
        try:
            order_sudo = self._document_check_access('account.payment', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='account_custom.action_report_account_payment', download=download)

        # use sudo to allow accessing/viewing account_payments for public user
        # only if he knows the private token
        # Log only once a day
        # if order_sudo:
        #     # store the date as a string in the session to allow serialization
        #     now = fields.Date.today().isoformat()
        #     session_obj_date = request.session.get('view_approval_%s' % order_sudo.id)
        #     if session_obj_date != now and request.env.user.share and access_token:
        #         request.session['view_approval_%s' % order_sudo.id] = now
        #         body = _('Approval viewed by approver %s', order_sudo.partner_id.name)
        #         _message_post_helper(
        #             "account.payment",
        #             order_sudo.id,
        #             body,
        #             token=order_sudo.access_token,
        #             message_type="notification",
        #             subtype_xmlid="mail.mt_note",
        #             partner_ids=order_sudo.user_id.sudo().partner_id.ids,
        #         )

        values = {
            'account_payment': order_sudo,
            'message': message,
            'token': access_token,
            'landing_route': '/account/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_approval_history', [])
        else:
            history = request.session.get('my_account_payments_history', [])
        values.update(get_records_pager(history, order_sudo))

        # return request.render('sale.sale_order_portal_template', values)
        return request.render('account_custom.account_payment_portal_template', values)

    # @http.route(['/my/account_payments/<int:order_id>/accept'], type='json', auth="public", website=True)
    @http.route(['/my/account_payments/<int:order_id>/accept'], type='http', auth="public", methods=['POST'], website=True)
    # def portal_account_payment_accept(self, order_id, access_token=None, name=None, signature=None):
    def portal_account_payment_accept(self, order_id, access_token=None, **post):
        _logger.info('DEBUG portal_account_payment_accept Start')

        # get from query string if not on json param
        # access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('account.payment', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}
        
        if not order_sudo.has_to_be_signed():
            return request.redirect('/my')

        try:
            order_sudo.write({
                'signed_by': order_sudo.approval_id.name,
                'signed_on': fields.Datetime.now(),
                'signature': order_sudo.approval_id.sign_signature,
            })

            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return request.redirect('/my')

        if not order_sudo.has_to_be_paid():
            order_sudo.action_post()
            order_sudo._send_order_confirmation_mail()

        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'
        
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/account_payments/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def portal_account_payment_decline(self, order_id, access_token=None, **post):
        _logger.info('DEBUG portal_account_payment_decline Start')
        try:
            order_sudo = self._document_check_access('account.payment', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if order_sudo.has_to_be_signed() and message:
            order_sudo.action_cancel()
            _message_post_helper('account.payment', order_id, _('Payment is rejected by %s : %s') % (order_sudo.approval_id.name, message), 
            **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

