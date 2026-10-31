# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SolarSerialRegistry(models.Model):
    _name = 'solar.serial.registry'
    _description = 'Solar Serialized Component Registry'
    _inherit = ['mail.thread']
    _order = 'component_category asc, id asc'

    name = fields.Char(string='Serial Number', required=True, tracking=True, copy=False)
    installation_project_id = fields.Many2one('solar.installation.project', string='Installation Project', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='installation_project_id.customer_id', string='Customer', store=True)

    component_category = fields.Selection([
        ('panel', 'Solar PV Module'),
        ('inverter', 'Solar Inverter / PCU'),
        ('battery', 'Lithium / Tubular Battery'),
        ('smart_meter', 'Bi-Directional Smart Meter'),
        ('gateway', 'IoT Data Logger / Gateway'),
    ], string='Component Type', required=True, default='panel', tracking=True)

    brand_oem = fields.Char(string='Manufacturer / Brand (OEM)', required=True)
    model_number = fields.Char(string='OEM Model Number')
    spec_rating = fields.Char(string='Specification (e.g. 550W / 5kW / 5kWh)')

    # Dispatch & Commissioning Details
    dispatch_date = fields.Date(string='Dispatched Date', default=fields.Date.today)
    commissioning_date = fields.Date(string='Commissioning Date')
    barcode_scanned = fields.Boolean(string='Scanned at Site', default=True)

    # Warranty Link
    warranty_years = fields.Integer(string='OEM Warranty Duration (Years)', default=25)
    warranty_card_id = fields.Many2one('solar.warranty.card', string='Warranty Certificate', readonly=True)
    status = fields.Selection([
        ('staged', 'Staged in Warehouse'),
        ('dispatched', 'Dispatched to Site'),
        ('installed', 'Mounted & Tested'),
        ('commissioned', 'Commissioned Active'),
        ('rma', 'Under RMA / Service Claim'),
        ('replaced', 'Replaced'),
    ], string='Life Cycle Status', default='staged', tracking=True)

    _sql_constraints = [
        ('serial_unique', 'unique(name)', 'This Component Serial Number is already registered in the system!')
    ]
