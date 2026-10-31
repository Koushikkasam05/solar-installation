# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SolarServiceTicket(models.Model):
    _name = 'solar.service.ticket'
    _description = 'Solar After-Sales Service & Maintenance Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char(string='Ticket Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    installation_project_id = fields.Many2one('solar.installation.project', string='Installed Site', required=True, tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    technician_id = fields.Many2one('res.users', string='Assigned Field Engineer', tracking=True)

    issue_category = fields.Selection([
        ('inverter_fault', 'Inverter Error Code / Fault Alert'),
        ('generation_drop', 'Low Generation / Soiling Degradation'),
        ('amc_cleaning', 'Scheduled Solar Module Cleaning'),
        ('preventative_check', 'Annual Electrical Preventative Inspection'),
        ('meter_issue', 'Net Metering / DISCOM Tariff Discrepancy'),
        ('physical_damage', 'Physical Damage (Hail / Monkeys / Storm)'),
    ], string='Issue Classification', required=True, default='generation_drop', tracking=True)

    inverter_error_code = fields.Char(string='Inverter Error Code (e.g. Err02, PV Overvolt)')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Emergency (System Down)'),
    ], string='Priority', default='1', tracking=True)

    description = fields.Text(string='Customer Description & Symptoms', required=True)
    resolution_details = fields.Text(string='Technician Resolution Notes')

    scheduled_date = fields.Datetime(string='Scheduled Service Visit', default=fields.Datetime.now)
    resolved_date = fields.Datetime(string='Resolved Date')

    state = fields.Selection([
        ('new', 'New Request'),
        ('assigned', 'Technician Dispatched'),
        ('in_progress', 'Site Diagnosis / Maintenance'),
        ('resolved', 'Resolved & Operational'),
        ('closed', 'Closed & Verified'),
    ], string='Status', default='new', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('solar.service.ticket') or _('New')
        return super(SolarServiceTicket, self).create(vals)

    def action_assign(self):
        self.write({'state': 'assigned'})

    def action_start_service(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        self.write({
            'state': 'resolved',
            'resolved_date': fields.Datetime.now()
        })

    def action_close(self):
        self.write({'state': 'closed'})


class SolarAmcContract(models.Model):
    _name = 'solar.amc.contract'
    _description = 'Solar Annual Maintenance Contract (AMC)'
    _inherit = ['mail.thread']

    name = fields.Char(string='AMC Agreement Ref', required=True)
    installation_project_id = fields.Many2one('solar.installation.project', string='Installed Solar Plant', required=True)
    customer_id = fields.Many2one('res.partner', string='Client', required=True)
    start_date = fields.Date(string='Contract Start Date', default=fields.Date.today, required=True)
    end_date = fields.Date(string='Contract Expiry Date', required=True)

    annual_cleanings_planned = fields.Integer(string='Planned Module Wash Cycles', default=12)
    cleanings_completed = fields.Integer(string='Cleanings Completed', default=0)
    contract_amount = fields.Monetary(string='Annual AMC Fee', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    status = fields.Selection([
        ('active', 'Active Contract'),
        ('renew_due', 'Renewal Due'),
        ('expired', 'Expired'),
    ], string='AMC Status', default='active')
