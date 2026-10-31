# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError

class StockLot(models.Model):
    _inherit = 'stock.lot'

    installation_id = fields.Many2one(
        'solarflow.installation',
        string='Allocated Installation Project',
        tracking=True,
        index=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer Owner',
        tracking=True,
        index=True
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order Contract',
        tracking=True
    )

    allocation_status = fields.Selection([
        ('available', 'In Warehouse (Available)'),
        ('allocated', 'Reserved for Installation'),
        ('dispatched', 'Dispatched to Site'),
        ('installed', 'Mounted & Energized'),
        ('warranty_active', 'Active under Warranty'),
        ('rma_service', 'Returned for Service / RMA'),
    ], string='Equipment Allocation Status', default='available', tracking=True, required=True)

    oem_manufacturer = fields.Char(string='OEM Brand')
    warranty_duration_years = fields.Integer(string='OEM Warranty Duration (Years)', default=10)
    purchase_date = fields.Date(string='Purchase Date', default=fields.Date.today)
    receipt_date = fields.Date(string='Warehouse Receipt Date', default=fields.Date.today)
    reservation_date = fields.Date(string='Sales Reservation Date')
    dispatch_date = fields.Date(string='Dispatched Date')
    commissioning_date = fields.Date(string='Commissioning Date')

    # Lifecycle Links
    warranty_ids = fields.One2many('solarflow.warranty', 'lot_id', string='Digital Warranties')
    warranty_count = fields.Integer(string='Warranties', compute='_compute_warranty_count')
    service_ticket_ids = fields.One2many('solarflow.service.ticket', 'lot_id', string='Service Tickets')
    service_ticket_count = fields.Integer(string='Service History', compute='_compute_service_ticket_count')

    # -------------------------------------------------------------------------
    # UNIQUE FEATURE: SERIAL-TO-WARRANTY LIFECYCLE
    # Timeline: Purchase → Warehouse Receipt → Reservation → Dispatch → Installation → Warranty → Service History
    # -------------------------------------------------------------------------
    lifecycle_stage = fields.Selection([
        ('purchase', '1. Purchase'),
        ('receipt', '2. Warehouse Receipt'),
        ('reservation', '3. Reservation'),
        ('dispatch', '4. Dispatch'),
        ('installation', '5. Installation'),
        ('warranty', '6. Warranty Active'),
        ('service', '7. Service History'),
    ], string='Lifecycle Stage', compute='_compute_lifecycle_stage', store=True, tracking=True)

    lifecycle_timeline_html = fields.Html(
        string='Serial-to-Warranty Lifecycle Timeline',
        compute='_compute_lifecycle_timeline',
        help="Visual progression: Purchase → Warehouse Receipt → Reservation → Dispatch → Installation → Warranty → Service History"
    )

    def _compute_warranty_count(self):
        for lot in self:
            lot.warranty_count = len(lot.warranty_ids)

    def _compute_service_ticket_count(self):
        for lot in self:
            lot.service_ticket_count = len(lot.service_ticket_ids)

    @api.depends('allocation_status', 'warranty_ids.status', 'service_ticket_ids', 'installation_id.state')
    def _compute_lifecycle_stage(self):
        for lot in self:
            if lot.service_ticket_ids:
                lot.lifecycle_stage = 'service'
            elif any(w.status == 'active' for w in lot.warranty_ids):
                lot.lifecycle_stage = 'warranty'
            elif lot.allocation_status == 'installed' or (lot.installation_id and lot.installation_id.state == 'completed'):
                lot.lifecycle_stage = 'installation'
            elif lot.allocation_status == 'dispatched':
                lot.lifecycle_stage = 'dispatch'
            elif lot.allocation_status == 'allocated':
                lot.lifecycle_stage = 'reservation'
            elif lot.receipt_date:
                lot.lifecycle_stage = 'receipt'
            else:
                lot.lifecycle_stage = 'purchase'

    @api.depends('lifecycle_stage', 'warranty_ids', 'service_ticket_ids', 'installation_id', 'dispatch_date', 'commissioning_date')
    def _compute_lifecycle_timeline(self):
        """Generates dynamic HTML timeline tracking actual Odoo record progression."""
        for lot in self:
            stages = [
                ('1. Purchase', lot.purchase_date or 'Logged', True, 'OEM Procurement verified'),
                ('2. Warehouse Receipt', lot.receipt_date or 'Logged', True, 'Received in Solar Central Warehouse'),
                ('3. Reservation', lot.reservation_date or (lot.sale_order_id.name if lot.sale_order_id else False),
                 lot.allocation_status in ['allocated', 'dispatched', 'installed', 'warranty_active', 'rma_service'],
                 f"Order: {lot.sale_order_id.name}" if lot.sale_order_id else "Reserved for EPC Project"),
                ('4. Dispatch', lot.dispatch_date or False,
                 lot.allocation_status in ['dispatched', 'installed', 'warranty_active', 'rma_service'],
                 "Dispatched with Delivery Gatepass"),
                ('5. Installation', lot.commissioning_date or (lot.installation_id.name if lot.installation_id else False),
                 lot.allocation_status in ['installed', 'warranty_active', 'rma_service'] or (lot.installation_id and lot.installation_id.state == 'completed'),
                 f"Project: {lot.installation_id.name}" if lot.installation_id else "Tested & Energized"),
                ('6. Warranty', lot.warranty_ids[0].name if lot.warranty_ids else False,
                 any(w.status == 'active' for w in lot.warranty_ids),
                 f"Digital Cert: {lot.warranty_ids[0].name}" if lot.warranty_ids else "Coverage active upon commissioning"),
                ('7. Service History', f"{len(lot.service_ticket_ids)} Ticket(s)" if lot.service_ticket_ids else "Clean Record",
                 bool(lot.service_ticket_ids),
                 f"Tickets logged: {len(lot.service_ticket_ids)}" if lot.service_ticket_ids else "No faults reported"),
            ]

            html = '<div style="display:flex; flex-wrap:wrap; gap:12px; margin:15px 0; font-family:sans-serif;">'
            for title, date_ref, is_done, desc in stages:
                bg = "#e6f4ea" if is_done else "#f1f3f4"
                border = "#34a853" if is_done else "#dadce0"
                color = "#137333" if is_done else "#5f6368"
                badge = "✓" if is_done else "○"

                html += f'''
                <div style="flex:1; min-width:140px; border-top:4px solid {border}; background:{bg}; padding:10px; border-radius:4px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                    <div style="font-size:11px; font-weight:bold; color:{color}; text-transform:uppercase;">{badge} {title}</div>
                    <div style="font-size:12px; font-weight:bold; color:#202124; margin:4px 0;">{date_ref or 'Pending'}</div>
                    <div style="font-size:11px; color:#5f6368;">{desc}</div>
                </div>
                '''
            html += '</div>'
            lot.lifecycle_timeline_html = html

    @api.constrains('installation_id', 'allocation_status')
    def _check_single_active_allocation(self):
        """Enforces Business Rule: Do not allocate the same active serial number to multiple installations."""
        for lot in self:
            if lot.installation_id and lot.allocation_status in ['allocated', 'dispatched', 'installed', 'warranty_active']:
                duplicates = self.search([
                    ('id', '!=', lot.id),
                    ('name', '=', lot.name),
                    ('product_id', '=', lot.product_id.id),
                    ('installation_id', '!=', False),
                    ('installation_id', '!=', lot.installation_id.id),
                    ('allocation_status', 'in', ['allocated', 'dispatched', 'installed', 'warranty_active']),
                ])
                if duplicates:
                    raise ValidationError(_("Serial Number '%s' is already actively allocated to Project '%s'!")
                                          % (lot.name, duplicates[0].installation_id.name))


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    installation_id = fields.Many2one(
        'solarflow.installation',
        string='Solar Installation Project',
        compute='_compute_installation_id',
        store=True,
        readonly=False
    )
    is_solar_dispatch = fields.Boolean(
        string='Is Solar Equipment Dispatch',
        compute='_compute_is_solar_dispatch',
        store=True
    )

    @api.depends('sale_id')
    def _compute_installation_id(self):
        for picking in self:
            if picking.sale_id and picking.sale_id.installation_id:
                picking.installation_id = picking.sale_id.installation_id

    @api.depends('sale_id.is_solar_order')
    def _compute_is_solar_dispatch(self):
        for picking in self:
            picking.is_solar_dispatch = bool(picking.sale_id and picking.sale_id.is_solar_order)

    def button_validate(self):
        """Enforces Business Rules:
        1. Dispatch must follow configured payment policy (sale_id.dispatch_permission == True).
        2. Require appropriate serial numbers before dispatch for tracked products.
        3. Updates allocated lots to dispatched and connects to installation and customer.
        """
        # Security Enforcement: Only Warehouse Manager or Super Administrator
        if not (self.env.user.has_group('solarflow_management.group_solarflow_warehouse_manager') or
                self.env.user.has_group('solarflow_management.group_solarflow_admin')):
            raise AccessError(_("Security Violation: Only Warehouse Managers or Super Administrators have permission to validate stock dispatches."))

        for picking in self:
            # Check Payment Policy for outgoing dispatches
            if picking.picking_type_code == 'outgoing' and picking.is_solar_dispatch:
                order = picking.sale_id
                if order and not order.dispatch_permission:
                    raise UserError(_(
                        "Dispatch Blocked by Payment Policy!\n\n"
                        "Sales Order '%s' requires at least %s%% advance payment ($%s).\n"
                        "Current Amount Paid: $%s (Status: %s).\n\n"
                        "Please record customer advance payment in Accounting before dispatching equipment."
                    ) % (order.name, order.advance_payment_pct, order.advance_payment_amount, order.amount_paid, order.payment_status))

                # Check serial number requirement on tracked products
                for move in picking.move_ids:
                    if move.product_id.tracking in ['serial', 'lot']:
                        assigned_lots = move.move_line_ids.mapped('lot_id')
                        if not assigned_lots:
                            raise ValidationError(_(
                                "Serial Number Required for Tracked Equipment!\n"
                                "Product '%s' is serial-tracked. Please assign valid serial numbers to move lines before dispatch."
                            ) % move.product_id.name)

        res = super(StockPicking, self).button_validate()

        # Update dispatched equipment lots and link to installation project
        for picking in self:
            if picking.picking_type_code == 'outgoing' and picking.is_solar_dispatch:
                inst = picking.installation_id or (picking.sale_id and picking.sale_id.installation_id)
                for move in picking.move_ids:
                    for line in move.move_line_ids:
                        if line.lot_id:
                            lot = line.lot_id
                            lot.write({
                                'allocation_status': 'dispatched',
                                'dispatch_date': fields.Date.today(),
                                'installation_id': inst.id if inst else False,
                                'customer_id': picking.partner_id.id if picking.partner_id else False,
                                'sale_order_id': picking.sale_id.id if picking.sale_id else False,
                            })
                            if inst and lot.id not in inst.lot_ids.ids:
                                inst.lot_ids = [(4, lot.id)]

        return res
