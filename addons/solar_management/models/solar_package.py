# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SolarPackage(models.Model):
    _name = 'solar.package'
    _description = 'Pre-Engineered Solar Package'
    _order = 'system_capacity_kw asc'

    name = fields.Char(string='Package Name', required=True)
    code = fields.Char(string='Package Code', required=True)
    system_capacity_kw = fields.Float(string='System Capacity (kW)', required=True, default=3.0)
    system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid System'),
        ('hybrid', 'Hybrid (Solar + Grid + Battery Storage)'),
        ('off_grid', 'Standalone Off-Grid System'),
    ], string='System Type', default='on_grid', required=True)
    phase = fields.Selection([
        ('single_phase', 'Single Phase (230V)'),
        ('three_phase', 'Three Phase (415V)'),
    ], string='AC Grid Phase', default='single_phase', required=True)

    # Technical Defaults
    default_panel_wattage = fields.Integer(string='Default Panel Rating (Watts)', default=550)
    panel_technology = fields.Selection([
        ('mono_perc', 'Mono PERC Half-Cut Cells'),
        ('topcon_bifacial', 'TOPCon N-Type Bifacial Cells'),
        ('polycrystalline', 'Polycrystalline Cells'),
    ], string='Panel Technology', default='topcon_bifacial')
    battery_capacity_kwh = fields.Float(string='Battery Bank Size (kWh)', default=0.0)

    # Estimated Generation & Financials
    est_monthly_units_kwh = fields.Float(string='Est. Monthly Generation (kWh)', compute='_compute_estimates', store=True)
    est_annual_units_kwh = fields.Float(string='Est. Annual Generation (kWh)', compute='_compute_estimates', store=True)
    min_roof_area_sqft = fields.Float(string='Min Roof Area Required (sq. ft.)', compute='_compute_estimates', store=True)

    base_price = fields.Monetary(string='Base Turnkey Price', required=True, default=2100.0)
    subsidy_eligible = fields.Boolean(string='Eligible for Central/State Subsidy', default=True)
    max_subsidy_amount = fields.Monetary(string='Estimated Subsidy Cap', compute='_compute_subsidy_cap', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    description = fields.Html(string='Marketing / Technical Description')
    active = fields.Boolean(default=True)

    @api.depends('system_capacity_kw')
    def _compute_estimates(self):
        for pkg in self:
            # 1 kW generates approx 125 units (kWh) per month on Indian / Global averages
            pkg.est_monthly_units_kwh = round(pkg.system_capacity_kw * 125.0, 1)
            pkg.est_annual_units_kwh = round(pkg.est_monthly_units_kwh * 12.0, 1)
            pkg.min_roof_area_sqft = round(pkg.system_capacity_kw * 85.0, 1)

    @api.depends('system_capacity_kw', 'subsidy_eligible')
    def _compute_subsidy_cap(self):
        for pkg in self:
            if not pkg.subsidy_eligible:
                pkg.max_subsidy_amount = 0.0
                continue
            # PM Surya Ghar scheme structure:
            # Up to 2 kW: ~30,000 / kW (or equivalent ~$360/kW)
            # 3 kW and above: capped at ~78,000 (or equivalent ~$940 max)
            cap = pkg.system_capacity_kw
            if cap <= 2.0:
                pkg.max_subsidy_amount = round(cap * 360.0, 2)
            elif cap <= 3.0:
                pkg.max_subsidy_amount = 940.0
            else:
                pkg.max_subsidy_amount = 940.0 # Rooftop residential cap
