# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_solar_order = fields.Boolean(string='Is Solar Installation Contract', default=False)
    survey_id = fields.Many2one('solar.site.survey', string='Site Survey Reference')
    package_id = fields.Many2one('solar.package', string='Solar Package')
    system_capacity_kw = fields.Float(string='Installed Capacity (kW)', default=3.0)
    system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid'),
        ('hybrid', 'Hybrid with Battery'),
        ('off_grid', 'Off-Grid Standalone'),
    ], string='System Type', default='on_grid')
    roof_type = fields.Selection([
        ('rcc_flat', 'RCC Flat Roof'),
        ('metal_sheet', 'Metal Sheet'),
        ('clay_tile', 'Pitched Tile'),
        ('asbestos', 'Asbestos Sheet'),
        ('ground_mount', 'Ground Mount'),
    ], string='Roof Architecture')

    # Subsidy & Financial Analysis
    subsidy_eligible = fields.Boolean(string='Apply Central / State Subsidy', default=True)
    subsidy_amount = fields.Monetary(string='Govt Subsidy (e.g. PM Surya Ghar)', compute='_compute_subsidy_amount', store=True, readonly=False)
    net_customer_cost = fields.Monetary(string='Net Customer Cost (Post Subsidy)', compute='_compute_solar_financials', store=True)

    # Solar ROI & Payback Calculator
    grid_tariff_rate = fields.Float(string='Grid Tariff Rate (per Unit/kWh)', default=8.5)
    annual_generation_kwh = fields.Float(string='Est. Annual Generation (kWh)', compute='_compute_solar_financials', store=True)
    annual_bill_savings = fields.Monetary(string='Annual Bill Savings', compute='_compute_solar_financials', store=True)
    simple_payback_years = fields.Float(string='Estimated Payback Period (Years)', compute='_compute_solar_financials', store=True)
    lifetime_25yr_savings = fields.Monetary(string='Lifetime 25-Year Savings', compute='_compute_solar_financials', store=True)
    co2_offset_ton_per_yr = fields.Float(string='Greenhouse Gas Offset (Tons CO2/Yr)', compute='_compute_solar_financials', store=True)

    # Milestone Payment Tracking
    milestone_ids = fields.One2many('solar.payment.milestone', 'order_id', string='Payment Milestones')
    installation_project_id = fields.Many2one('solar.installation.project', string='Installation Project', readonly=True)
    installation_count = fields.Integer(string='Installation Projects', compute='_compute_installation_count')

    @api.depends('package_id', 'system_capacity_kw', 'subsidy_eligible')
    def _compute_subsidy_amount(self):
        for order in self:
            if not order.subsidy_eligible:
                order.subsidy_amount = 0.0
                continue
            cap = max(float(order.system_capacity_kw or 0.0), 0.0)
            if cap <= 2.0:
                order.subsidy_amount = cap * 30000.0
            elif cap <= 3.0:
                order.subsidy_amount = 60000.0 + (cap - 2.0) * 18000.0
            else:
                order.subsidy_amount = 78000.0

    @api.depends('amount_total', 'subsidy_amount', 'system_capacity_kw', 'grid_tariff_rate')
    def _compute_solar_financials(self):
        for order in self:
            order.net_customer_cost = max(0.0, order.amount_total - order.subsidy_amount)
            # 1 kW produces approx 1450 units per year
            annual_gen = order.system_capacity_kw * 1450.0
            order.annual_generation_kwh = annual_gen
            annual_savings = annual_gen * order.grid_tariff_rate
            order.annual_bill_savings = annual_savings

            if annual_savings > 0:
                order.simple_payback_years = round(order.net_customer_cost / annual_savings, 2)
            else:
                order.simple_payback_years = 0.0

            order.lifetime_25yr_savings = annual_savings * 25.0
            # 0.82 kg CO2 per kWh = 0.00082 Tons per kWh
            order.co2_offset_ton_per_yr = round(annual_gen * 0.00082, 2)

    def _compute_installation_count(self):
        for order in self:
            order.installation_count = 1 if order.installation_project_id else 0

    def action_generate_milestones(self):
        self.ensure_one()
        self.milestone_ids.unlink()

        total = self.amount_total
        stages = [
            ("Booking Advance & Contract Signing", 10.0, 'advance'),
            ("Site Engineering Design & DISCOM Approval", 20.0, 'design'),
            ("Solar Modules, Inverter & BOS Dispatch", 50.0, 'dispatch'),
            ("Mechanical & Electrical Installation Done", 15.0, 'installation'),
            ("Bi-Directional Net Meter Sync & Handover", 5.0, 'commissioning'),
        ]

        for name, pct, code in stages:
            amt = (total * pct) / 100.0
            self.env['solar.payment.milestone'].create({
                'order_id': self.id,
                'name': name,
                'milestone_stage': code,
                'percentage': pct,
                'amount': amt,
                'currency_id': self.currency_id.id,
                'state': 'pending',
            })

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.is_solar_order and not order.installation_project_id:
                # Spawn Solar Installation Project
                project_vals = {
                    'name': f"INST-{order.name}-{order.partner_id.name}",
                    'sale_order_id': order.id,
                    'customer_id': order.partner_id.id,
                    'system_capacity_kw': order.system_capacity_kw,
                    'system_type': order.system_type,
                    'roof_type': order.roof_type,
                    'survey_id': order.survey_id.id if order.survey_id else False,
                    'state': 'draft',
                }
                proj = self.env['solar.installation.project'].create(project_vals)
                order.installation_project_id = proj.id
                # Also auto-generate payment milestones if not present
                if not order.milestone_ids:
                    order.action_generate_milestones()
        return res

    def action_view_installation(self):
        self.ensure_one()
        return {
            'name': _('Installation Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'solar.installation.project',
            'res_id': self.installation_project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class SolarPaymentMilestone(models.Model):
    _name = 'solar.payment.milestone'
    _description = 'Solar EPC Milestone Payment'
    _order = 'id asc'

    order_id = fields.Many2one('sale.order', string='Sales Order', ondelete='cascade', required=True)
    name = fields.Char(string='Milestone Description', required=True)
    milestone_stage = fields.Selection([
        ('advance', 'Booking Advance (10%)'),
        ('design', 'Design & DISCOM Approval (20%)'),
        ('dispatch', 'Material Dispatch (50%)'),
        ('installation', 'Installation Done (15%)'),
        ('commissioning', 'Net Meter & Commissioning (5%)'),
    ], string='Milestone Stage', required=True)

    percentage = fields.Float(string='Split (%)', required=True)
    amount = fields.Monetary(string='Milestone Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid in Full'),
    ], string='Status', default='pending')
    invoice_id = fields.Many2one('account.move', string='Milestone Invoice', readonly=True)

    def action_mark_paid(self):
        self.write({'state': 'paid'})
