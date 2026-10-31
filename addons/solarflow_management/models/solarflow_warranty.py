# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import hashlib

class SolarFlowWarranty(models.Model):
    _name = 'solarflow.warranty'
    _description = 'SolarFlow Digital Warranty Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(
        string='Warranty Reference',
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
    installation_id = fields.Many2one(
        'solarflow.installation',
        string='Installation Reference',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        related='installation_id.sale_order_id',
        store=True,
        tracking=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product / Component',
        required=True,
        tracking=True
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Equipment Serial Number',
        tracking=True,
        index=True,
        domain="[('product_id', '=', product_id)]",
        help="Specific serialized hardware item covered under this warranty."
    )

    warranty_type = fields.Selection([
        ('inverter', 'Solar Inverter Replacement Warranty'),
        ('battery', 'Battery Storage Degradation & Cycle Warranty'),
        ('panel', 'PV Solar Module 25-Year Linear Output Warranty'),
        ('workmanship', 'EPC Workmanship & Roof Integrity Warranty'),
        ('other', 'Balance of System OEM Warranty'),
    ], string='Coverage Policy Category', required=True, default='inverter', tracking=True)

    # Configurable Warranty Terms
    duration_months = fields.Integer(string='Duration (Months)', default=24, tracking=True)
    duration_years = fields.Float(string='Duration (Years)', compute='_compute_duration_years', inverse='_inverse_duration_years', store=True)
    start_date = fields.Date(string='Warranty Start Date', default=fields.Date.today, required=True, tracking=True)
    expiry_date = fields.Date(string='Warranty Expiry Date', compute='_compute_expiry_date', store=True, tracking=True)

    # Status: Upcoming, Active, Expired
    status = fields.Selection([
        ('upcoming', 'Upcoming (Pre-Commissioning)'),
        ('active', 'Active Coverage'),
        ('expired', 'Warranty Expired'),
        ('claim', 'RMA Claim in Progress'),
    ], string='Warranty Status', compute='_compute_status', store=True, tracking=True, index=True)

    manufacturer_details = fields.Char(string='Manufacturer / OEM Brand', default='Tier-1 Certified OEM')
    warranty_document = fields.Binary(string='Warranty Certificate Document', attachment=True)
    verification_hash = fields.Char(string='SHA-256 Digital Verification Token', compute='_compute_hash', store=True)
    terms_clauses = fields.Text(string='Terms & Coverage Clauses')

    # Related Service Tickets
    ticket_ids = fields.One2many('solarflow.service.ticket', 'warranty_id', string='Service Tickets')
    ticket_count = fields.Integer(string='Tickets Count', compute='_compute_ticket_count')

    _sql_constraints = [
        ('solarflow_warranty_name_unique', 'unique(name)', 'Warranty Reference must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solarflow.warranty.seq') or _('WRNT-NEW')
        records = super(SolarFlowWarranty, self).create(vals_list)
        records._check_duplicate_active_warranty()
        return records

    def write(self, vals):
        res = super(SolarFlowWarranty, self).write(vals)
        self._check_duplicate_active_warranty()
        return res

    @api.constrains('lot_id', 'product_id', 'warranty_type', 'status')
    def _check_duplicate_active_warranty(self):
        """Enforces Business Rule 5: Prevent duplicate active warranty records for the same equipment and coverage."""
        for rec in self:
            if rec.lot_id and rec.status in ['active', 'upcoming']:
                duplicates = self.search([
                    ('id', '!=', rec.id),
                    ('lot_id', '=', rec.lot_id.id),
                    ('warranty_type', '=', rec.warranty_type),
                    ('status', 'in', ['active', 'upcoming']),
                ])
                if duplicates:
                    raise ValidationError(_(
                        "Duplicate Active Warranty Blocked!\n"
                        "Equipment Serial '%s' already has an active %s warranty under reference '%s'."
                    ) % (rec.lot_id.name, rec.warranty_type, duplicates[0].name))

    @api.depends('duration_months')
    def _compute_duration_years(self):
        for rec in self:
            rec.duration_years = round(rec.duration_months / 12.0, 1)

    def _inverse_duration_years(self):
        for rec in self:
            rec.duration_months = int(rec.duration_years * 12)

    @api.depends('start_date', 'duration_months')
    def _compute_expiry_date(self):
        for rec in self:
            if rec.start_date and rec.duration_months:
                rec.expiry_date = rec.start_date + relativedelta(months=rec.duration_months)
            else:
                rec.expiry_date = False

    @api.depends('start_date', 'expiry_date')
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            if not rec.start_date or not rec.expiry_date:
                rec.status = 'upcoming'
            elif today < rec.start_date:
                rec.status = 'upcoming'
            elif rec.start_date <= today <= rec.expiry_date:
                rec.status = 'active'
            else:
                rec.status = 'expired'

    @api.depends('name', 'customer_id', 'start_date', 'lot_id')
    def _compute_hash(self):
        for rec in self:
            serial = rec.lot_id.name if rec.lot_id else 'GENERAL'
            raw = f"SOLARFLOW-{rec.name}-{rec.customer_id.id}-{serial}-{rec.start_date}"
            rec.verification_hash = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = len(rec.ticket_ids)

    @api.model
    def action_check_warranty_expiry(self):
        """Automated cron action: checks warranties expiring within 30 days and sends reminder activities."""
        today = fields.Date.today()
        upcoming_expiry_date = today + relativedelta(days=30)
        expiring_warranties = self.search([
            ('status', '=', 'active'),
            ('expiry_date', '<=', upcoming_expiry_date),
            ('expiry_date', '>=', today),
        ])
        for wrnt in expiring_warranties:
            wrnt.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_("Warranty Expiring Soon: %s") % wrnt.name,
                note=_("Warranty for %s (Serial %s) expires on %s. Contact customer %s for AMC renewal.")
                     % (wrnt.product_id.name, wrnt.lot_id.name if wrnt.lot_id else 'N/A', wrnt.expiry_date, wrnt.customer_id.name),
                user_id=wrnt.installation_id.supervisor_id.id or self.env.uid
            )
        return True
