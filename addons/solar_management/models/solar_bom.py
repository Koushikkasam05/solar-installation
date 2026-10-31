# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SolarBomLine(models.Model):
    _name = 'solar.bom.line'
    _description = 'Solar Bill of Materials Item'
    _order = 'category asc, id asc'

    survey_id = fields.Many2one('solar.site.survey', string='Site Survey', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Inventory Item')
    name = fields.Char(string='Component Description', required=True)
    category = fields.Selection([
        ('panel', 'PV Solar Modules'),
        ('inverter', 'Solar Inverter / PCU'),
        ('battery', 'Battery Storage Bank'),
        ('structure', 'Module Mounting Structure & Hardware'),
        ('cable', 'Solar DC & AC Armored Cables'),
        ('bos', 'Balance of System (DBs, Earthing, LA, Conduit)'),
        ('labor', 'Installation, Civil & Commissioning Labor'),
    ], string='Component Category', required=True, default='bos')

    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    uom = fields.Char(string='Unit of Measure', default='Units')
    unit_cost = fields.Monetary(string='Unit Cost', default=0.0, required=True)
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    notes = fields.Char(string='Technical Specification Notes')

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.unit_cost
