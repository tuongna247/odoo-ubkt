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
        """Tìm hr.employee của user hiện tại qua address_home_id hoặc user_id.
           Admin (uid=2) xem được tất cả — trả về False để dùng domain riêng.
        """
        partner = request.env.user.partner_id
        employee = request.env['hr.employee'].sudo().search([
            '|',
            ('address_home_id', '=', partner.id),
            ('user_id', '=', request.env.user.id),
        ], limit=1)
        return employee

    def _is_admin(self):
        return request.env.user.has_group('base.group_system')

    @http.route(['/my/donations', '/my/donations/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_donor_list(self, page=1, date_begin=None, date_end=None, sortby=None, benefactor_id=None, search=None, **kw):
        employee = self._get_current_employee()
        is_admin = self._is_admin()

        if not employee and not is_admin:
            return request.render('donor_portal.donor_not_found')

        Payment = request.env['account.payment'].sudo()

        # Admin xem được tất cả hoặc lọc theo ân nhân cụ thể
        if is_admin:
            domain = [('state', '=', 'posted'), ('benefactor_id', '!=', False)]
            if benefactor_id:
                domain += [('benefactor_id', '=', int(benefactor_id))]
            if search:
                # Tìm employee theo tên trước
                matched_employees = request.env['hr.employee'].sudo().search([('name', 'ilike', search)])
                domain += [('benefactor_id', 'in', matched_employees.ids)]
        else:
            domain = [
                ('benefactor_id', '=', employee.id),
                ('state', '=', 'posted'),
            ]
            if search:
                domain += [('description', 'ilike', search)]
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
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search': search, 'benefactor_id': benefactor_id},
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

        # Danh sách ân nhân cho admin lọc
        all_benefactors = []
        if is_admin:
            all_benefactors = request.env['hr.employee'].sudo().search([
                ('id', 'in', Payment.search([('state', '=', 'posted'), ('benefactor_id', '!=', False)]).mapped('benefactor_id').ids)
            ])

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
            'is_admin': is_admin,
            'all_benefactors': all_benefactors,
            'selected_benefactor_id': int(benefactor_id) if benefactor_id else None,
            'search': search or '',
        }
        return request.render('donor_portal.portal_donor_list', values)

    @http.route(['/my/donations/<int:payment_id>'],
                type='http', auth='user', website=True)
    def portal_donor_detail(self, payment_id, **kw):
        employee = self._get_current_employee()
        is_admin = self._is_admin()

        if not employee and not is_admin:
            return request.render('donor_portal.donor_not_found')

        # Admin xem được tất cả, ân nhân chỉ xem của mình
        if is_admin:
            domain = [('id', '=', payment_id), ('state', '=', 'posted')]
        else:
            domain = [('id', '=', payment_id), ('benefactor_id', '=', employee.id), ('state', '=', 'posted')]

        payment = request.env['account.payment'].sudo().search(domain, limit=1)

        if not payment:
            return request.redirect('/my/donations')

        task = payment.project_task_id
        attachments = task.attachment_id if task else request.env['ir.attachment']

        values = {
            'employee': employee or payment.benefactor_id,
            'payment': payment,
            'task': task,
            'attachments': attachments,
            'page_name': 'donor',
            'is_admin': is_admin,
        }
        return request.render('donor_portal.portal_donor_detail', values)
