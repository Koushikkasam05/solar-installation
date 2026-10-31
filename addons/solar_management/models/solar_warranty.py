# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
import hashlib

class SolarWarrantyCard(models.Model):
    _name = 'solar.warranty.card'
    _description = 'Solar Digital Warranty Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Certificate Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    installation_project_id = fields.Many2one('solar.installation.project', string='Commissioned Project', required=True, ondelete='cascade', tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer / Beneficiary', required=True, tracking=True)

    warranty_type = fields.Selection([
        ('module_perf', '25-Year Solar PV Module Linear Output Warranty'),
        ('inverter', 'Grid-Tie Inverter Replacement Warranty'),
        ('battery', 'Energy Storage Battery Cycle Life Warranty'),
        ('workmanship', 'EPC Workmanship & Roof Integrity Warranty'),
    ], string='Warranty Category', required=True, default='module_perf', tracking=True)

    oem_brand = fields.Char(string='OEM Manufacturer / Certifier', required=True)
    duration_years = fields.Integer(string='Duration (Years)', default=25, required=True)
    start_date = fields.Date(string='Warranty Start Date', default=fields.Date.today, required=True)
    expiry_date = fields.Date(string='Warranty Expiration Date', compute='_compute_expiry_date', store=True)

    verification_hash = fields.Char(string='Digital Verification Token', compute='_compute_verification_token', store=True)
    terms_and_conditions = fields.Text(string='Terms & Coverage SLA')

    status = fields.Selection([
        ('active', 'Active & Valid'),
        ('claim_in_progress', 'Warranty Claim Under Review'),
        ('claim_resolved', 'RMA Replacement Completed'),
        ('expired', 'Warranty Period Concluded'),
    ], string='Status', default='active', tracking=True)

    claim_notes = fields.Text(string='Warranty Claim / RMA History')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('solar.warranty.card') or _('New')
        return super(SolarWarrantyCard, self).create(vals)

    @api.depends('start_date', 'duration_years')
    def _compute_expiry_date(self):
        for card in self:
            if card.start_date and card.duration_years:
                card.expiry_date = card.start_date + relativedelta(years=card.duration_years)
            else:
                card.expiry_date = False

    @api.depends('name', 'customer_id', 'start_date')
    def _compute_verification_token(self):
        for card in self:
            raw_str = f"{card.name}-{card.customer_id.id}-{card.start_date}-SOLAR-SECURE"
            card.verification_hash = hashlib.sha256(raw_str.encode()).hexdigest()[:16].upper()

    def action_file_claim(self):
        self.write({'status': 'claim_in_progress'})

    def action_resolve_claim(self):
        self.write({'status': 'claim_resolved'})
