# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SolarFlowSurveyRejectWizard(models.TransientModel):
    _name = 'solarflow.survey.reject.wizard'
    _description = 'Survey Rejection Reason Wizard'

    survey_id = fields.Many2one('solarflow.survey', string='Survey', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_confirm_rejection(self):
        self.ensure_one()
        if not self.rejection_reason or not self.rejection_reason.strip():
            raise ValidationError(_("A valid rejection reason must be provided."))
        self.survey_id.action_reject(reason=self.rejection_reason)
        return {'type': 'ir.actions.act_window_close'}
