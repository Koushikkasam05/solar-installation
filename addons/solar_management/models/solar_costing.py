# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SolarProjectCosting(models.Model):
    _name = 'solar.project.costing'
    _description = 'Solar EPC Job Costing & Real-Time Profitability'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(string='Costing Reference', required=True)
    project_id = fields.Many2one('solar.installation.project', string='Installation Project', required=True, ondelete='cascade')
    customer_id = fields.Many2one(related='project_id.customer_id', string='Customer', store=True)
    system_capacity_kw = fields.Float(related='project_id.system_capacity_kw', string='System Size (kW)', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Revenue
    contract_revenue = fields.Monetary(string='Total Contract Revenue (Turnkey)', required=True, tracking=True)

    # Cost Breakdown
    bom_hardware_cost = fields.Monetary(string='PV Modules, Inverter & Storage', default=0.0, tracking=True)
    structure_civil_cost = fields.Monetary(string='Mounting Structures & Grouting', default=0.0, tracking=True)
    electrical_bos_cost = fields.Monetary(string='Electrical BOS (Cables, DBs, Earthing)', default=0.0, tracking=True)
    labor_technician_cost = fields.Monetary(string='Technician & Civil Labor Fees', default=0.0, tracking=True)
    discom_liaisoning_cost = fields.Monetary(string='DISCOM Approvals & Meter Fees', default=0.0, tracking=True)
    transportation_cost = fields.Monetary(string='Freight, Transport & Logistics', default=0.0, tracking=True)
    contingency_cost = fields.Monetary(string='Site Contingency / Miscellaneous', default=0.0)

    # Computed Profitability Metrics
    total_project_cost = fields.Monetary(string='Total Execution Cost', compute='_compute_profitability', store=True)
    gross_profit = fields.Monetary(string='Gross Profit (EBITDA)', compute='_compute_profitability', store=True)
    profit_margin_pct = fields.Float(string='Net Profit Margin (%)', compute='_compute_profitability', store=True)
    cost_per_watt = fields.Float(string='Cost per Watt ($/W)', compute='_compute_profitability', store=True)
    revenue_per_watt = fields.Float(string='Revenue per Watt ($/W)', compute='_compute_profitability', store=True)

    margin_status = fields.Selection([
        ('high', 'High Margin (> 25%)'),
        ('healthy', 'Healthy Margin (15% - 25%)'),
        ('low', 'Thin Margin (5% - 15%)'),
        ('loss', 'Deficit / Unprofitable (< 0%)'),
    ], string='Profitability Health', compute='_compute_profitability', store=True)

    @api.depends(
        'contract_revenue', 'bom_hardware_cost', 'structure_civil_cost',
        'electrical_bos_cost', 'labor_technician_cost', 'discom_liaisoning_cost',
        'transportation_cost', 'contingency_cost', 'system_capacity_kw'
    )
    def _compute_profitability(self):
        for rec in self:
            total_cost = (
                rec.bom_hardware_cost +
                rec.structure_civil_cost +
                rec.electrical_bos_cost +
                rec.labor_technician_cost +
                rec.discom_liaisoning_cost +
                rec.transportation_cost +
                rec.contingency_cost
            )
            rec.total_project_cost = total_cost
            rec.gross_profit = rec.contract_revenue - total_cost

            if rec.contract_revenue > 0:
                margin = (rec.gross_profit / rec.contract_revenue) * 100.0
                rec.profit_margin_pct = round(margin, 2)
            else:
                rec.profit_margin_pct = 0.0

            total_watts = rec.system_capacity_kw * 1000.0 if rec.system_capacity_kw else 1.0
            rec.cost_per_watt = round(total_cost / total_watts, 3)
            rec.revenue_per_watt = round(rec.contract_revenue / total_watts, 3)

            if rec.profit_margin_pct >= 25.0:
                rec.margin_status = 'high'
            elif rec.profit_margin_pct >= 15.0:
                rec.margin_status = 'healthy'
            elif rec.profit_margin_pct > 0.0:
                rec.margin_status = 'low'
            else:
                rec.margin_status = 'loss'
