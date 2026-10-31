# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_solar_order = fields.Boolean(string='Is SolarFlow Order', default=False)
    solar_lead_id = fields.Many2one('crm.lead', string='Related Solar Lead', tracking=True)
    survey_id = fields.Many2one(
        'solarflow.survey',
        string='Approved Survey',
        tracking=True,
        domain="[('state', '=', 'approved')]",
        help="Only officially approved site surveys may be attached to a solar quotation."
    )
    solar_package_id = fields.Many2one(
        'solarflow.package',
        string='Solar Package',
        tracking=True,
        domain="[('active', '=', True)]"
    )

    installation_capacity_kw = fields.Float(string='Installation Capacity (kW)', default=3.0, tracking=True)
    solar_system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid System'),
        ('hybrid', 'Smart Hybrid (Solar + Battery + Grid)'),
        ('off_grid', 'Standalone Off-Grid System'),
    ], string='System Type', default='on_grid', required=True, tracking=True)

    roof_type = fields.Selection([
        ('rcc_flat', 'RCC Flat Concrete Roof'),
        ('metal_sheet', 'Industrial Metal Sheet'),
        ('clay_tile', 'Pitched Tile'),
        ('asbestos', 'Asbestos Sheet'),
        ('ground_mount', 'Ground Mount'),
    ], string='Roof Architecture')

    # Payment Policy & Accounting Integration
    advance_payment_pct = fields.Float(
        string='Advance Payment Policy (%)',
        default=50.0,
        help="Percentage of total order amount required as advance before dispatch permission is granted."
    )
    advance_payment_amount = fields.Monetary(
        string='Required Advance Amount',
        compute='_compute_solar_payments',
        store=True
    )
    amount_paid = fields.Monetary(
        string='Actual Amount Paid',
        compute='_compute_solar_payments',
        store=True,
        tracking=True,
        help="Total payments reconciled against posted invoices for this order."
    )
    amount_outstanding = fields.Monetary(
        string='Outstanding Balance',
        compute='_compute_solar_payments',
        store=True,
        help="Remaining unpaid balance on this contract."
    )

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid (0%)'),
        ('partially_paid', 'Partially Paid (Advance Met)'),
        ('fully_paid', 'Paid in Full (100%)'),
    ], string='Payment Completion Status', compute='_compute_solar_payments', store=True, tracking=True)

    dispatch_permission = fields.Boolean(
        string='Dispatch Permission Granted',
        compute='_compute_solar_payments',
        store=True,
        tracking=True,
        help="Granted automatically when customer payment satisfies the advance payment policy."
    )

    # Subsidy & ROI Analysis
    subsidy_amount = fields.Monetary(string='Govt Subsidy Offset', compute='_compute_subsidy', store=True, readonly=False)
    net_customer_cost = fields.Monetary(string='Net Customer Cost', compute='_compute_subsidy', store=True)
    simple_payback_years = fields.Float(string='Estimated Payback (Years)', compute='_compute_subsidy', store=True)

    installation_id = fields.Many2one('solarflow.installation', string='Linked Installation Project', readonly=True)

    @api.constrains('survey_id', 'state')
    def _check_approved_survey_requirement(self):
        """Enforces Business Rule: Quotations require approved surveys."""
        for order in self:
            if order.is_solar_order and order.survey_id:
                if order.survey_id.state != 'approved':
                    raise ValidationError(_("Quotation '%s' cannot proceed with unapproved survey '%s' (Current status: %s). The survey must be Approved by the Chief Engineer.")
                                          % (order.name, order.survey_id.name, order.survey_id.state))

    @api.onchange('survey_id')
    def _onchange_survey_id(self):
        if self.survey_id:
            if self.survey_id.state != 'approved':
                raise UserError(_("Selected survey is not approved yet! Only approved surveys can be linked."))
            self.installation_capacity_kw = self.survey_id.recommended_capacity_kw
            self.solar_system_type = self.survey_id.system_type
            self.roof_type = self.survey_id.roof_type
            if self.survey_id.package_id:
                self.solar_package_id = self.survey_id.package_id
                self.action_populate_package_components()

    @api.onchange('solar_package_id')
    def _onchange_solar_package_id(self):
        if self.solar_package_id:
            self.installation_capacity_kw = self.solar_package_id.system_capacity_kw
            self.solar_system_type = self.solar_package_id.system_type
            self.action_populate_package_components()

    def action_populate_package_components(self):
        """Populates quotation lines from the selected solar package components without hardcoding."""
        for order in self:
            if not order.solar_package_id:
                continue

            # Clear existing lines and populate from package components
            order.order_line = [(5, 0, 0)]
            new_lines = []

            for line in order.solar_package_id.package_line_ids:
                new_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': f"[{line.category.upper()}] {line.name}",
                    'product_uom_qty': line.quantity,
                    'price_unit': line.unit_price,
                }))

            order.order_line = new_lines

    @api.depends('amount_total', 'advance_payment_pct', 'invoice_ids.payment_state', 'invoice_ids.amount_residual', 'invoice_ids.state')
    def _compute_solar_payments(self):
        for order in self:
            # Advance required
            order.advance_payment_amount = (order.amount_total * (order.advance_payment_pct or 50.0)) / 100.0

            # Calculate actual paid amount from posted invoices
            paid_sum = 0.0
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            for inv in posted_invoices:
                paid_sum += (inv.amount_total - inv.amount_residual)

            order.amount_paid = paid_sum
            order.amount_outstanding = max(0.0, order.amount_total - paid_sum)

            # Determine payment status & dispatch permission
            if paid_sum >= order.amount_total and order.amount_total > 0:
                order.payment_status = 'fully_paid'
                order.dispatch_permission = True
            elif paid_sum >= order.advance_payment_amount and order.advance_payment_amount > 0:
                order.payment_status = 'partially_paid'
                order.dispatch_permission = True
            else:
                order.payment_status = 'unpaid'
                order.dispatch_permission = False

    @api.depends('installation_capacity_kw', 'amount_total')
    def _compute_subsidy(self):
        for order in self:
            cap = max(float(order.installation_capacity_kw or 0.0), 0.0)
            if cap <= 2.0:
                subsidy = cap * 30000.0
            elif cap <= 3.0:
                subsidy = 60000.0 + (cap - 2.0) * 18000.0
            else:
                subsidy = 78000.0
            order.subsidy_amount = subsidy
            order.net_customer_cost = max(0.0, order.amount_total - subsidy)
            annual_savings = cap * 1450.0 * 0.12  # ₹0.12/kWh equivalent in this model
            order.simple_payback_years = round(order.net_customer_cost / annual_savings, 2) if annual_savings > 0 else 0.0

    def action_confirm(self):
        """Enforces Business Rules:
        - Confirmed sales orders must have valid customer and product details.
        - Spawns Solar Installation record.
        """
        # Security Enforcement: Only Sales Manager or Super Administrator
        if not (self.env.user.has_group('solarflow_management.group_solarflow_sales_manager') or
                self.env.user.has_group('solarflow_management.group_solarflow_admin')):
            raise AccessError(_("Security Violation: Only Sales Managers or Super Administrators have permission to confirm sales orders."))
        if self.env.user.has_group('solarflow_management.group_solarflow_director') and not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
            raise AccessError(_("Security Violation: Director / Investor role has strict read-only access and cannot confirm orders."))

        for order in self:
            if order.is_solar_order:
                if not order.order_line:
                    raise UserError(_("Solar order '%s' must have component lines before confirmation.") % order.name)
                if not order.partner_id:
                    raise UserError(_("Please specify a customer before confirming the order."))
                if order.survey_id and order.survey_id.state != 'approved':
                    raise ValidationError(_("Cannot confirm order '%s': Attached survey '%s' is not approved.") % (order.name, order.survey_id.name))

        res = super(SaleOrder, self).action_confirm()

        # Create Solar Installation project upon order confirmation
        for order in self:
            if order.is_solar_order and not order.installation_id:
                inst_vals = {
                    'name': f"INST-{order.name}",
                    'sale_order_id': order.id,
                    'customer_id': order.partner_id.id,
                    'survey_id': order.survey_id.id if order.survey_id else False,
                    'package_id': order.solar_package_id.id if order.solar_package_id else False,
                    'installation_capacity_kw': order.installation_capacity_kw,
                    'system_type': order.solar_system_type,
                    'installation_address': order.partner_id.contact_address,
                    'state': 'draft',
                }
                inst = self.env['solarflow.installation'].create(inst_vals)
                order.installation_id = inst.id

        return res

    @api.model
    def action_create_from_survey(self, survey):
        """Creates a quotation from an approved site survey."""
        if not (self.env.user.has_group('solarflow_management.group_solarflow_sales_manager') or
                self.env.user.has_group('solarflow_management.group_solarflow_admin')):
            raise AccessError(_("Security Violation: Only Sales Managers or Super Administrators can generate sales quotations."))

        if survey.state != 'approved':
            raise UserError(_("Survey must be approved before quotation creation."))

        order_vals = {
            'partner_id': survey.partner_id.id,
            'opportunity_id': survey.lead_id.id if survey.lead_id else False,
            'solar_lead_id': survey.lead_id.id if survey.lead_id else False,
            'survey_id': survey.id,
            'is_solar_order': True,
            'solar_package_id': survey.package_id.id if survey.package_id else False,
            'installation_capacity_kw': survey.recommended_capacity_kw,
            'solar_system_type': survey.system_type,
            'roof_type': survey.roof_type,
        }
        order = self.create(order_vals)

        # Populate components from package or survey BOM
        if survey.package_id:
            order.action_populate_package_components()
        elif survey.bom_line_ids:
            order.order_line = [(0, 0, {
                'product_id': line.product_id.id if line.product_id else False,
                'name': line.name,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_cost,
            }) for line in survey.bom_line_ids]

        return {
            'name': _('SolarFlow Sales Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def unlink(self):
        for order in self:
            if order.is_solar_order and not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
                raise AccessError(_("Security Violation: Only Super Administrators have permission to delete SolarFlow Sales Orders."))
        return super(SaleOrder, self).unlink()
