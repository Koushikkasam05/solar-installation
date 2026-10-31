# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

class SolarFlowServiceTicket(models.Model):
    _name = 'solarflow.service.ticket'
    _description = 'SolarFlow After-Sales Service Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, complaint_date desc, id desc'

    name = fields.Char(
        string='Ticket Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        index=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Equipment Product',
        required=True,
        tracking=True
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Equipment Serial Number',
        tracking=True,
        index=True,
        domain="[('product_id', '=', product_id)]",
        help="Equipment serial number reporting the breakdown or defect."
    )
    warranty_id = fields.Many2one(
        'solarflow.warranty',
        string='Related Warranty',
        compute='_compute_warranty_id',
        store=True,
        readonly=False,
        tracking=True,
        help="Applicable warranty automatically discovered via the serial number."
    )
    installation_id = fields.Many2one(
        'solarflow.installation',
        string='Installation Site',
        compute='_compute_installation_id',
        store=True,
        readonly=False
    )

    complaint_date = fields.Date(
        string='Complaint Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    problem_description = fields.Text(
        string='Problem Description & Symptoms',
        required=True,
        tracking=True
    )
    fault_category = fields.Selection([
        ('inverter_fault', 'Inverter Internal Error / MPPT Failure (OEM Defect)'),
        ('battery_degradation', 'Battery Rapid Capacity Degradation (OEM Defect)'),
        ('module_burn', 'Solar PV Hotspot / Delamination (OEM Defect)'),
        ('wiring_earthing', 'Wiring Loose Connection / Earth Fault'),
        ('grid_surge', 'External DISCOM Grid Lightning Surge (Non-OEM)'),
        ('physical_damage', 'External Physical Damage / Accidental (Non-OEM)'),
        ('amc_routine', 'Periodic Routine Maintenance / Cleaning'),
    ], string='Fault Category', required=True, default='inverter_fault', tracking=True)

    priority = fields.Selection([
        ('0', 'Low Priority'),
        ('1', 'Normal (Standard SLA 48h)'),
        ('2', 'High (SLA 24h)'),
        ('3', 'Emergency (Critical Generation Outage)'),
    ], string='Priority Level', default='1', tracking=True)

    assigned_technician_id = fields.Many2one(
        'res.users',
        string='Assigned Technician',
        tracking=True
    )
    diagnosis = fields.Text(
        string='Technician Diagnosis & Root Cause',
        tracking=True
    )
    resolution = fields.Text(
        string='Resolution Summary & Corrective Action',
        tracking=True
    )

    # Replacement Parts & Financial Costs
    part_line_ids = fields.One2many(
        'solarflow.service.part.line',
        'ticket_id',
        string='Replacement Parts Consumed'
    )
    parts_cost = fields.Monetary(
        string='Replacement Parts Total',
        compute='_compute_charges',
        store=True
    )
    labour_cost = fields.Monetary(
        string='Labour Charges',
        default=0.0,
        tracking=True
    )
    repair_cost = fields.Monetary(
        string='Gross Repair Cost (Parts + Labour)',
        compute='_compute_charges',
        store=True,
        help="Total cost incurred to complete the repair."
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # Warranty Coverage & Invoicing
    warranty_covered = fields.Boolean(
        string='Covered Under Warranty',
        compute='_compute_warranty_coverage',
        store=True,
        tracking=True,
        help="If covered, repair and replacement parts are free ($0 customer charge)."
    )
    customer_charge = fields.Monetary(
        string='Customer Payable Amount',
        compute='_compute_charges',
        store=True,
        tracking=True,
        help="$0.00 for covered repairs; full repair cost for non-covered repairs."
    )

    # Customer Sign-Off Confirmation
    customer_confirmation = fields.Boolean(
        string='Customer Sign-Off Confirmation',
        default=False,
        tracking=True,
        help="Confirmation received from customer verifying system is restored."
    )
    customer_confirmation_date = fields.Date(string='Confirmation Date')

    # Workflow Status
    state = fields.Selection([
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('waiting_parts', 'Waiting for Parts'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], string='Ticket Status', default='new', tracking=True, required=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solarflow.service.ticket.seq') or _('TICK-NEW')
        return super(SolarFlowServiceTicket, self).create(vals_list)

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        """Rule 1 & 2: Automatically identify equipment and applicable warranty from Serial Number."""
        if self.lot_id:
            self.product_id = self.lot_id.product_id
            if self.lot_id.customer_id:
                self.customer_id = self.lot_id.customer_id
            if self.lot_id.installation_id:
                self.installation_id = self.lot_id.installation_id

            # Discover active warranty
            active_warranty = self.env['solarflow.warranty'].search([
                ('lot_id', '=', self.lot_id.id),
                ('status', '=', 'active'),
            ], limit=1)
            self.warranty_id = active_warranty.id if active_warranty else False

    @api.depends('lot_id')
    def _compute_warranty_id(self):
        for ticket in self:
            if ticket.lot_id and not ticket.warranty_id:
                active_w = self.env['solarflow.warranty'].search([
                    ('lot_id', '=', ticket.lot_id.id),
                    ('status', '=', 'active'),
                ], limit=1)
                ticket.warranty_id = active_w.id if active_w else False

    @api.depends('lot_id', 'warranty_id')
    def _compute_installation_id(self):
        for ticket in self:
            if ticket.lot_id and ticket.lot_id.installation_id:
                ticket.installation_id = ticket.lot_id.installation_id
            elif ticket.warranty_id and ticket.warranty_id.installation_id:
                ticket.installation_id = ticket.warranty_id.installation_id

    @api.depends('warranty_id', 'warranty_id.status', 'fault_category')
    def _compute_warranty_coverage(self):
        """Rule 3: Determine whether the reported issue is covered.
        - Non-covered faults: physical damage, external grid lightning surge, accidental damage.
        - Covered faults: internal inverter failure, battery cell drop, module hotspot, provided warranty is Active!
        """
        non_covered_categories = ['physical_damage', 'grid_surge']
        for ticket in self:
            if ticket.warranty_id and ticket.warranty_id.status == 'active':
                if ticket.fault_category not in non_covered_categories:
                    ticket.warranty_covered = True
                else:
                    ticket.warranty_covered = False
            else:
                ticket.warranty_covered = False

    @api.depends('part_line_ids.subtotal', 'labour_cost', 'warranty_covered')
    def _compute_charges(self):
        """Rule 6, 7, 8:
        Covered repairs must not charge customer for covered work ($0.00).
        Non-covered repairs calculate applicable parts and labour charges.
        """
        for ticket in self:
            parts_sum = sum(line.subtotal for line in ticket.part_line_ids)
            ticket.parts_cost = parts_sum
            gross = parts_sum + (ticket.labour_cost or 0.0)
            ticket.repair_cost = gross

            if ticket.warranty_covered:
                ticket.customer_charge = 0.0 # Free under warranty!
            else:
                ticket.customer_charge = gross

    # -------------------------------------------------------------------------
    # WORKFLOW TRANSITIONS & VALIDATION
    # -------------------------------------------------------------------------

    def action_assign(self):
        for ticket in self:
            if not ticket.assigned_technician_id:
                ticket.assigned_technician_id = self.env.user
            ticket.write({'state': 'assigned'})

    def action_start_repair(self):
        for ticket in self:
            ticket.write({'state': 'in_progress'})

    def action_wait_parts(self):
        for ticket in self:
            ticket.write({'state': 'waiting_parts'})

    def action_resolve(self):
        for ticket in self:
            if not ticket.diagnosis or not ticket.resolution:
                raise ValidationError(_("Please document both the Technician Diagnosis and Resolution before marking Resolved."))
            ticket.write({'state': 'resolved'})

    def action_close(self):
        """Rule 9: Record customer confirmation before closure."""
        if self.env.user.has_group('solarflow_management.group_solarflow_director') and not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
            raise AccessError(_("Security Violation: Director / Investor role has strict read-only access."))

        for ticket in self:
            if not ticket.customer_confirmation:
                raise ValidationError(_("Customer Confirmation Sign-Off is required before closing Service Ticket '%s'.") % ticket.name)
            ticket.write({
                'state': 'closed',
                'customer_confirmation_date': fields.Date.today()
            })

    def unlink(self):
        if not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
            raise AccessError(_("Security Violation: Only Super Administrators have permission to delete Service Tickets."))
        return super(SolarFlowServiceTicket, self).unlink()


class SolarFlowServicePartLine(models.Model):
    _name = 'solarflow.service.part.line'
    _description = 'Replacement Parts for Service Ticket'

    ticket_id = fields.Many2one('solarflow.service.ticket', string='Service Ticket', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Replacement Part', required=True)
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_price = fields.Monetary(string='Unit Price', required=True)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.unit_price = self.product_id.list_price

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
