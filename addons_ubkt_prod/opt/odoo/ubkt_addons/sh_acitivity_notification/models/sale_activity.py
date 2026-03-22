# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import html2plaintext


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    text_note = fields.Char("Notes In Char format ",
                            compute='_compute_html_to_char_note')

    def _compute_html_to_char_note(self):
        if self:
            for rec in self:
                if rec.note:
                    rec.text_note = html2plaintext(rec.note)
                else:
                    rec.text_note = ''

    @api.model
    def notify_mail_activity_fun(self):

        template = self.env.ref(
            'sh_acitivity_notification.template_mail_activity_due_notify_email'
        )
        notify_create_user_template = self.env.ref(
            'sh_acitivity_notification.template_mail_activity_due_notify_email_create_user'
        )
        company_object = self.env['res.company'].search(
            [('activity_due_notification', '=', True)], limit=1)
        if template and company_object and company_object.activity_due_notification:

            activity_obj = self.env['mail.activity'].search([])

            if activity_obj:
                for record in activity_obj:
                    if record.date_deadline and record.user_id and record.user_id.id != self.env.ref(
                            'base.user_root'
                    ).id and record.user_id.commercial_partner_id and record.user_id.commercial_partner_id.email:

                        # On Due Date
                        if company_object.ondue_date_notify:

                            if datetime.strptime(
                                    str(record.date_deadline),
                                    DEFAULT_SERVER_DATE_FORMAT).date(
                                    ) == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_due:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref(
                                            'base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On After First Notify
                        if company_object.after_first_notify and company_object.enter_after_first_notify:
                            after_date = datetime.strptime(
                                str(record.date_deadline),
                                DEFAULT_SERVER_DATE_FORMAT).date() + timedelta(
                                    days=company_object.
                                    enter_after_first_notify)

                            if after_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_after_first:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref(
                                            'base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On After Second Notify
                        if company_object.after_second_notify and company_object.enter_after_second_notify:
                            after_date = datetime.strptime(
                                str(record.date_deadline),
                                DEFAULT_SERVER_DATE_FORMAT).date() + timedelta(
                                    days=company_object.
                                    enter_after_second_notify)

                            if after_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_after_second:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref(
                                            'base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On Before First Notify
                        if company_object.before_first_notify and company_object.enter_before_first_notify:
                            before_date = datetime.strptime(
                                str(record.date_deadline),
                                DEFAULT_SERVER_DATE_FORMAT).date() - timedelta(
                                    days=company_object.
                                    enter_before_first_notify)

                            if before_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_before_first:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref(
                                            'base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On Before Second Notify
                        if company_object.before_second_notify and company_object.enter_before_second_notify:
                            before_date = datetime.strptime(
                                str(record.date_deadline),
                                DEFAULT_SERVER_DATE_FORMAT).date() - timedelta(
                                    days=company_object.
                                    enter_before_second_notify)

                            if before_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_before_second:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref(
                                            'base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
