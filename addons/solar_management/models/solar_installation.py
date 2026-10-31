# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SolarInstallationProject(models.Model):
    _name = 'solar.installation.project'
    _description = 'Solar EPC Installation & Field Commissioning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Project ID', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    sale_order_id = fields.Many2one('sale.order', string='Sales Contract', required=True, tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    survey_id = fields.Many2one('solar.site.survey', string='Site Survey Reference')

    # Team & Schedule
    supervisor_id = fields.Many2one('res.users', string='Lead Site Engineer / Supervisor', default=lambda self: self.env.user, tracking=True)
    technician_ids = fields.Many2many('res.users', 'solar_project_technician_rel', 'project_id', 'user_id', string='Field Electricians & Crew')
    start_date = fields.Date(string='Installation Start Date', default=fields.Date.today, tracking=True)
    target_completion_date = fields.Date(string='Target Commissioning Date', tracking=True)
    actual_commissioning_date = fields.Date(string='Actual Handover Date')

    # System Profile
    system_capacity_kw = fields.Float(string='Capacity (kW)', default=3.0)
    system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid'),
        ('hybrid', 'Hybrid with Battery'),
        ('off_grid', 'Off-Grid Standalone'),
    ], string='System Type', default='on_grid')
    roof_type = fields.Selection([
        ('rcc_flat', 'RCC Flat Roof'),
        ('metal_sheet', 'Metal Sheet'),
        ('clay_tile', 'Pitched Tile'),
        ('asbestos', 'Asbestos Sheet'),
        ('ground_mount', 'Ground Mount'),
    ], string='Roof Architecture')

    # 6-Phase Commissioning Milestone Checklist
    phase_1_structure = fields.Boolean(string='Phase 1: Civil & Structure Grouting Done', default=False, tracking=True)
    phase_2_modules = fields.Boolean(string='Phase 2: PV Modules Mounted & Stringed', default=False, tracking=True)
    phase_3_inverter = fields.Boolean(string='Phase 3: Inverter, ACDB & DCDB Wired', default=False, tracking=True)
    phase_4_earthing = fields.Boolean(string='Phase 4: Earthing (<5Ω) & LA Installed', default=False, tracking=True)
    phase_5_testing = fields.Boolean(string='Phase 5: Electrical QC & Megger Testing Done', default=False, tracking=True)
    phase_6_discom_sync = fields.Boolean(string='Phase 6: DISCOM Net Metering Sync Active', default=False, tracking=True)

    progress_percent = fields.Float(string='Commissioning Progress (%)', compute='_compute_progress', store=True)

    # Electrical QC & Verification Log
    test_string1_voc = fields.Float(string='String 1 Open Circuit Voltage (Voc - Volts)')
    test_string1_isc = fields.Float(string='String 1 Short Circuit Current (Isc - Amps)')
    test_string2_voc = fields.Float(string='String 2 Open Circuit Voltage (Voc - Volts)')
    test_string2_isc = fields.Float(string='String 2 Short Circuit Current (Isc - Amps)')
    test_earth_resistance_ohms = fields.Float(string='Earth Pit Resistance (Ohms)', default=2.8, help="Must be under 5.0 Ohms")
    test_insulation_resistance_mohm = fields.Float(string='Insulation Megger Test (Mega-Ohms)', default=150.0)
    test_grid_voltage = fields.Float(string='Grid AC Voltage (Volts)', default=235.0)

    # Installation Evidences / Photos
    photo_structure_erection = fields.Binary(string='Structure Installation Photo', attachment=True)
    photo_panel_layout = fields.Binary(string='Mounted Panels Photo', attachment=True)
    photo_inverter_wiring = fields.Binary(string='Inverter & DB Wiring Photo', attachment=True)
    photo_earthing_pit = fields.Binary(string='Earthing Chamber Photo', attachment=True)
    photo_net_meter = fields.Binary(string='Bi-Directional Net Meter Photo', attachment=True)

    # Serial Registry
    serial_registry_ids = fields.One2many('solar.serial.registry', 'installation_project_id', string='Serialized Components')
    serial_count = fields.Integer(string='Registered Serial Count', compute='_compute_serial_count')

    # Warranty Link
    warranty_card_ids = fields.One2many('solar.warranty.card', 'installation_project_id', string='Issued Warranty Certificates')
    warranty_count = fields.Integer(string='Warranty Count', compute='_compute_warranty_count')

    # Service & Maintenance Link
    ticket_ids = fields.One2many('solar.service.ticket', 'installation_project_id', string='Service Tickets')

    # Job Costing Link
    costing_id = fields.Many2one('solar.project.costing', string='Project Costing Record', readonly=True)

    # Project Workflow Status
    state = fields.Selection([
        ('draft', 'Project Initiated'),
        ('scheduled', 'Field Crew Assigned'),
        ('structure', 'Structure Erection'),
        ('cabling', 'Module & DB Cabling'),
        ('testing', 'Electrical Testing & QC'),
        ('discom_sync', 'DISCOM Net Meter Sync'),
        ('commissioned', 'System Commissioned & Handed Over'),
        ('cancelled', 'Cancelled'),
    ], string='Project State', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('solar.installation.project') or _('New')
        return super(SolarInstallationProject, self).create(vals)

    @api.depends('phase_1_structure', 'phase_2_modules', 'phase_3_inverter', 'phase_4_earthing', 'phase_5_testing', 'phase_6_discom_sync')
    def _compute_progress(self):
        for p in self:
            phases = [p.phase_1_structure, p.phase_2_modules, p.phase_3_inverter, p.phase_4_earthing, p.phase_5_testing, p.phase_6_discom_sync]
            completed = sum(1 for item in phases if item)
            p.progress_percent = round((completed / 6.0) * 100.0, 1)

    def _compute_serial_count(self):
        for p in self:
            p.serial_count = len(p.serial_registry_ids)

    def _compute_warranty_count(self):
        for p in self:
            p.warranty_count = len(p.warranty_card_ids)

    def action_schedule(self):
        self.write({'state': 'scheduled'})

    def action_start_structure(self):
        self.write({'state': 'structure', 'phase_1_structure': True})

    def action_cabling_done(self):
        self.write({
            'state': 'cabling',
            'phase_2_modules': True,
            'phase_3_inverter': True,
            'phase_4_earthing': True,
        })

    def action_testing_qc(self):
        self.ensure_one()
        if self.test_earth_resistance_ohms > 5.0:
            raise UserError(_("Earth Pit Resistance must be below 5.0 Ohms (measured: %s Ohms). Please add chemical compound.") % self.test_earth_resistance_ohms)
        self.write({
            'state': 'testing',
            'phase_5_testing': True
        })

    def action_discom_sync(self):
        self.write({
            'state': 'discom_sync',
            'phase_6_discom_sync': True
        })

    def action_commission_and_handover(self):
        self.ensure_one()
        if not (self.phase_1_structure and self.phase_2_modules and self.phase_3_inverter and self.phase_4_earthing and self.phase_5_testing and self.phase_6_discom_sync):
            raise UserError(_("Cannot commission project until all 6 Commissioning Milestones are verified and checked!"))

        self.write({
            'state': 'commissioned',
            'actual_commissioning_date': fields.Date.today()
        })

        # Auto-generate Digital Warranty Cards for customer
        self.action_issue_warranty_certificates()

        # Auto-create Project Costing record if not already created
        if not self.costing_id:
            costing = self.env['solar.project.costing'].create({
                'name': f"COST-{self.name}",
                'project_id': self.id,
                'customer_id': self.customer_id.id,
                'contract_revenue': self.sale_order_id.amount_total,
                'bom_hardware_cost': round(self.system_capacity_kw * 420.0, 2),
                'structure_civil_cost': round(self.system_capacity_kw * 45.0, 2),
                'electrical_bos_cost': round(self.system_capacity_kw * 35.0, 2),
                'labor_technician_cost': round(self.system_capacity_kw * 30.0, 2),
                'discom_liaisoning_cost': 120.0,
                'transportation_cost': 60.0,
            })
            self.costing_id = costing.id

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Solar System Commissioned!'),
                'message': _('System successfully commissioned! Warranty certificates and financial costing generated.'),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_issue_warranty_certificates(self):
        self.ensure_one()
        # Create standard warranty certificate
        self.warranty_card_ids.unlink()

        comm_date = self.actual_commissioning_date or fields.Date.today()
        # 1. 25-Year Solar PV Module Performance Warranty
        self.env['solar.warranty.card'].create({
            'installation_project_id': self.id,
            'customer_id': self.customer_id.id,
            'warranty_type': 'module_perf',
            'duration_years': 25,
            'start_date': comm_date,
            'oem_brand': 'Tier-1 Certified PV Modules',
            'terms_and_conditions': 'Guarantees minimum 90% peak output at Year 10 and 80% peak output at Year 25.',
        })

        # 2. 10-Year Inverter Warranty
        self.env['solar.warranty.card'].create({
            'installation_project_id': self.id,
            'customer_id': self.customer_id.id,
            'warranty_type': 'inverter',
            'duration_years': 10 if self.system_type == 'on_grid' else 5,
            'start_date': comm_date,
            'oem_brand': 'Smart Grid-Tied Inverter OEM',
            'terms_and_conditions': 'Full replacement warranty on inverter power electronics and internal MPPT circuitry.',
        })

        # 3. 5-Year Workmanship & Civil Warranty
        self.env['solar.warranty.card'].create({
            'installation_project_id': self.id,
            'customer_id': self.customer_id.id,
            'warranty_type': 'workmanship',
            'duration_years': 5,
            'start_date': comm_date,
            'oem_brand': 'Solar EPC Workmanship Standard',
            'terms_and_conditions': 'Guarantees structural mounting integrity against wind speeds up to 150 km/h and zero roof leakage.',
        })
