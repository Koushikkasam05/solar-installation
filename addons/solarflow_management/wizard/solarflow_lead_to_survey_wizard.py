# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SolarFlowLeadToSurveyWizard(models.TransientModel):
    _name = 'solarflow.lead.to.survey.wizard'
    _description = 'Schedule Site Survey from Lead'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True)
    surveyor_id = fields.Many2one('res.users', string='Assigned Surveyor', required=True, default=lambda self: self.env.user)
    scheduled_date = fields.Datetime(string='Scheduled Date', default=fields.Datetime.now, required=True)
    notes = fields.Text(string='Survey Instructions')

    def action_confirm_schedule(self):
        self.ensure_one()
        return self.lead_id.action_schedule_site_survey()
