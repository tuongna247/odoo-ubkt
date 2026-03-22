# -*- coding: utf-8 -*-

import time
import datetime
from odoo import api, models, _
from odoo.exceptions import UserError
# import logging
# _logger = logging.getLogger(__name__)

class ReportCashBook(models.AbstractModel):
    _name = 'report.account_report.report_cashbook_modify_initial_balance'
    _description = 'Cash Book Modify'

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        """
               :param:
                       accounts: the recordset of accounts
                       init_balance: boolean value of initial_balance
                       sortby: sorting by date or partner and journal
                       display_account: type of account(receivable, payable and both)

               Returns a dictionary of accounts with following key and value {
                       'code': account code,
                       'name': account name,
                       'debit': sum of total debit amount,
                       'credit': sum of total credit amount,
                       'balance': total balance,
                       'amount_currency': sum of amount_currency,
                       'move_lines': list of move line
               }
               """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}
        # move_lines_123 = {x: [] for x in accounts.ids}
        formatted_date_from = datetime.datetime.strptime(self.env.context.get('date_from'), '%Y-%m-%d').strftime('%y%m%d')
        formatted_date_to = datetime.datetime.strptime(self.env.context.get('date_to'), '%Y-%m-%d').strftime('%y%m%d')

        # Prepare initial sql query and Get the initial move lines
        data = {}
        data_1 = {}
        account_data_journal = {}
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False,initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""
                    SELECT 0 AS lid, 
                    l.account_id AS account_id, '' AS ldate, '' AS lcode, 
                    0.0 AS amount_currency,'' AS lref,'Initial Balance' AS lname, 
                    COALESCE(SUM(l.credit),0.0) AS credit,COALESCE(SUM(l.debit),0.0) AS debit,COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) as balance, 
                    '' AS lpartner_id,'' AS move_name, '' AS currency_code,NULL AS currency_id,'' AS partner_name,
                    '' AS mmove_id, '' AS invoice_id, '' AS invoice_type,'' AS invoice_number
                    FROM account_move_line l 
                    INNER JOIN account_move m ON (l.move_id = m.id) 
                    INNER JOIN account_payment ap on m.id = ap.move_id 
                    LEFT JOIN res_currency c ON (l.currency_id = c.id) 
                    LEFT JOIN res_partner p ON (l.partner_id = p.id) 
                    JOIN account_journal j ON (l.journal_id = j.id) 
                    JOIN account_account acc ON (l.account_id = acc.id) 
                    WHERE l.account_id IN %s""" + filters + 'GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)

            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)
            sql_123 = ("""
                    SELECT 0 AS lid, 
                    l.account_id AS account_id, l.journal_id as journal_id, l.payment_id as lpayment, '' AS ldate, '' AS lcode, 
                    0.0 AS amount_currency,'' AS lref,
                    COALESCE(SUM(l.credit),0.0) AS credit,COALESCE(SUM(l.debit),0.0) AS debit,COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) as balance, 
                    '' AS lpartner_id,'' AS move_name, '' AS currency_code,NULL AS currency_id,'' AS partner_name,
                    '' AS mmove_id, '' AS invoice_id, '' AS invoice_type,'' AS invoice_number
                    FROM account_move_line l 
                    INNER JOIN account_move m ON (l.move_id = m.id) 
                    INNER JOIN account_payment ap on m.id = ap.move_id 
                    LEFT JOIN res_currency c ON (l.currency_id = c.id) 
                    LEFT JOIN res_partner p ON (l.partner_id = p.id) 
                    JOIN account_journal j ON (l.journal_id = j.id) 
                    JOIN account_account acc ON (l.account_id = acc.id) 
                    WHERE l.account_id IN %s""" + filters + 'GROUP BY l.account_id, l.journal_id, l.payment_id')

            params = (tuple(accounts.ids),) + tuple(init_where_params)

            cr.execute(sql_123, params)
            for row_1 in cr.dictfetchall():
                # payment = self.env['account.payment'].browse(row_1['lpayment'])
                # if payment and (payment.is_advance is True or payment.is_internal_transfer is True):
                if row_1['journal_id'] not in data:
                    data[row_1['journal_id']] = row_1['debit'] - row_1['credit']
                    data_1[row_1['journal_id']] = row_1['debit'] - row_1['credit']
                else:
                    data[row_1['journal_id']] += row_1['debit'] - row_1['credit']
                    data_1[row_1['journal_id']] += row_1['debit'] - row_1['credit']

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
        if not accounts:
            journals = self.env['account.journal'].search([('type', '=', 'cash')])
            accounts = []
            for journal in journals:
                accounts.append(journal.payment_credit_account_id.id)
            accounts = self.env['account.account'].search([('id', 'in', accounts)])

        sql = ('''SELECT l.id AS lid, l.journal_id as journal_id, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.payment_id as lpayment, l.currency_id, l.amount_currency, l.ref AS lref, ap.paper_payment_code as lpaper_payment_code, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                        m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
                        FROM account_move_line l\
                        JOIN account_move m ON (l.move_id=m.id)\
                        INNER JOIN account_payment ap on m.id = ap.move_id \
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        JOIN account_account acc ON (l.account_id = acc.id) \
                        WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.journal_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, ap.paper_payment_code, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)

        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)
            payment = self.env['account.payment'].browse(row['lpayment'])
            if payment:
                row['lname'] = payment.description
                row['move_name'] = payment.name_seq
            rpw_1 = row
            # if payment and payment.is_advance is False and payment.is_internal_transfer is False:
            if 'journal_id' not in 'account_data_journal' and rpw_1['lid'] != 0:
                if rpw_1['journal_id'] not in account_data_journal:
                    account_data_journal[rpw_1['journal_id']] = rpw_1['debit'] - rpw_1['credit']
                else:
                    account_data_journal[rpw_1['journal_id']] += rpw_1['debit'] - rpw_1['credit']

                if rpw_1['journal_id'] not in data_1:
                    data_1[rpw_1['journal_id']] = rpw_1['debit'] - rpw_1['credit']
                else:
                    data_1[rpw_1['journal_id']] += rpw_1['debit'] - rpw_1['credit']
        journal_name = {}
        for jour in data_1.keys():
            journal_data_name = self.env['account.journal'].browse(jour)
            if journal_data_name:
                journal_name[jour] = journal_data_name.name
            else:
                journal_name[jour] = ''
            if jour not in data:
                data[jour] = 0
            if jour not in account_data_journal:
                account_data_journal[jour] = 0
        # Calculate the debit, credit and balance for Accounts
        account_res = []

        l_toatl_1 = l_toatl_2 = l_toatl_3 = l_toatl_4 = l_toatl_5 = l_toatl_6 = 0
        l_in_total_1 = l_in_total_2 = l_in_total_3 = l_in_total_4 = l_in_total_5 = l_in_total_6 = 0

        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            res['debit_credit'] = 0
            for line in res.get('move_lines'):
                if line.get('ldate') and line['ldate'] != '':
                    row_date = None
                    if isinstance(line['ldate'], str) and line['ldate'] != '':
                        row_date = datetime.datetime.strptime(line['ldate'], '%Y-%m-%d').strftime('%y%m%d')
                    elif isinstance(line['ldate'], datetime.date):
                        row_date = line['ldate'].strftime('%y%m%d')
                    if row_date != None:
                        if formatted_date_from <= row_date <= formatted_date_to:
                            if line.get('lpayment'):
                                payment = self.env['account.payment'].browse(line['lpayment'])
                                if payment and (payment.is_advance is True or payment.is_internal_transfer is True):
                                    if payment.is_advance is True:
                                        l_in_total_3 += line['debit']
                                        l_in_total_4 += line['credit']
                                    if payment.is_internal_transfer is True:
                                        l_in_total_5 += line['debit']
                                        l_in_total_6 += line['credit']
                                else:
                                    l_in_total_1 += line['debit']
                                    l_in_total_2 += line['credit']
                            else:
                                l_in_total_1 += line['debit']
                                l_in_total_2 += line['credit']

                if line.get('lpayment'):
                    payment = self.env['account.payment'].browse(line['lpayment'])
                    if payment and (payment.is_advance is True or payment.is_internal_transfer is True):
                        if payment.is_advance is True:
                            line['lpayment_is_advance'] = 1
                            line['lpayment_is_internal_transfer'] = 0
                            l_toatl_3 += line['debit']
                            l_toatl_4 += line['credit']
                        if payment.is_internal_transfer is True:
                            line['lpayment_is_internal_transfer'] = 1
                            line['lpayment_is_advance'] = 0
                            l_toatl_5 += line['debit']
                            l_toatl_6 += line['credit']
                    else:
                        line['lpayment_is_advance'] = 0
                        line['lpayment_is_internal_transfer'] = 0
                        l_toatl_1 += line['debit']
                        l_toatl_2 += line['credit']
                else:
                    line['lpayment_is_advance'] = 0
                    line['lpayment_is_internal_transfer'] = 0
                    l_toatl_1 += line['debit']
                    l_toatl_2 += line['credit']
                if line.get('lid') and line['lid'] != 0:
                    res['debit_credit'] += line['debit'] - line['credit']
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']

            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        l_total = {
            'l_toatl_1': l_toatl_1,
            'l_toatl_2': l_toatl_2,
            'l_toatl_3': l_toatl_3,
            'l_toatl_4': l_toatl_4,
            'l_toatl_5': l_toatl_5,
            'l_toatl_6': l_toatl_6,
            'l_in_total_1': l_in_total_1,
            'l_in_total_2': l_in_total_2,
            'l_in_total_3': l_in_total_3,
            'l_in_total_4': l_in_total_4,
            'l_in_total_5': l_in_total_5,
            'l_in_total_6': l_in_total_6,
        }

        return account_res, l_total, journal_name, data, account_data_journal, data_1

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        init_balance = data['form'].get('initial_balance', True)
        display_account = data['form'].get('display_account')

        sortby = data['form'].get('sortby', 'sort_date')
        codes = []

        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        account_ids = data['form']['account_ids']
        accounts = self.env['account.account'].search([('id', 'in', account_ids)])
        if not accounts:
            journals = self.env['account.journal'].search([('type', '=', 'cash')])
            accounts = []
            for journal in journals:
                accounts.append(journal.payment_credit_account_id.id)
            accounts = self.env['account.account'].search([('id', 'in', accounts)])
        record, l_total, journal_1, journal_2, journal_3, journal_4 = self.with_context(data['form'].get('comparison_context', {}))._get_account_move_entry(accounts, init_balance, sortby, display_account)
        journal_data = {}
        for account in record:
            for journal in account['move_lines']:

                if journal.get('journal_id'):
                    journal_env = self.env['account.journal'].browse(journal['journal_id'])
                    if journal_env and journal_env.name not in journal_data:
                        sub_data = {
                            'name': journal_env.name,
                            'l1': 0,
                            'l2': 0,
                            'l3': 0,
                            'l4': 0,
                            'l5': 0,
                            'l6': 0,
                            'l7': 0,
                            'move_line': []
                        }
                        journal_data[journal_env.name] = sub_data
                        if journal['lpayment_is_advance'] == 1:
                            journal_data[journal_env.name]['l3'] += journal['debit']
                            journal_data[journal_env.name]['l4'] += journal['credit']
                            journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                        elif journal['lpayment_is_internal_transfer'] == 1:
                            # journal_data[journal_env.name]['l5'] += journal['debit']
                            # journal_data[journal_env.name]['l6'] += journal['credit']
                            # journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                            journal_data[journal_env.name]['l6'] += journal['debit']
                            journal_data[journal_env.name]['l5'] += journal['credit']
                            journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                        else:
                            journal_data[journal_env.name]['l1'] += journal['debit']
                            journal_data[journal_env.name]['l2'] += journal['credit']
                            journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                        journal_data[journal_env.name]['move_line'].append(journal)
                    else:
                        if journal['lpayment_is_advance'] == 1:
                            journal_data[journal_env.name]['l3'] += journal['debit']
                            journal_data[journal_env.name]['l4'] += journal['credit']
                            journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                        elif journal['lpayment_is_internal_transfer'] == 1:
                        #     journal_data[journal_env.name]['l5'] += journal['debit']
                        #     journal_data[journal_env.name]['l6'] += journal['credit']
                        #     journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                            journal_data[journal_env.name]['l6'] += journal['debit']
                            journal_data[journal_env.name]['l5'] += journal['credit']
                            journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                        else:
                            journal_data[journal_env.name]['l1'] += journal['debit']
                            journal_data[journal_env.name]['l2'] += journal['credit']
                            journal_data[journal_env.name]['l7'] += journal['debit'] - journal['credit']
                        journal_data[journal_env.name]['move_line'].append(journal)
        company = self.env['res.company'].search([], limit=1)
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data['form'],
            'company': company,
            'docs': docs,
            'time': time,
            'Accounts': record,
            'l_total': l_total,
            'print_journal': codes,
            'init_balance': init_balance,
            'journal_data': journal_data,
            'journal_name':  dict(sorted(journal_1.items(), key=lambda item: item[0])),
            'journal_2': dict(sorted(journal_2.items(), key=lambda item: item[0])),
            'journal_3': dict(sorted(journal_3.items(), key=lambda item: item[0])),
            'journal_4': dict(sorted(journal_4.items(), key=lambda item: item[0]))
        }
