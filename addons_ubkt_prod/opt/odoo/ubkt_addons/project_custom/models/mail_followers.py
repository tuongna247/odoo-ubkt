# -*- coding: utf-8 -*-

from odoo import api, models, _
import logging
_logger = logging.getLogger(__name__)

class MailFollowers(models.Model):
    _inherit = "mail.followers"

    def _get_recipient_data(self, records, message_type, subtype_id, pids=None):
        _logger.info('[Debug] mail_followers _get_recipient_data start ')

        res = []
        if not pids:
            return res

        self.env['mail.followers'].flush(['partner_id', 'subtype_ids'])
        self.env['mail.message.subtype'].flush(['internal'])
        self.env['res.users'].flush(['notification_type', 'active', 'partner_id', 'groups_id'])
        self.env['res.partner'].flush(['active', 'partner_share'])
        self.env['res.groups'].flush(['users'])
        if records and subtype_id:
            query = """
SELECT DISTINCT ON (pid) * FROM (
    WITH sub_followers AS (
        SELECT fol.partner_id,
               coalesce(subtype.internal, false) as internal
          FROM mail_followers fol
          JOIN mail_followers_mail_message_subtype_rel subrel ON subrel.mail_followers_id = fol.id
          JOIN mail_message_subtype subtype ON subtype.id = subrel.mail_message_subtype_id
         WHERE subrel.mail_message_subtype_id = %s
           AND fol.res_model = %s
           AND fol.res_id IN %s
           AND fol.partner_id IN %s

     UNION ALL

        SELECT id,
               FALSE
          FROM res_partner
         WHERE id=ANY(%s)
    )
    SELECT partner.id as pid,
           partner.active as active,
           partner.partner_share as pshare,
           users.notification_type AS notif,
           array_agg(groups_rel.gid) AS groups
      FROM res_partner partner
 LEFT JOIN res_users users ON users.partner_id = partner.id
                          AND users.active
 LEFT JOIN res_groups_users_rel groups_rel ON groups_rel.uid = users.id
      JOIN sub_followers ON sub_followers.partner_id = partner.id
                        AND NOT (sub_followers.internal AND partner.partner_share)
        GROUP BY partner.id,
                 users.notification_type
) AS x
ORDER BY pid, notif
"""
            params = [subtype_id, records._name, tuple(records.ids), tuple(pids), list(pids) or []]
            _logger.info('[Debug] mail_followers _get_recipient_data params ' + str(params))

            self.env.cr.execute(query, tuple(params))
            res = self.env.cr.fetchall()
        elif pids:
            params = []
            query_pid = """
SELECT partner.id as pid,
partner.active as active, partner.partner_share as pshare,
users.notification_type AS notif, NULL AS groups
FROM res_partner partner
LEFT JOIN res_users users ON users.partner_id = partner.id AND users.active
WHERE partner.id IN %s"""
            params.append(tuple(pids))
            query = 'SELECT DISTINCT ON (pid) * FROM (%s) AS x ORDER BY pid, notif' % query_pid
            self.env.cr.execute(query, tuple(params))
            res = self.env.cr.fetchall()
        else:
            res = []
        
        return res
