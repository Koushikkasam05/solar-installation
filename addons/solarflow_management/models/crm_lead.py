# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    is_solar_lead = fields.Boolean(
        string='Is SolarFlow Lead',
        default=True,
        help="Flags whether this opportunity belongs to SolarFlow ERP."
    )

    solarflow_reference = fields.Char(
        string='Solar Reference',
        copy=False,
        readonly=True,
        index=True,
        help="Unique auto-generated reference number for this solar inquiry."
    )

    solar_capacity_kw = fields.Float(
        string='Required Capacity (kW)',
        default=3.0,
        tracking=True,
        help="Estimated or desired solar plant capacity in Kilowatts."
    )

    solar_system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid System'),
        ('hybrid', 'Smart Hybrid (Solar + Battery + Grid)'),
        ('off_grid', 'Standalone Off-Grid System'),
    ], string='System Type', default='on_grid', required=True, tracking=True)

    subsidy_required = fields.Boolean(
        string='Subsidy Requirement',
        default=True,
        tracking=True,
        help="Whether the customer intends to claim central/state government subsidy (e.g., PM Surya Ghar)."
    )

    expected_install_date = fields.Date(
        string='Expected Installation Date',
        tracking=True,
        help="Target date by which the customer expects commissioning."
    )

    solar_lead_source = fields.Selection([
        ('web_inbound', 'Website / Inbound Portal'),
        ('referral', 'Customer Referral'),
        ('telemarketing', 'In-House Telemarketing'),
        ('expo', 'Clean Energy Expo / Trade Show'),
        ('channel_partner', 'Channel Partner / EPC Affiliate'),
        ('direct_walkin', 'Direct Walk-in Enquiry'),
    ], string='Solar Lead Source', default='web_inbound', tracking=True)

    survey_status = fields.Selection([
        ('not_scheduled', 'Survey Not Scheduled'),
        ('scheduled', 'Survey Scheduled'),
        ('completed', 'Survey Completed'),
        ('approved', 'Survey Approved by Engineer'),
        ('rejected', 'Survey Rejected / Infeasible'),
    ], string='Survey Status', default='not_scheduled', tracking=True)

    # Technical energy profile & bill metrics
    monthly_consumption_kwh = fields.Float(
        string='Monthly Avg Consumption (kWh/Units)',
        default=450.0,
        help="Average monthly power consumption recorded from consumer bill."
    )
    current_electricity_tariff = fields.Float(
        string='Current Tariff (per kWh)',
        default=8.5,
        help="Grid electricity tariff rate per unit."
    )
    estimated_monthly_bill = fields.Monetary(
        string='Estimated Monthly Bill',
        compute='_compute_solar_estimates',
        store=True
    )
    estimated_roof_area_sqft = fields.Float(
        string='Estimated Available Roof (sq. ft.)',
        default=600.0
    )
    solar_feasibility_score = fields.Integer(
        string='Feasibility Score (%)',
        compute='_compute_solar_estimates',
        store=True
    )

    # Relationship to Site Survey
    survey_ids = fields.One2many(
        'solarflow.survey',
        'lead_id',
        string='Site Surveys'
    )
    survey_count = fields.Integer(
        string='Surveys Count',
        compute='_compute_survey_count'
    )

    _sql_constraints = [
        ('solarflow_reference_unique', 'unique(solarflow_reference)', 'SolarFlow reference numbers must be unique!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_solar_lead', True) and not vals.get('solarflow_reference'):
                vals['solarflow_reference'] = self.env['ir.sequence'].next_by_code('solarflow.lead.seq') or _('SF-DRAFT')
        return super(CrmLead, self).create(vals_list)

    @api.constrains('partner_name', 'contact_name', 'partner_id', 'phone', 'email_from')
    def _check_customer_information(self):
        for lead in self:
            if not lead.is_solar_lead:
                continue
            has_name = bool(lead.partner_name or lead.contact_name or (lead.partner_id and lead.partner_id.name))
            if not has_name:
                raise ValidationError(_("Customer Name or Company Name is mandatory for creating a SolarFlow Lead."))
            if not lead.phone and not lead.email_from:
                raise ValidationError(_("Please provide at least a Phone Number or an Email Address for the customer."))

    @api.constrains('solar_capacity_kw')
    def _check_solar_capacity(self):
        for lead in self:
            if lead.is_solar_lead and lead.solar_capacity_kw <= 0:
                raise ValidationError(_("Required solar capacity must be strictly greater than 0 kW."))

    @api.depends('monthly_consumption_kwh', 'current_electricity_tariff', 'estimated_roof_area_sqft', 'solar_capacity_kw')
    def _compute_solar_estimates(self):
        for lead in self:
            lead.estimated_monthly_bill = lead.monthly_consumption_kwh * lead.current_electricity_tariff

            # Calculate Feasibility Score
            score = 100
            # Space requirement rule of thumb: ~80 sq.ft. per kW
            req_space = lead.solar_capacity_kw * 80.0
            if lead.estimated_roof_area_sqft < req_space:
                deficit = req_space - lead.estimated_roof_area_sqft
                penalty = min(50, int((deficit / req_space) * 50))
                score -= penalty

            if lead.monthly_consumption_kwh < 150:
                score -= 15

            lead.solar_feasibility_score = max(0, min(100, score))

    def _compute_survey_count(self):
        for lead in self:
            lead.survey_count = len(lead.survey_ids)

    def action_schedule_site_survey(self):
        """Converts qualified lead into the Site Survey stage."""
        self.ensure_one()
        # Find or create partner
        partner = self.partner_id
        if not partner:
            partner = self._create_lead_partner()

        survey_vals = {
            'lead_id': self.id,
            'partner_id': partner.id,
            'recommended_capacity_kw': self.solar_capacity_kw,
            'system_type': self.solar_system_type,
            'roof_area_sqft': self.estimated_roof_area_sqft,
            'state': 'draft',
        }
        survey = self.env['solarflow.survey'].create(survey_vals)
        self.survey_status = 'scheduled'

        # Schedule follow-up activity
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Conduct On-Site Rooftop Solar Feasibility Survey"),
            note=_("Site survey scheduled for %s. Inspect roof structural load, shading, and main DB distance.") % partner.name,
            user_id=self.user_id.id or self.env.uid
        )

        return {
            'name': _('Site Feasibility Survey'),
            'type': 'ir.actions.act_window',
            'res_model': 'solarflow.survey',
            'res_id': survey.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _create_lead_partner(self):
        """Helper to create a res.partner for the customer."""
        partner_vals = {
            'name': self.contact_name or self.partner_name or self.name,
            'phone': self.phone,
            'email': self.email_from,
            'street': self.street,
            'city': self.city,
            'zip': self.zip,
            'customer_rank': 1,
        }
        partner = self.env['res.partner'].create(partner_vals)
        self.partner_id = partner.id
        return partner

    def action_view_surveys(self):
        self.ensure_one()
        return {
            'name': _('Site Surveys'),
            'type': 'ir.actions.act_window',
            'res_model': 'solarflow.survey',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
