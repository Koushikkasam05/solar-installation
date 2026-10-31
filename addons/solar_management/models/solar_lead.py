# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    is_solar_lead = fields.Boolean(string='Is Solar Opportunity', default=True)
    customer_segment = fields.Selection([
        ('residential', 'Residential Rooftop'),
        ('commercial', 'Commercial Rooftop'),
        ('industrial', 'Industrial / Factory'),
        ('agricultural', 'Agricultural / Solar Pump'),
    ], string='Solar Customer Segment', default='residential')

    # Electricity Bill & DISCOM Profile
    discom_provider = fields.Char(string='DISCOM / Utility Provider')
    consumer_number = fields.Char(string='Electricity Consumer ID')
    sanctioned_load_kw = fields.Float(string='Sanctioned / Connected Load (kW)', default=5.0)
    monthly_avg_kwh = fields.Float(string='Monthly Avg Consumption (kWh/Units)', default=450.0)
    current_tariff_rate = fields.Float(string='Current Tariff Rate (per kWh)', default=8.5)
    monthly_bill_amount = fields.Monetary(string='Avg Monthly Bill Amount', compute='_compute_monthly_bill', store=True)

    # Roof & Feasibility Assessment
    roof_area_sqft = fields.Float(string='Approx Roof Area (sq. ft.)', default=600.0)
    recommended_capacity_kw = fields.Float(
        string='Recommended Solar Capacity (kW)',
        compute='_compute_solar_recommendations',
        store=True,
        help="Calculated based on monthly units, roof area (100 sq.ft/kW), and sanctioned load."
    )
    solar_feasibility_score = fields.Integer(
        string='Feasibility Score (%)',
        compute='_compute_solar_recommendations',
        store=True
    )
    feasibility_status = fields.Selection([
        ('high', 'High Feasibility (>75%)'),
        ('medium', 'Moderate Feasibility (50-75%)'),
        ('low', 'Low Feasibility (<50%)'),
    ], string='Feasibility Tier', compute='_compute_solar_recommendations', store=True)

    # Link to Surveys & Installation
    survey_ids = fields.One2many('solar.site.survey', 'lead_id', string='Site Surveys')
    survey_count = fields.Integer(string='Survey Count', compute='_compute_survey_count')

    @api.depends('monthly_avg_kwh', 'current_tariff_rate')
    def _compute_monthly_bill(self):
        for lead in self:
            lead.monthly_bill_amount = lead.monthly_avg_kwh * lead.current_tariff_rate

    @api.depends('monthly_avg_kwh', 'roof_area_sqft', 'sanctioned_load_kw')
    def _compute_solar_recommendations(self):
        for lead in self:
            # Rule of thumb: 1 kW produces approx 120 kWh per month
            capacity_by_kwh = lead.monthly_avg_kwh / 120.0 if lead.monthly_avg_kwh else 0.0
            # Rule of thumb: 1 kW requires approx 80-100 sq ft
            capacity_by_roof = lead.roof_area_sqft / 90.0 if lead.roof_area_sqft else 0.0
            # Sanctioned load limit
            max_allowed = lead.sanctioned_load_kw if lead.sanctioned_load_kw else capacity_by_kwh

            rec_cap = min(capacity_by_kwh, capacity_by_roof)
            if max_allowed > 0 and rec_cap > max_allowed:
                rec_cap = max_allowed

            lead.recommended_capacity_kw = round(rec_cap, 2)

            # Feasibility scoring calculation
            score = 100
            if lead.roof_area_sqft < 250:
                score -= 30
            elif lead.roof_area_sqft < 450:
                score -= 15

            if lead.monthly_avg_kwh < 200:
                score -= 20

            if lead.sanctioned_load_kw < 3.0:
                score -= 10

            lead.solar_feasibility_score = max(0, min(100, score))

            if lead.solar_feasibility_score >= 75:
                lead.feasibility_status = 'high'
            elif lead.solar_feasibility_score >= 50:
                lead.feasibility_status = 'medium'
            else:
                lead.feasibility_status = 'low'

    def _compute_survey_count(self):
        for lead in self:
            lead.survey_count = len(lead.survey_ids)

    def action_schedule_site_survey(self):
        self.ensure_one()
        return {
            'name': _('Schedule Site Survey'),
            'type': 'ir.actions.act_window',
            'res_model': 'solar.site.survey',
            'view_mode': 'form',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_recommended_kw': self.recommended_capacity_kw,
                'default_roof_area_sqft': self.roof_area_sqft,
            },
            'target': 'current',
        }

    def action_view_surveys(self):
        self.ensure_one()
        return {
            'name': _('Site Surveys'),
            'type': 'ir.actions.act_window',
            'res_model': 'solar.site.survey',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
