# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math

class SolarBomGeneratorWizard(models.TransientModel):
    _name = 'solar.bom.generator.wizard'
    _description = 'Generate Dynamic Solar BOM'

    survey_id = fields.Many2one('solar.site.survey', string='Site Survey', required=True)
    package_id = fields.Many2one('solar.package', string='Solar Package', required=True)
    panel_wattage = fields.Integer(string='Panel Wattage (Watts)', default=550, required=True)
    inverter_type = fields.Selection([
        ('string', 'String Inverter (Grid-tied)'),
        ('micro', 'Microinverters'),
        ('hybrid', 'Hybrid Inverter (Battery Ready)'),
    ], string='Inverter Architecture', default='string', required=True)
    cable_run_length = fields.Float(string='Estimated Cable Run (Meters)', default=30.0)

    calculated_panels = fields.Integer(string='Calculated Panels', compute='_compute_calculations')
    calculated_inverter_kw = fields.Float(string='Inverter Sizing (kW)', compute='_compute_calculations')

    @api.depends('package_id', 'panel_wattage')
    def _compute_calculations(self):
        for rec in self:
            if rec.package_id and rec.panel_wattage > 0:
                total_watts = rec.package_id.system_capacity_kw * 1000.0
                rec.calculated_panels = math.ceil(total_watts / rec.panel_wattage)
                rec.calculated_inverter_kw = round(rec.package_id.system_capacity_kw * 1.0, 2)
            else:
                rec.calculated_panels = 0
                rec.calculated_inverter_kw = 0.0

    def action_generate_bom(self):
        self.ensure_one()
        if not self.survey_id:
            raise UserError(_("Survey reference missing."))
        # Call the survey's BOM generator
        return self.survey_id.action_generate_automatic_bom(
            package_id=self.package_id.id,
            panel_wattage=self.panel_wattage,
            cable_run_length=self.cable_run_length
        )
