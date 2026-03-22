# -*- coding: utf-8 -*-

import base64

from odoo import api, models, tools, _
from odoo.exceptions import UserError
from .project_constants import *
import logging
_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = "mail.template"

    # def generate_email(self, res_ids, fields):
    #     res = super().generate_email(res_ids, fields)

    #     if self.model not in ['project.task']:
    #         return res

    #     records = self.env[self.model].browse(res_ids)
    #     for record in records:
    #         record_data = res[record.id]
    #         attachments = record.attachment_id
            
    #         if attachments:
    #             # Template Opinion of the pastor, Template consultations
    #             if record.stage_id.id in (STAGE_ID_PASTOR, STAGE_ID_CONSULT):
    #                 record_data.setdefault('attachments', [])
    #                 record_data['attachments'].clear()
    #                 for attachment in attachments:
    #                     record_data['attachments'].append((attachment.name, attachment.datas))

    #     return res

    def generate_email(self, res_ids, fields):
        _logger.info('[Debug] project_custom generate_email Start ')
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        results = dict()
        for lang, (template, template_res_ids) in self._classify_per_lang(res_ids).items():
            for field in fields:
                generated_field_values = template._render_field(
                    field, template_res_ids,
                    options={'render_safe': field == 'subject'},
                    post_process=(field == 'body_html')
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(field in fields for field in ['email_to', 'partner_to', 'email_cc']):
                results = template.generate_recipients(results, template_res_ids)
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get('body_html'):
                    values['body'] = tools.html_sanitize(values['body_html'])
                # technical settings
                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )

            # Add report in attachments: generate once for all template_res_ids
            if template.report_template:
                if self.model not in ['project.task']:
                    _logger.info('[Debug] Generate the attachment')
                    for res_id in template_res_ids:
                        attachments = []
                        report_name = template._render_field('report_name', [res_id])[res_id]
                        report = template.report_template
                        report_service = report.report_name

                        if report.report_type in ['qweb-html', 'qweb-pdf']:
                            result, format = report._render_qweb_pdf([res_id])
                        else:
                            res = report._render([res_id])
                            if not res:
                                raise UserError(_('Unsupported report type %s found.', report.report_type))
                            result, format = res

                        # TODO in trunk, change return format to binary to match message_post expected format
                        result = base64.b64encode(result)
                        if not report_name:
                            report_name = 'report.' + report_service
                        ext = "." + format
                        if not report_name.endswith(ext):
                            report_name += ext
                        attachments.append((report_name, result))
                        results[res_id]['attachments'] = attachments
                else:
                    _logger.info('[Debug] Not generate the attachment')
                    # result = base64.b64encode(result)
                    records = self.env[self.model].browse(res_ids)
                    for record in records:
                        record_data = results[record.id]
                        attachments = record.attachment_id
                        
                        if attachments:
                            # Template Opinion of the pastor, Template consultations
                            if record.stage_id.id in (STAGE_ID_PASTOR, STAGE_ID_CONSULT):
                                record_data.setdefault('attachments', [])
                                record_data['attachments'].clear()
                                for attachment in attachments:
                                    record_data['attachments'].append((attachment.name, attachment.datas))

        return multi_mode and results or results[res_ids[0]]
