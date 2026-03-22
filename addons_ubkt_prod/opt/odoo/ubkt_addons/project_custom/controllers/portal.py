# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
import logging
_logger = logging.getLogger(__name__)

class CustomerPortalInherit(portal.CustomerPortal):

    @http.route(['/my/project_tasks/<int:order_id>'], type='http', auth="public", website=True)
    def portal_project_task_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        _logger.info('[debug] portal_project_task_page Start')
        try:
            order_sudo = self._document_check_access('project.task', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='project_custom.action_report_project_custom', download=download)

        values = {
            'project_task': order_sudo,
            'message': message,
            'token': access_token,
            'landing_route': '/project/task/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        history = request.session.get('my_project_tasks_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('project_custom.project_task_portal_template', values)

    @http.route(['/my/project_tasks/<int:order_id>/accept'], type='http', auth="public", website=True)
    def portal_project_task_accept(self, order_id, access_token=None, name=None, **post):
        _logger.info('[debug] portal_project_task_accept Start')
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('project.task', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        message = post.get('approve_message')
        query_string = '&message=sign_ok'
        
        if message:
            order_sudo._approve_project(message)

            _message_post_helper(
                'project.task', order_sudo.id, _('Project is approved by %s') % (order_sudo.approval_id.name,),
                **({'token': access_token} if access_token else {}))
        else:
            query_string = "&message=cant_approve"

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/project_tasks/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def portal_project_task_decline(self, order_id, access_token=None, **post):
        _logger.info('[debug] portal_project_task_decline Start')
        try:
            order_sudo = self._document_check_access('project.task', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if message:
            order_sudo._reject_project(message)
            _message_post_helper(
                'project.task', order_sudo.id, _('Project is rejected by %s') % (order_sudo.approval_id.name,),
                **({'token': access_token} if access_token else {}))
        else:
            query_string = "&message=cant_reject"

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))
