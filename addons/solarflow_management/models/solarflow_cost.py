# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

class SolarFlowProjectCost(models.Model):
    _name = 'solarflow.project.cost'
    _description = 'SolarFlow Project Cost & Profitability Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Cost Sheet Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        index=True
    )
    installation_id = fields.Many2one(
        'solarflow.installation',
        string='Solar Installation Project',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order Contract',
        related='installation_id.sale_order_id',
        store=True,
        tracking=True,
        index=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='installation_id.customer_id',
        store=True,
        index=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # -------------------------------------------------------------------------
    # COST COMPONENTS (TRACKED FIELDS AS REQUIRED)
    # -------------------------------------------------------------------------
    # Actual Incurred Costs
    material_cost = fields.Monetary(
        string='Material Cost',
        default=0.0,
        tracking=True,
        help="Direct hardware cost: PV modules, inverter, structure, cables."
    )
    technician_labour_cost = fields.Monetary(
        string='Technician Labour Cost',
        default=0.0,
        tracking=True,
        help="On-site electrician and technician labor charges."
    )
    # Alias for compatibility
    labour_cost = fields.Monetary(
        string='Labour Cost',
        related='technician_labour_cost',
        readonly=False,
        store=True
    )
    transportation_cost = fields.Monetary(
        string='Transportation Cost',
        default=0.0,
        tracking=True,
        help="Freight, logistics and site delivery charges."
    )
    additional_material_cost = fields.Monetary(
        string='Additional Material Cost',
        default=0.0,
        tracking=True,
        help="Unplanned BOS items, conduit extensions, fasteners."
    )
    other_expenses = fields.Monetary(
        string='Other Expenses',
        default=0.0,
        tracking=True,
        help="DISCOM statutory permits, net-meter fees, insurance."
    )

    # Estimated Costs (Budgeted Baseline)
    estimated_material_cost = fields.Monetary(string='Estimated Material Cost', default=0.0, tracking=True)
    estimated_labour_cost = fields.Monetary(string='Estimated Labour Cost', default=0.0, tracking=True)
    estimated_transportation_cost = fields.Monetary(string='Estimated Transportation Cost', default=0.0, tracking=True)
    estimated_additional_cost = fields.Monetary(string='Estimated Additional Cost', default=0.0)
    estimated_other_expenses = fields.Monetary(string='Estimated Other Expenses', default=0.0)

    # -------------------------------------------------------------------------
    # REVENUE (ESTIMATED & ACTUAL)
    # -------------------------------------------------------------------------
    estimated_revenue = fields.Monetary(
        string='Estimated Revenue',
        default=0.0,
        tracking=True,
        help="Quoted contract price approved by customer."
    )
    actual_revenue = fields.Monetary(
        string='Actual Revenue',
        default=0.0,
        tracking=True,
        help="Total recognized revenue / invoiced amount received."
    )
    # Backward compatibility alias
    contract_revenue = fields.Monetary(
        string='Contract Revenue',
        related='actual_revenue',
        readonly=False,
        store=True
    )

    # -------------------------------------------------------------------------
    # TOTAL CALCULATIONS
    # Formula: Total Cost = Material Cost + Labour Cost + Transportation Cost + Additional Material Cost + Other Expenses
    # -------------------------------------------------------------------------
    estimated_cost = fields.Monetary(
        string='Estimated Cost',
        compute='_compute_totals',
        store=True,
        tracking=True,
        help="Total estimated project cost baseline."
    )
    actual_cost = fields.Monetary(
        string='Actual Cost',
        compute='_compute_totals',
        store=True,
        tracking=True,
        help="Total actual incurred cost."
    )
    # Alias total_cost = actual_cost
    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_totals',
        store=True,
        help="Total Cost = Material + Labour + Transportation + Additional Material + Other Expenses."
    )

    # -------------------------------------------------------------------------
    # GROSS PROFIT & GROSS MARGIN
    # Formula: Gross Profit = Revenue - Total Cost
    # Formula: Gross Margin = (Gross Profit / Revenue) * 100
    # Note: Not called final accounting profit; calculations are transparent.
    # -------------------------------------------------------------------------
    gross_profit = fields.Monetary(
        string='Gross Profit',
        compute='_compute_profitability',
        store=True,
        tracking=True,
        help="Project Gross Profit = Actual Revenue − Actual Total Cost (Not final net accounting profit)."
    )
    gross_margin = fields.Float(
        string='Gross Margin (%)',
        compute='_compute_profitability',
        store=True,
        digits=(16, 2),
        tracking=True,
        help="Gross Margin (%) = (Gross Profit / Actual Revenue) × 100. Returns 0.0% when revenue is zero."
    )

    estimated_gross_profit = fields.Monetary(
        string='Estimated Gross Profit',
        compute='_compute_profitability',
        store=True,
        help="Estimated Gross Profit = Estimated Revenue − Estimated Cost."
    )
    estimated_gross_margin = fields.Float(
        string='Estimated Gross Margin (%)',
        compute='_compute_profitability',
        store=True,
        digits=(16, 2),
        help="Estimated Gross Margin (%) = (Estimated Gross Profit / Estimated Revenue) × 100."
    )

    # -------------------------------------------------------------------------
    # BUDGET VARIANCE & PROFIT LEAKAGE ALERTS
    # -------------------------------------------------------------------------
    cost_variance = fields.Monetary(
        string='Cost Variance (Actual - Estimated)',
        compute='_compute_variance',
        store=True,
        help="Cost Variance = Actual Cost − Estimated Cost."
    )
    cost_variance_pct = fields.Float(
        string='Cost Overrun (%)',
        compute='_compute_variance',
        store=True,
        digits=(16, 2),
        help="Percentage by which actual cost exceeds or is below estimated cost."
    )
    is_budget_exceeded = fields.Boolean(
        string='Budget Exceeded',
        compute='_compute_variance',
        store=True,
        index=True,
        help="True if Actual Cost > Estimated Cost."
    )

    leakage_threshold_pct = fields.Float(
        string='Leakage Alert Threshold (%)',
        default=10.0,
        tracking=True,
        help="Configurable threshold percentage. If cost overrun exceeds this %, alert Solar Manager / Director."
    )
    is_profit_leakage = fields.Boolean(
        string='Profit Leakage Alert Triggered',
        compute='_compute_variance',
        store=True,
        index=True,
        help="Triggered when Cost Overrun (%) > Leakage Alert Threshold (%)."
    )
    alert_notified = fields.Boolean(
        string='Leakage Notification Sent',
        default=False,
        copy=False
    )

    notes = fields.Text(string='Profitability Notes & Explanations')

    _sql_constraints = [
        ('solarflow_cost_name_unique', 'unique(name)', 'Costing Reference must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.user.has_group('solarflow_management.group_solarflow_finance_manager') or
                self.env.user.has_group('solarflow_management.group_solarflow_admin')):
            raise AccessError(_("Security Violation: Only Finance Managers and Super Administrators have permission to create Project Costing sheets."))
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solarflow.project.cost.seq') or _('COST-NEW')
        records = super(SolarFlowProjectCost, self).create(vals_list)
        for rec in records:
            if rec.is_profit_leakage and not rec.alert_notified:
                rec.action_notify_profit_leakage()
        return records

    def write(self, vals):
        if not (self.env.user.has_group('solarflow_management.group_solarflow_finance_manager') or
                self.env.user.has_group('solarflow_management.group_solarflow_admin')):
            raise AccessError(_("Security Violation: Only Finance Managers and Super Administrators have permission to modify Project Costing sheets."))
        res = super(SolarFlowProjectCost, self).write(vals)
        for rec in self:
            if rec.is_profit_leakage and not rec.alert_notified:
                rec.action_notify_profit_leakage()
        return res

    def unlink(self):
        if not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
            raise AccessError(_("Security Violation: Only Super Administrators have permission to delete Project Costing records."))
        return super(SolarFlowProjectCost, self).unlink()

    # -------------------------------------------------------------------------
    # COMPUTATIONS
    # -------------------------------------------------------------------------
    @api.depends(
        'material_cost', 'technician_labour_cost', 'transportation_cost',
        'additional_material_cost', 'other_expenses',
        'estimated_material_cost', 'estimated_labour_cost',
        'estimated_transportation_cost', 'estimated_additional_cost',
        'estimated_other_expenses'
    )
    def _compute_totals(self):
        """Total Cost = Material Cost + Labour Cost + Transportation Cost + Other Expenses + Additional Material Cost."""
        for rec in self:
            rec.actual_cost = (
                rec.material_cost +
                rec.technician_labour_cost +
                rec.transportation_cost +
                rec.additional_material_cost +
                rec.other_expenses
            )
            rec.total_cost = rec.actual_cost

            rec.estimated_cost = (
                rec.estimated_material_cost +
                rec.estimated_labour_cost +
                rec.estimated_transportation_cost +
                rec.estimated_additional_cost +
                rec.estimated_other_expenses
            )

    @api.depends('actual_revenue', 'estimated_revenue', 'actual_cost', 'estimated_cost')
    def _compute_profitability(self):
        """Gross Profit = Revenue − Total Cost.
        Gross Margin = (Gross Profit / Revenue) × 100.
        Safe for zero-revenue cases!
        """
        for rec in self:
            # Actual Gross Profit & Margin
            rec.gross_profit = rec.actual_revenue - rec.actual_cost
            if rec.actual_revenue > 0:
                rec.gross_margin = round((rec.gross_profit / rec.actual_revenue) * 100.0, 2)
            else:
                rec.gross_margin = 0.0

            # Estimated Gross Profit & Margin
            rec.estimated_gross_profit = rec.estimated_revenue - rec.estimated_cost
            if rec.estimated_revenue > 0:
                rec.estimated_gross_margin = round((rec.estimated_gross_profit / rec.estimated_revenue) * 100.0, 2)
            else:
                rec.estimated_gross_margin = 0.0

    @api.depends('actual_cost', 'estimated_cost', 'leakage_threshold_pct')
    def _compute_variance(self):
        """Compares estimated against actual costs and detects budget excess and profit leakage."""
        for rec in self:
            variance = rec.actual_cost - rec.estimated_cost
            rec.cost_variance = variance
            rec.is_budget_exceeded = rec.actual_cost > rec.estimated_cost

            if rec.estimated_cost > 0:
                rec.cost_variance_pct = round((variance / rec.estimated_cost) * 100.0, 2)
            else:
                rec.cost_variance_pct = 0.0

            # Check profit leakage against configured threshold
            threshold = rec.leakage_threshold_pct or 10.0
            rec.is_profit_leakage = (rec.cost_variance_pct > threshold)

    # -------------------------------------------------------------------------
    # NOTIFICATION AUTOMATION
    # -------------------------------------------------------------------------
    def action_notify_profit_leakage(self):
        """Notifies the Solar Manager or Director if actual project cost exceeds estimated cost by configured %."""
        self.ensure_one()
        director_group = self.env.ref('solarflow_management.group_solarflow_director', raise_if_not_found=False)
        manager_group = self.env.ref('solarflow_management.group_solarflow_manager', raise_if_not_found=False)

        recipients = self.env['res.users']
        if director_group and director_group.users:
            recipients |= director_group.users
        if manager_group and manager_group.users:
            recipients |= manager_group.users

        if not recipients:
            recipients = self.env.user

        for user in recipients:
            self.activity_schedule(
                'mail.mail_activity_data_warning',
                summary=_("Profit Leakage Alert: %s (Overrun: %s%%)") % (self.name, self.cost_variance_pct),
                note=_(
                    "Project Cost Alert!\n"
                    "Project '%s' for customer '%s' has exceeded its budget.\n\n"
                    "- Estimated Cost: $%s\n"
                    "- Actual Cost: $%s\n"
                    "- Cost Variance: +$%s (+%s%%)\n"
                    "- Configured Leakage Threshold: %s%%\n\n"
                    "Immediate management review of project procurement is recommended."
                ) % (
                    self.installation_id.name if self.installation_id else self.name,
                    self.customer_id.name if self.customer_id else 'N/A',
                    self.estimated_cost,
                    self.actual_cost,
                    self.cost_variance,
                    self.cost_variance_pct,
                    self.leakage_threshold_pct,
                ),
                user_id=user.id
            )
        self.alert_notified = True
        return True

