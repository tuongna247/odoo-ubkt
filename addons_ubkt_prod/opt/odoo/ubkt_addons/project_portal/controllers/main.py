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

    @http.route(['/my/project/dashboard'], type='http', auth="public", website=True)
    def portal_project_task_page(self, report_type=None, access_token=None, message=False, download=False, **kw):
        _logger.info('[debug] portal_project_task_page Start')
        projects = request.env['project.project'].search([], order='id asc')
        all_task_stage = request.env['project.task.type'].search([('active', '=', True), ('project_ids', '!=', False)], order='sequence asc')
        print(len(all_task_stage))
        print(all_task_stage.mapped('project_ids'))
        project_stage_task = []
        for project in projects:
            data = {
                'name': project.name
            }
            task_type = project.type_ids.sorted(lambda r: r.sequence)
            count_task = []
            for type in task_type:
                task = {}
                tasks = request.env['project.task'].search_count([('project_id', '=', project.id), ('stage_id', '=', type.id), ('kanban_state', '=', 'normal')])
                task['name'] = type.name
                task['number'] = tasks
                count_task.append(task)
            data['count_task'] = count_task
            project_stage_task.append(data)

        dashboard_1 = []
        data_text = {
            'normal': 'Đang thực hiện',
            'done': 'Hoàn tất',
            'blocked': 'Chờ giúp'
        }
        for type in data_text:
            data_all_project = {
                'name': data_text[type]
            }
            count_task_1 = []
            for project in projects:
                tasks_1 = request.env['project.task'].search_count(
                    [('project_id', '=', project.id), ('kanban_state', '=', type)])
                count_task_1.append(tasks_1)
            data_all_project['count_task'] = count_task_1
            dashboard_1.append(data_all_project)

        import pprint
        pprint.pprint(dashboard_1)

        task_year_frist = request.env['project.task'].search([('date_assign', '!=', False)], order='date_assign asc', limit=1)
        task_year_last = request.env['project.task'].search([('date_assign', '!=', False)], order='date_assign desc', limit=1)
        all_task = request.env['project.task'].search([('date_assign', '!=', False)])
        year_start = 2019
        year_end = 2022

        chart_dashboard = []

        if task_year_frist and task_year_last:
            year_start = task_year_frist.date_assign.year
            year_end = task_year_last.date_assign.year
        year = list(range(year_start, year_end + 1))

        color = ['red', 'green', 'blue']
        stt = 0
        for project in projects:
            chart = {
                'project_name': project.name,
                'color': color[stt]
            }
            chart_data = []
            for x in range(year_start, year_end + 1):
                task_for_this_year = all_task.filtered(lambda r: r.date_assign.year == x and r.project_id == project)
                chart_data.append(len(task_for_this_year))
            chart['count_task'] = chart_data
            chart_dashboard.append(chart)
            stt += 1
            print(stt)
        print('1==1-1-1-1-', year)
        pprint.pprint(chart_dashboard)

        return request.render('project_portal.project_portal_dashboard', {
            'project': projects,
            'project_stage_task': project_stage_task,
            'dashboard_1': dashboard_1,
            'year': year,
            'chart_dashboard': chart_dashboard
        })
