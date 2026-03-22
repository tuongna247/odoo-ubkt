# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ICMForm(models.Model):
    _inherit = 'project.task'

    icm_flag = fields.Boolean(string='ICM', default=False, store=True)

    # Management Information
    icm_spintend_name = fields.Char(string='Full name Church Superintendent')
    icm_spintend_phone = fields.Char(string='Phone')
    icm_spintend_email = fields.Char(string='Email')
    icm_spintend_marital = fields.Selection(string='Marital Status', selection=[
            ('single', 'Single'),
            ('married', 'Married'),
        ], default='')
    icm_spintend_children = fields.Integer(string='No. of children')
    icm_spintend_participate = fields.Text(string='Participate in bible training programs')
    icm_spintend_no_years = fields.Integer(string='Number of years in position')
    icm_spintend_serving = fields.Text(string='Number of years serving the Lord in the church')

    # Land Ownership
    icm_land_ownership = fields.Selection(string='Land ownership', selection=[
            ('church', 'Church'),
            ('others', 'Others'),
        ], default='')
    icm_land_other = fields.Char(string='Other')
    icm_land_obtain = fields.Selection(string='This land is obtain from', selection=[
            ('purchase', 'Purchase'),
            ('donate', 'Donate'),
        ], default='')

    # Community
    icm_population_area = fields.Integer(string='Population of the area (person)')
    icm_near_town = fields.Char(string='Nearest Town or City')
    icm_town_distance = fields.Float(string='Distance from Town (km)')
    icm_near_branch = fields.Char(string='Nearest Branch')
    icm_branch_distance = fields.Float(string='Distance from branch (km)')

    def get_years():
        year_list = []
        current_year = fields.Date.today().strftime("%Y")
        current_year = int(current_year)
        min_year = 1900
        max_year = current_year + 50

        for i in range(min_year, max_year):
            year_list.append((str(i), str(i)))
        return year_list

    # Congregation
    icm_main_language = fields.Char(string='Main Language')
    icm_official_believers = fields.Integer(string='Official number of believers')
    icm_official_adult = fields.Integer(string='Official Adult')
    icm_official_children = fields.Integer(string='Official Children')
    icm_attend_num = fields.Integer(string='Number of people attending')
    icm_attend_adult = fields.Integer(string='Attend Adult')
    icm_attend_children = fields.Integer(string='Attend Children')
    icm_monthly_donate = fields.Float(string='Monthly Donate(vnd)', digits=(25, 0))
    icm_published_year = fields.Selection(get_years(), string='Published Year')

    # Finance Details
    icm_total_build_cost_vnd = fields.Float(string='Total building cost (vnd)', digits=(25, 0))
    icm_total_build_cost_usd = fields.Monetary(string='Total building cost (usd)', readonly=True, currency_field='currency_id')

    # Construction Plan
    icm_completed_works = fields.Integer(string='Months to complete works')
    icm_construct_scale = fields.Selection(string='Construction scale', selection=[
            ('heavy_materials', 'New construction with heavy materials (brick, stone, cement)'),
            ('ligh_materials', 'New construction with light materials (prefabricated house with steel frame)'),
            ('repair', 'Repair'),
        ], default='')
    icm_construct_size = fields.Float(string='Const. size (length x width) (m2)', 
            compute='_compute_construct_size', readonly=True)
    icm_construct_length = fields.Float(string='Construction Length (m)')
    icm_construct_width = fields.Float(string='Construction Width (m)')
    icm_land_size = fields.Float(string='Land Size (length x width) (m2))', 
            compute='_compute_land_size', readonly=True)
    icm_land_length = fields.Float(string='ICM Land Length (m)')
    icm_land_width = fields.Float(string='ICM Land Width (m)')

    # Dedication of the church
    icm_give_effort_vnd = fields.Float(string='Give effort (vnd)', digits=(25, 0))
    icm_give_effort_usd = fields.Monetary(string='Give effort (usd)', readonly=True, currency_field='currency_id')
    icm_donate_materials_vnd = fields.Float(string='Donate Materials (vnd)', digits=(25, 0))
    icm_donate_materials_usd = fields.Monetary(string='Donate Materials (usd)', readonly=True, currency_field='currency_id')
    icm_donate_cash_vnd = fields.Float(string='Donate Cash (vnd)', digits=(25, 0))
    icm_donate_cash_usd = fields.Monetary(string='Donate Cash (usd)', readonly=True, currency_field='currency_id')
    icm_donate_land_vnd = fields.Float(string='Land (vnd)', digits=(25, 0))
    icm_donate_land_usd = fields.Monetary(string='Land (usd)', readonly=True, currency_field='currency_id')
    icm_exchange_rate = fields.Monetary(string='Currency exchange rate 1 usd = vnd', currency_field='currency_id')

    @api.onchange('icm_total_build_cost_vnd')
    def _onchange_icm_total_build_cost_vnd(self):
        self.icm_total_build_cost_usd = self.convert_usd(self.icm_total_build_cost_vnd, self.icm_exchange_rate)

    @api.onchange('icm_give_effort_vnd')
    def _onchange_icm_give_effort_vnd(self):
        self.icm_give_effort_usd = self.convert_usd(self.icm_give_effort_vnd, self.icm_exchange_rate)

    @api.onchange('icm_donate_materials_vnd')
    def _onchange_icm_donate_materials_vnd(self):
        self.icm_donate_materials_usd = self.convert_usd(self.icm_donate_materials_vnd, self.icm_exchange_rate)

    @api.onchange('icm_donate_cash_vnd')
    def _onchange_icm_donate_cash_vnd(self):
        self.icm_donate_cash_usd = self.convert_usd(self.icm_donate_cash_vnd, self.icm_exchange_rate)

    @api.onchange('icm_donate_land_vnd')
    def _onchange_icm_donate_land_vnd(self):
        self.icm_donate_land_usd = self.convert_usd(self.icm_donate_land_vnd, self.icm_exchange_rate)

    def _compute_construct_size(self):
        self.icm_construct_size = self.cal_area(self.icm_construct_length, self.icm_construct_width)

    @api.onchange('icm_construct_length')
    def _onchange_icm_construct_length(self):
        self.icm_construct_size = self.cal_area(self.icm_construct_length, self.icm_construct_width)
    
    @api.onchange('icm_construct_width')
    def _onchange_icm_construct_width(self):
        self.icm_construct_size = self.cal_area(self.icm_construct_length, self.icm_construct_width)

    def _compute_land_size(self):
        self.icm_land_size = self.cal_area(self.icm_land_length, self.icm_land_width)

    @api.onchange('icm_land_length')
    def _onchange_icm_land_length(self):
        self.icm_land_size = self.cal_area(self.icm_land_length, self.icm_land_width)

    @api.onchange('icm_land_width')
    def _onchange_icm_land_width(self):
        self.icm_land_size = self.cal_area(self.icm_land_length, self.icm_land_width)

    def cal_area(self, length, width):
        return length * width

    @api.onchange('icm_exchange_rate')
    def _onchange_icm_exchange_rate(self):
        self.convert_usd_again()
        
    def convert_usd(self, number, exchange_rate):
        if exchange_rate and float(exchange_rate) > 0:
            return number / exchange_rate

    def convert_usd_again(self):
        self.icm_total_build_cost_usd = self.convert_usd(self.icm_total_build_cost_vnd, self.icm_exchange_rate)
        self.icm_give_effort_usd = self.convert_usd(self.icm_give_effort_vnd, self.icm_exchange_rate)
        self.icm_donate_materials_usd = self.convert_usd(self.icm_donate_materials_vnd, self.icm_exchange_rate)
        self.icm_donate_cash_usd = self.convert_usd(self.icm_donate_cash_vnd, self.icm_exchange_rate)
        self.icm_donate_land_usd = self.convert_usd(self.icm_donate_land_vnd, self.icm_exchange_rate)

    def convert_usd_b4save(self, vals):
        exchange_rate = vals.get('icm_exchange_rate')
        if exchange_rate is None:
            exchange_rate = self.icm_exchange_rate

        icm_total_build_cost_vnd = vals.get('icm_total_build_cost_vnd')
        if icm_total_build_cost_vnd is None:
            icm_total_build_cost_vnd = self.icm_total_build_cost_vnd

        icm_give_effort_vnd = vals.get('icm_give_effort_vnd')
        if icm_give_effort_vnd is None:
            icm_give_effort_vnd = self.icm_give_effort_vnd

        icm_donate_materials_vnd = vals.get('icm_donate_materials_vnd')
        if icm_donate_materials_vnd is None:
            icm_donate_materials_vnd = self.icm_donate_materials_vnd

        icm_donate_cash_vnd = vals.get('icm_donate_cash_vnd')
        if icm_donate_cash_vnd is None:
            icm_donate_cash_vnd = self.icm_donate_cash_vnd

        icm_donate_land_vnd = vals.get('icm_donate_land_vnd')
        if icm_donate_land_vnd is None:
            icm_donate_land_vnd = self.icm_donate_land_vnd

        vals['icm_total_build_cost_usd'] = self.convert_usd(icm_total_build_cost_vnd, exchange_rate)
        vals['icm_give_effort_usd'] = self.convert_usd(icm_give_effort_vnd, exchange_rate)
        vals['icm_donate_materials_usd'] = self.convert_usd(icm_donate_materials_vnd, exchange_rate)
        vals['icm_donate_cash_usd'] = self.convert_usd(icm_donate_cash_vnd, exchange_rate)
        vals['icm_donate_land_usd'] = self.convert_usd(icm_donate_land_vnd, exchange_rate)

        return vals

    @api.model
    def create(self, vals):
        vals = self.convert_usd_b4save(vals)

        rec =  super(ICMForm, self).create(vals)

        return rec

    def write(self, vals):
        vals = self.convert_usd_b4save(vals)

        rec = super(ICMForm, self).write(vals)

        return rec
    