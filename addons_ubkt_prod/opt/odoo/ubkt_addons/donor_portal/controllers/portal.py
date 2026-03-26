# -*- coding: utf-8 -*-
import json
from urllib.parse import quote as url_quote
from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import defaultdict


class DonorPortal(CustomerPortal):

    # Bank info for VietQR — update these to match UBKT's actual bank account
    _BANK_CODE = 'MB'
    _BANK_ACCOUNT = '1234567890'
    _ACCOUNT_NAME = 'UY BAN KIEN THIET'

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

    # ─── Dashboard ───────────────────────────────────────────────────────────

    @http.route(['/my/', '/my/dashboard'], type='http', auth='user', website=True)
    def portal_dashboard(self, **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.redirect('/my/donations')

        Payment = request.env['account.payment'].sudo()
        my_payments = Payment.search([('benefactor_id', '=', employee.id), ('state', '=', 'posted')])
        my_tasks = my_payments.mapped('project_task_id')

        grand_total_vnd = sum(my_payments.mapped('amount'))
        map_tasks = [
            {'province': t.province_code, 'name': t.partner_id.name or t.name}
            for t in my_tasks if t.province_code
        ]
        featured_clips = my_tasks.filtered(lambda t: t.featured_video_url)[:5]

        values = {
            'employee': employee,
            'project_count': len(my_tasks),
            'believers_total': sum(my_tasks.mapped('believers_capacity')),
            'bible_classes_total': sum(my_tasks.mapped('bible_classes_count')),
            'gospel_total': sum(my_tasks.mapped('gospel_outreach_count')),
            'new_believers_total': sum(my_tasks.mapped('new_believers_count')),
            'grand_total_vnd': grand_total_vnd,
            'map_tasks_json': json.dumps(map_tasks),
            'featured_clips': featured_clips,
            'page_name': 'dashboard',
        }
        return request.render('donor_portal.portal_dashboard', values)

    # ─── My Projects ─────────────────────────────────────────────────────────

    @http.route(['/my/projects'], type='http', auth='user', website=True)
    def portal_my_projects(self, **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.redirect('/my/donations')

        my_task_ids = request.env['account.payment'].sudo().search([
            ('benefactor_id', '=', employee.id), ('state', '=', 'posted')
        ]).mapped('project_task_id.id')
        my_tasks = request.env['project.task'].sudo().search([('id', 'in', my_task_ids)])

        values = {
            'employee': employee,
            'tasks': my_tasks,
            'page_name': 'my_projects',
        }
        return request.render('donor_portal.portal_my_projects', values)

    @http.route(['/my/projects/<int:task_id>'], type='http', auth='user', website=True)
    def portal_project_detail(self, task_id, **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.redirect('/my/donations')

        # Security: donor must have a payment linked to this task
        has_access = request.env['account.payment'].sudo().search_count([
            ('benefactor_id', '=', employee.id),
            ('project_task_id', '=', task_id),
            ('state', '=', 'posted'),
        ])
        if not has_access:
            return request.redirect('/my/projects')

        task = request.env['project.task'].sudo().browse(task_id)
        if not task.exists():
            return request.redirect('/my/projects')

        task_payments = request.env['account.payment'].sudo().search([
            ('benefactor_id', '=', employee.id),
            ('project_task_id', '=', task_id),
            ('state', '=', 'posted'),
        ])

        values = {
            'employee': employee,
            'task': task,
            'task_payments': task_payments,
            'page_name': 'my_projects',
        }
        return request.render('donor_portal.portal_project_detail', values)

    # ─── Explore ─────────────────────────────────────────────────────────────

    @http.route(['/my/explore'], type='http', auth='user', website=True)
    def portal_explore(self, **kw):
        open_tasks = request.env['project.task'].sudo().search([
            ('available_for_donation', '=', True),
            ('approved_data_entry', '=', True),
        ])
        values = {
            'tasks': open_tasks,
            'page_name': 'explore',
        }
        return request.render('donor_portal.portal_explore', values)

    # ─── Donation Flow ────────────────────────────────────────────────────────

    @http.route(['/my/donate/<int:task_id>'], type='http', auth='user', website=True)
    def portal_donate_form(self, task_id, **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.redirect('/my/explore')

        task = request.env['project.task'].sudo().search([
            ('id', '=', task_id),
            ('available_for_donation', '=', True),
        ], limit=1)
        if not task:
            return request.redirect('/my/explore')

        values = {
            'task': task,
            'employee': employee,
            'page_name': 'explore',
        }
        return request.render('donor_portal.portal_donate_form', values)

    @http.route(['/my/donate/<int:task_id>/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_donate_submit(self, task_id, amount=0, payment_method='bank', note='', **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.redirect('/my/explore')

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0

        if amount <= 0:
            return request.redirect('/my/donate/%d' % task_id)

        task = request.env['project.task'].sudo().search([
            ('id', '=', task_id), ('available_for_donation', '=', True)
        ], limit=1)
        if not task:
            return request.redirect('/my/explore')

        donor_name = employee.name or request.env.user.name
        transfer_note = note.strip() if note.strip() else '%s dang hien %s' % (donor_name, task.name)

        qr_url = 'https://img.vietqr.io/image/%s-%s-compact.jpg?amount=%d&addInfo=%s&accountName=%s' % (
            self._BANK_CODE, self._BANK_ACCOUNT,
            int(amount),
            url_quote(transfer_note),
            url_quote(self._ACCOUNT_NAME),
        )

        values = {
            'task': task,
            'employee': employee,
            'amount': amount,
            'payment_method': payment_method,
            'note': transfer_note,
            'qr_url': qr_url,
            'bank_code': self._BANK_CODE,
            'bank_account': self._BANK_ACCOUNT,
            'account_name': self._ACCOUNT_NAME,
            'page_name': 'explore',
        }
        return request.render('donor_portal.portal_donate_confirm', values)

    @http.route(['/my/donate/thankyou'], type='http', auth='user', website=True)
    def portal_donate_thankyou(self, task_id=None, **kw):
        task = None
        if task_id:
            task = request.env['project.task'].sudo().browse(int(task_id))
            if not task.exists():
                task = None
        values = {
            'task': task,
            'page_name': 'explore',
            'bible_verse': 'Người nào gieo ít thì gặt ít, người nào gieo nhiều thì gặt nhiều. — 2 Cô-rinh-tô 9:6',
        }
        return request.render('donor_portal.portal_donate_thankyou', values)

    # ─── Personal Goals ───────────────────────────────────────────────────────

    @http.route(['/my/goals'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_goals(self, year=None, target_projects=0, target_amount=0, prayer_note='', **kw):
        employee = self._get_current_employee()
        if not employee:
            return request.redirect('/my/donations')

        current_year = fields.Date.today().year
        goal_year = int(year) if year else current_year

        GoalModel = request.env['donor.goal'].sudo()

        if request.httprequest.method == 'POST':
            existing = GoalModel.search([('employee_id', '=', employee.id), ('year', '=', goal_year)], limit=1)
            vals = {
                'employee_id': employee.id,
                'year': goal_year,
                'target_projects': int(target_projects or 0),
                'target_amount': float(target_amount or 0),
                'prayer_note': prayer_note,
            }
            if existing:
                existing.write(vals)
            else:
                GoalModel.create(vals)

        goal = GoalModel.search([('employee_id', '=', employee.id), ('year', '=', goal_year)], limit=1)

        # Compute current year progress
        Payment = request.env['account.payment'].sudo()
        year_payments = Payment.search([
            ('benefactor_id', '=', employee.id),
            ('state', '=', 'posted'),
            ('date', '>=', '%d-01-01' % goal_year),
            ('date', '<=', '%d-12-31' % goal_year),
        ])
        current_amount = sum(year_payments.mapped('amount'))
        current_project_ids = year_payments.mapped('project_task_id.id')
        current_projects = len(set(current_project_ids))

        values = {
            'employee': employee,
            'goal': goal,
            'goal_year': goal_year,
            'current_year': current_year,
            'current_amount': current_amount,
            'current_projects': current_projects,
            'page_name': 'goals',
        }
        return request.render('donor_portal.portal_goals', values)
