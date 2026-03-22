# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import defaultdict


class DonorPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        employee = self._get_current_employee()

        if 'donor_count' in counters:
            if employee:
                values['donor_count'] = request.env['account.payment'].sudo().search_count([
                    ('benefactor_id', '=', employee.id),
                    ('state', '=', 'posted'),
                ])
            else:
                values['donor_count'] = 0

        # Nếu là người dâng hiến → ẩn mục "Payment Approvals" khỏi portal home
        if employee:
            values['payment_approval_count'] = 0

        return values

    def _get_current_employee(self):
        """Tìm hr.employee của user hiện tại qua address_home_id hoặc user_id."""
        partner = request.env.user.partner_id
        employee = request.env['hr.employee'].sudo().search([
            '|',
            ('address_home_id', '=', partner.id),
            ('user_id', '=', request.env.user.id),
        ], limit=1)
        return employee

    @http.route(['/my/donations', '/my/donations/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_donor_list(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.render('donor_portal.donor_not_found')

        Payment = request.env['account.payment'].sudo()

        domain = [
            ('benefactor_id', '=', employee.id),
            ('state', '=', 'posted'),
        ]
        if date_begin:
            domain += [('date', '>=', date_begin)]
        if date_end:
            domain += [('date', '<=', date_end)]

        # Sắp xếp
        sort_options = {
            'date_desc': ('date desc', 'Ngày mới nhất'),
            'date_asc': ('date asc', 'Ngày cũ nhất'),
            'amount_desc': ('amount desc', 'Số tiền cao nhất'),
            'amount_asc': ('amount asc', 'Số tiền thấp nhất'),
        }
        order = sort_options.get(sortby, sort_options['date_desc'])[0]

        total = Payment.search_count(domain)
        pager = portal_pager(
            url='/my/donations',
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=total,
            page=page,
            step=20,
        )

        payments = Payment.search(domain, order=order, limit=20, offset=pager['offset'])

        # Tổng hợp theo dự án
        by_project = defaultdict(lambda: {'name': '', 'count': 0, 'total_vnd': 0.0, 'total_usd': 0.0})
        all_payments = Payment.search(domain)
        grand_total_vnd = 0.0
        grand_total_usd = 0.0

        for p in all_payments:
            project_name = p.project_task_id.name if p.project_task_id else 'Dâng hiến chung'
            by_project[project_name]['name'] = project_name
            by_project[project_name]['count'] += 1
            by_project[project_name]['total_vnd'] += p.amount or 0.0
            if p.pay_currency_id and p.pay_currency_id.name == 'USD':
                by_project[project_name]['total_usd'] += p.foreign_amount or 0.0
                grand_total_usd += p.foreign_amount or 0.0
            grand_total_vnd += p.amount or 0.0

        values = {
            'employee': employee,
            'payments': payments,
            'pager': pager,
            'by_project': dict(by_project),
            'grand_total_vnd': grand_total_vnd,
            'grand_total_usd': grand_total_usd,
            'total_count': total,
            'date_begin': date_begin,
            'date_end': date_end,
            'sortby': sortby,
            'sort_options': sort_options,
            'page_name': 'donor',
        }
        return request.render('donor_portal.portal_donor_list', values)

    @http.route(['/my/donations/<int:payment_id>'],
                type='http', auth='user', website=True)
    def portal_donor_detail(self, payment_id, **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.render('donor_portal.donor_not_found')

        payment = request.env['account.payment'].sudo().search([
            ('id', '=', payment_id),
            ('benefactor_id', '=', employee.id),
            ('state', '=', 'posted'),
        ], limit=1)

        if not payment:
            return request.redirect('/my/donations')

        values = {
            'employee': employee,
            'payment': payment,
            'page_name': 'donor',
        }
        return request.render('donor_portal.portal_donor_detail', values)
