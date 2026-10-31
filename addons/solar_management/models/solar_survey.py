# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math

class SolarSiteSurvey(models.Model):
    _name = 'solar.site.survey'
    _description = 'Solar Rooftop Site Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Survey Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    lead_id = fields.Many2one('crm.lead', string='Source Lead / Opportunity', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    surveyor_id = fields.Many2one('res.users', string='Assigned Surveyor', default=lambda self: self.env.user, tracking=True)
    engineer_id = fields.Many2one('res.users', string='Approving Solar Engineer', tracking=True)
    
    # Scheduling & Geo Coordinates
    scheduled_date = fields.Datetime(string='Scheduled Date', default=fields.Datetime.now, tracking=True)
    completed_date = fields.Datetime(string='Survey Completed Date')
    site_address = fields.Char(string='Site Address')
    latitude = fields.Float(string='Latitude (GPS)', digits=(10, 7))
    longitude = fields.Float(string='Longitude (GPS)', digits=(10, 7))

    # Roof Assessment
    roof_type = fields.Selection([
        ('rcc_flat', 'RCC Flat Concrete Roof'),
        ('metal_sheet', 'Trapezoidal / Industrial Metal Sheet'),
        ('clay_tile', 'Pitched Clay Tile Roof'),
        ('asbestos', 'Corrugated Asbestos / Cement Sheet'),
        ('ground_mount', 'Ground Mounted Open Yard'),
    ], string='Roof Architecture Type', default='rcc_flat', required=True, tracking=True)

    roof_area_sqft = fields.Float(string='Total Roof Area (sq. ft.)', default=1000.0)
    usable_area_sqft = fields.Float(string='Shadow-Free Usable Area (sq. ft.)', default=750.0)
    roof_tilt_deg = fields.Float(string='Roof Pitch / Tilt Angle (°)', default=12.0)
    azimuth_deg = fields.Float(string='Azimuth Angle (° from South)', default=180.0, help="180° is True South")
    floor_level = fields.Integer(string='Building Floor Level', default=2)
    structural_soundness = fields.Selection([
        ('excellent', 'Excellent (Heavy Structural Load Rated)'),
        ('good', 'Good (Standard Solar Elevated Mount OK)'),
        ('reinforce', 'Requires Structural Reinforcement'),
        ('unsafe', 'Unsafe / Low Load Bearing'),
    ], string='Structural Integrity', default='good', required=True)

    # Shading Analysis
    shadow_profile = fields.Selection([
        ('clear', '100% Shadow-Free (Sunlit 9:00 AM - 4:30 PM)'),
        ('morning_shade', 'Minor Morning Shading (< 9:00 AM)'),
        ('afternoon_shade', 'Minor Late Afternoon Shading (> 4:30 PM)'),
        ('obstacle_shade', 'Partial Shade (Water Tank / Parapet Obstacle)'),
        ('severe_shade', 'Heavy Obstacle Shading (Not Recommended)'),
    ], string='Shading Analysis', default='clear', required=True)

    # Electrical & Balance of System (BOS) Feasibility
    db_distance_meters = fields.Float(string='Distance to Main DB (Meters)', default=25.0)
    service_phase = fields.Selection([
        ('single_phase', 'Single-Phase (230V)'),
        ('three_phase', 'Three-Phase (415V)'),
    ], string='Grid Service Phase', default='single_phase', required=True)
    meter_location = fields.Selection([
        ('ground_floor', 'Ground Floor Exterior'),
        ('stilt_basement', 'Stilt / Basement Panel Room'),
        ('customer_gate', 'Near Boundary Gate'),
    ], string='DISCOM Meter Location', default='ground_floor')
    earthing_pit_available = fields.Boolean(string='Earthing Pit Space Available', default=True)
    chemical_pits_required = fields.Integer(string='Chemical Earthing Pits Required', default=3, help="AC Earthing, DC Earthing, LA Earthing")
    lightning_arrester_req = fields.Boolean(string='Lightning Arrester Required', default=True)
    cable_tray_required = fields.Boolean(string='Dedicated Cable Tray Required', default=True)

    # Inspection Checklist
    check_roof_strength = fields.Boolean(string='Roof Load Checked & Verified', default=False)
    check_meter_box = fields.Boolean(string='Meter Box & Connected Load Checked', default=False)
    check_earthing_space = fields.Boolean(string='Earthing Soil Space Identified', default=False)
    check_cable_route = fields.Boolean(string='Conduit / Cable Route Mapped', default=False)
    check_client_briefing = fields.Boolean(string='Client In-Person Briefing Conducted', default=False)

    # Photos & Visual Evidences
    photo_roof = fields.Binary(string='Roof Panoramic Photo', attachment=True)
    photo_meter = fields.Binary(string='Existing Meter & DB Photo', attachment=True)
    photo_obstacle = fields.Binary(string='Shadow Obstacle Photo', attachment=True)
    photo_earthing = fields.Binary(string='Earthing Yard Photo', attachment=True)

    # System Recommendation & Package Selection
    recommended_kw = fields.Float(string='Surveyed Max Capacity (kW)', compute='_compute_surveyed_capacity', store=True)
    package_id = fields.Many2one('solar.package', string='Proposed Solar Package')
    system_type = fields.Selection(related='package_id.system_type', string='System Type', readonly=True)

    # Generated BOM and Sales Order
    bom_line_ids = fields.One2many('solar.bom.line', 'survey_id', string='Survey Bill of Materials')
    bom_total_cost = fields.Monetary(string='Estimated BOM Cost', compute='_compute_bom_cost', store=True)
    sale_order_id = fields.Many2one('sale.order', string='Generated Sales Quotation', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Status Workflow
    state = fields.Selection([
        ('draft', 'Draft Scheduled'),
        ('in_progress', 'Survey in Progress'),
        ('completed', 'Completed by Surveyor'),
        ('approved', 'Approved by Engineer'),
        ('rejected', 'Rejected / Infeasible'),
    ], string='Status', default='draft', tracking=True)

    rejection_reason = fields.Text(string='Rejection / Non-Feasible Reason')
    engineer_notes = fields.Text(string='Chief Engineer Review Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('solar.site.survey') or _('New')
        return super(SolarSiteSurvey, self).create(vals)

    @api.depends('usable_area_sqft', 'roof_type', 'shadow_profile')
    def _compute_surveyed_capacity(self):
        for survey in self:
            # 1 kW requires ~80-100 sq.ft.
            base_kw = survey.usable_area_sqft / 85.0 if survey.usable_area_sqft else 0.0
            if survey.shadow_profile == 'obstacle_shade':
                base_kw *= 0.85
            elif survey.shadow_profile == 'severe_shade':
                base_kw *= 0.50
            survey.recommended_kw = round(max(0.0, base_kw), 1)

    @api.depends('bom_line_ids.total_cost')
    def _compute_bom_cost(self):
        for survey in self:
            survey.bom_total_cost = sum(line.total_cost for line in survey.bom_line_ids)

    def action_start_survey(self):
        self.write({'state': 'in_progress'})

    def action_complete_survey(self):
        self.ensure_one()
        if not (self.check_roof_strength and self.check_meter_box and self.check_earthing_space):
            raise UserError(_("Please complete all mandatory checklist verification flags before submitting."))
        self.write({
            'state': 'completed',
            'completed_date': fields.Datetime.now()
        })

    def action_engineer_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'engineer_id': self.env.user.id
        })

    def action_reject(self):
        self.ensure_one()
        self.write({'state': 'rejected'})

    def action_generate_automatic_bom(self, package_id=None, panel_wattage=550, cable_run_length=None):
        self.ensure_one()
        target_pkg = self.env['solar.package'].browse(package_id) if package_id else self.package_id
        if not target_pkg:
            raise UserError(_("Please select a Solar Package first before generating the Bill of Materials."))

        # Clear existing survey BOM lines
        self.bom_line_ids.unlink()

        # Generate BOM dynamically based on package kW & engineering formulas
        system_kw = target_pkg.system_capacity_kw
        total_watts = system_kw * 1000.0
        p_watt = panel_wattage or target_pkg.default_panel_wattage or 550
        panel_count = math.ceil(total_watts / p_watt)
        cable_len = cable_run_length or (self.db_distance_meters * 2 + 10.0)

        lines_data = []

        # 1. Solar Panels
        lines_data.append({
            'survey_id': self.id,
            'category': 'panel',
            'name': f"High-Efficiency Mono-PERC / Bifacial Solar Panel ({p_watt}W)",
            'quantity': panel_count,
            'uom': 'Units',
            'unit_cost': round(p_watt * 0.28, 2), # e.g. ~$154 or equivalent
        })

        # 2. Solar Inverter
        inverter_name = f"{system_kw}kW {'3-Phase' if target_pkg.phase == 'three_phase' else '1-Phase'} Grid-Tie Solar Inverter"
        if target_pkg.system_type == 'hybrid':
            inverter_name = f"{system_kw}kW Smart Hybrid Inverter (Battery Ready)"
        lines_data.append({
            'survey_id': self.id,
            'category': 'inverter',
            'name': inverter_name,
            'quantity': 1,
            'uom': 'Unit',
            'unit_cost': round(system_kw * 120.0 + 250.0, 2),
        })

        # 3. Battery Storage (if Hybrid / Off-grid)
        if target_pkg.system_type in ['hybrid', 'off_grid']:
            lines_data.append({
                'survey_id': self.id,
                'category': 'battery',
                'name': f"LiFePO4 Lithium Battery Bank ({round(system_kw * 1.5, 1)} kWh 48V)",
                'quantity': 1,
                'uom': 'Pack',
                'unit_cost': round(system_kw * 380.0, 2),
            })

        # 4. Mounting Structure
        structure_type = "Elevated HDGI Structure (1.5m clearance)" if self.roof_type == 'rcc_flat' else "Aluminum Short Rail & EPDM Sheet Clamps"
        lines_data.append({
            'survey_id': self.id,
            'category': 'structure',
            'name': f"{structure_type} for {panel_count} Panels",
            'quantity': panel_count,
            'uom': 'Panel Slots',
            'unit_cost': 28.0 if self.roof_type == 'rcc_flat' else 14.0,
        })

        # 5. Solar DC Cable (4 sq mm / 6 sq mm UV Resistant)
        lines_data.append({
            'survey_id': self.id,
            'category': 'cable',
            'name': "Solar DC UV Resistant Flexible Copper Cable (4 sq. mm)",
            'quantity': cable_len,
            'uom': 'Meters',
            'unit_cost': 1.65,
        })

        # 6. AC Distribution Box (ACDB) & DC Distribution Box (DCDB) with SPDs
        lines_data.append({
            'survey_id': self.id,
            'category': 'bos',
            'name': f"IP65 Solar ACDB + DCDB Box with Class II SPDs and MCBs ({target_pkg.phase.replace('_', ' ').title()})",
            'quantity': 1,
            'uom': 'Set',
            'unit_cost': 95.0 if target_pkg.phase == 'single_phase' else 165.0,
        })

        # 7. Chemical Earthing & Lightning Arrester (LA)
        earthing_count = self.chemical_pits_required or 3
        lines_data.append({
            'survey_id': self.id,
            'category': 'bos',
            'name': f"Copper Bonded Chemical Earthing Rods (3m) with Bentonite Compound",
            'quantity': earthing_count,
            'uom': 'Pits',
            'unit_cost': 55.0,
        })
        if self.lightning_arrester_req:
            lines_data.append({
                'survey_id': self.id,
                'category': 'bos',
                'name': "Early Streamer Emission (ESE) / Copper Spike Lightning Arrester with 10m Mast",
                'quantity': 1,
                'uom': 'Set',
                'unit_cost': 110.0,
            })

        # Create lines in Odoo
        for l in lines_data:
            self.env['solar.bom.line'].create(l)

        self.package_id = target_pkg.id
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('BOM Generated!'),
                'message': _('Automatic Bill of Materials generated for %s kW system with %s panels.') % (system_kw, panel_count),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_create_sales_quotation(self):
        self.ensure_one()
        if self.state not in ['completed', 'approved']:
            raise UserError(_("Please complete and approve the site survey before generating a quotation."))
        if not self.bom_line_ids:
            self.action_generate_automatic_bom()

        # Create Sale Order
        order_vals = {
            'partner_id': self.partner_id.id,
            'opportunity_id': self.lead_id.id if self.lead_id else False,
            'survey_id': self.id,
            'package_id': self.package_id.id,
            'is_solar_order': True,
            'system_capacity_kw': self.package_id.system_capacity_kw if self.package_id else self.recommended_kw,
            'system_type': self.package_id.system_type if self.package_id else 'on_grid',
            'roof_type': self.roof_type,
        }
        order = self.env['sale.order'].create(order_vals)

        # Base turnkey solar system sale line
        base_price_per_kw = 720.0 # Standard rooftop turnkey rate $/kW or equivalent base
        turnkey_total = order.system_capacity_kw * base_price_per_kw

        # Check or create solar turnkey service product
        product = self.env['product.product'].search([('default_code', '=', 'SOLAR-TURNKEY')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': f"Turnkey Solar EPC Project ({order.system_capacity_kw} kW)",
                'default_code': 'SOLAR-TURNKEY',
                'type': 'service',
                'list_price': turnkey_total,
            })

        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'name': f"Complete Rooftop Solar EPC Supply & Commissioning ({order.system_capacity_kw} kW {self.package_id.name or ''})",
            'product_uom_qty': 1.0,
            'price_unit': turnkey_total,
        })

        self.sale_order_id = order.id

        return {
            'name': _('Solar Sales Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }
