# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
import math

class SolarFlowSurvey(models.Model):
    _name = 'solarflow.survey'
    _description = 'SolarFlow Rooftop Site Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Survey Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        index=True
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Related Lead',
        required=True,
        tracking=True,
        ondelete='restrict',
        index=True
    )

    survey_date = fields.Date(
        string='Survey Date',
        default=fields.Date.today,
        tracking=True,
        required=True
    )
    surveyor_id = fields.Many2one(
        'res.users',
        string='Survey Technician',
        default=lambda self: self.env.user,
        tracking=True
    )
    engineer_id = fields.Many2one(
        'res.users',
        string='Approving Engineer',
        readonly=True,
        tracking=True
    )

    # Roof & Environmental Specifications
    roof_area_sqft = fields.Float(
        string='Total Roof Area (sq. ft.)',
        default=0.0,
        tracking=True
    )
    usable_area_sqft = fields.Float(
        string='Shadow-Free Usable Area (sq. ft.)',
        default=0.0,
        tracking=True
    )
    roof_direction = fields.Selection([
        ('south', 'True South (180°) - Optimal'),
        ('south_east', 'South-East (135°)'),
        ('south_west', 'South-West (225°)'),
        ('east', 'East (90°)'),
        ('west', 'West (270°)'),
        ('north', 'North (360° / 0°) - Low Yield'),
    ], string='Roof Direction', default='south', required=True, tracking=True)

    roof_tilt_deg = fields.Float(
        string='Roof Tilt (Degrees)',
        default=12.0,
        help="Optimal pitch is typically between 10° and 25°."
    )
    cable_distance_meters = fields.Float(
        string='Cable Distance to Main DB (Meters)',
        default=0.0,
        tracking=True
    )
    grid_availability = fields.Selection([
        ('single_phase', 'Single-Phase 230V Stable Grid'),
        ('three_phase', 'Three-Phase 415V Stable Grid'),
        ('irregular_grid', 'Frequent Power Cuts / Fluctuating Grid'),
        ('off_grid', 'No Grid Available / Remote Off-Grid'),
    ], string='Grid Availability', default='single_phase', required=True, tracking=True)

    roof_condition = fields.Selection([
        ('excellent', 'Excellent (Reinforced Concrete / Heavy Load Bearing)'),
        ('good', 'Good (Sound Structural Condition for Standard Solar Rails)'),
        ('repair_needed', 'Repair Needed (Minor Waterproofing or Crack Repair)'),
        ('unsafe', 'Unsafe (Weak Asbestos / Structural Damage / Infeasible)'),
    ], string='Roof Condition', default='good', required=True, tracking=True)

    # Photographs & Evidence
    photo_ids = fields.Many2many(
        'ir.attachment',
        'solarflow_survey_photo_rel',
        'survey_id',
        'attachment_id',
        string='Site Photographs'
    )
    photo_roof = fields.Binary(string='Primary Roof Panoramic Photo', attachment=True)
    photo_meter = fields.Binary(string='Existing Meter & DB Photo', attachment=True)
    photo_shadow = fields.Binary(string='Obstacle & Shadow Analysis Photo', attachment=True)

    survey_notes = fields.Text(string='Survey Notes & Site Observations')

    # Status Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Approval Status', default='draft', tracking=True, required=True, index=True)

    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True,
        help="Mandatory rationale if survey is rejected."
    )

    # Solar Recommendations & BOM
    recommended_capacity_kw = fields.Float(
        string='Surveyed Max Capacity (kW)',
        compute='_compute_surveyed_capacity',
        store=True,
        readonly=False
    )
    system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid System'),
        ('hybrid', 'Smart Hybrid (Solar + Battery + Grid)'),
        ('off_grid', 'Standalone Off-Grid System'),
    ], string='Recommended System Type', default='on_grid', required=True)

    package_id = fields.Many2one('solarflow.package', string='Proposed Solar Package')
    bom_line_ids = fields.One2many('solarflow.bom.line', 'survey_id', string='Bill of Materials Items')
    bom_total_cost = fields.Monetary(string='Estimated BOM Cost', compute='_compute_bom_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    sale_order_ids = fields.One2many('sale.order', 'survey_id', string='Linked Quotations')
    quotation_count = fields.Integer(string='Quotations Count', compute='_compute_quotation_count')

    _sql_constraints = [
        ('solarflow_survey_name_unique', 'unique(name)', 'Survey Reference numbers must be unique!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solarflow.survey.seq') or _('SURV-NEW')
        return super(SolarFlowSurvey, self).create(vals_list)

    @api.constrains('usable_area_sqft', 'roof_area_sqft')
    def _check_roof_areas(self):
        for rec in self:
            if rec.roof_area_sqft < 0 or rec.usable_area_sqft < 0:
                raise ValidationError(_("Roof area and Shadow-free usable area cannot be negative."))
            if rec.usable_area_sqft > rec.roof_area_sqft:
                raise ValidationError(_("Shadow-free usable area (%s sq.ft.) cannot exceed total roof area (%s sq.ft.).")
                                      % (rec.usable_area_sqft, rec.roof_area_sqft))

    @api.depends('usable_area_sqft')
    def _compute_surveyed_capacity(self):
        for survey in self:
            # Rule of thumb: ~80-85 sq.ft. per kW
            if survey.usable_area_sqft > 0:
                survey.recommended_capacity_kw = round(survey.usable_area_sqft / 80.0, 1)
            else:
                survey.recommended_capacity_kw = 3.0

    @api.depends('bom_line_ids.total_cost')
    def _compute_bom_cost(self):
        for survey in self:
            survey.bom_total_cost = sum(line.total_cost for line in survey.bom_line_ids)

    def _compute_quotation_count(self):
        for survey in self:
            survey.quotation_count = len(survey.sale_order_ids)

    # -------------------------------------------------------------------------
    # WORKFLOW TRANSITIONS & SERVER-SIDE VALIDATION RULES
    # -------------------------------------------------------------------------

    def action_schedule(self):
        for rec in self:
            if not rec.surveyor_id:
                raise ValidationError(_("Please assign a Survey Technician before scheduling the survey."))
            rec.write({'state': 'scheduled'})
            if rec.lead_id:
                rec.lead_id.survey_status = 'scheduled'

    def action_start(self):
        for rec in self:
            if rec.state not in ['scheduled', 'draft']:
                raise UserError(_("Survey can only be started from Draft or Scheduled state."))
            rec.write({'state': 'in_progress'})

    def action_submit(self):
        for rec in self:
            # Validation Rule 1: Cannot submit without core technical survey information
            if rec.roof_area_sqft <= 0:
                raise ValidationError(_("Please provide a valid Roof Area (> 0 sq.ft.) before submitting."))
            if rec.usable_area_sqft <= 0:
                raise ValidationError(_("Please provide a valid Shadow-Free Area (> 0 sq.ft.) before submitting."))
            if rec.cable_distance_meters <= 0:
                raise ValidationError(_("Please specify the Cable Distance to the main distribution panel (> 0m)."))
            if not rec.roof_condition:
                raise ValidationError(_("Roof condition must be assessed before submitting."))

            rec.write({'state': 'submitted'})
            if rec.lead_id:
                rec.lead_id.survey_status = 'completed'

    def action_approve(self):
        # Security Enforcement: Only Sales Manager or Super Administrator can approve surveys
        is_authorized = (
            self.env.user.has_group('solarflow_management.group_solarflow_sales_manager') or
            self.env.user.has_group('solarflow_management.group_solarflow_admin') or
            self.env.user.has_group('solarflow_management.group_solarflow_engineer') or
            self.env.user.has_group('solarflow_management.group_solarflow_manager')
        )
        if not is_authorized:
            raise AccessError(_("Security Violation: Only a Sales Manager or Super Administrator is authorized to approve site surveys."))

        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Only submitted surveys can be reviewed and approved."))
            if rec.roof_condition == 'unsafe':
                raise ValidationError(_("Cannot approve a site survey where the roof condition is marked 'Unsafe'."))

            rec.write({
                'state': 'approved',
                'engineer_id': self.env.user.id,
            })
            if rec.lead_id:
                rec.lead_id.survey_status = 'approved'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Survey Approved'),
                'message': _('Survey %s has been officially approved. Quotations may now be created.') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reject(self, reason=None):
        # Security Enforcement: Only Sales Manager or Super Administrator can reject surveys
        is_authorized = (
            self.env.user.has_group('solarflow_management.group_solarflow_sales_manager') or
            self.env.user.has_group('solarflow_management.group_solarflow_admin') or
            self.env.user.has_group('solarflow_management.group_solarflow_engineer') or
            self.env.user.has_group('solarflow_management.group_solarflow_manager')
        )
        if not is_authorized:
            raise AccessError(_("Security Violation: Only a Sales Manager or Super Administrator is authorized to reject site surveys."))

        for rec in self:
            rejection_text = reason or rec.rejection_reason
            # Validation Rule 2: A rejected survey must contain a rejection reason
            if not rejection_text or not rejection_text.strip():
                raise ValidationError(_("A detailed Rejection Reason is required to reject a site survey."))

            rec.write({
                'state': 'rejected',
                'rejection_reason': rejection_text.strip(),
                'engineer_id': self.env.user.id,
            })
            if rec.lead_id:
                rec.lead_id.survey_status = 'rejected'

    def action_generate_automatic_bom(self):
        """Generates dynamic BOM components based on configured solar packages."""
        self.ensure_one()
        pkg = self.package_id
        if not pkg:
            raise UserError(_("Please select a configured Solar Package first to generate the automatic BOM."))

        self.bom_line_ids.unlink()

        # Generate BOM directly from the package's configured components
        bom_lines = []
        for line in pkg.package_line_ids:
            bom_lines.append({
                'survey_id': self.id,
                'product_id': line.product_id.id if line.product_id else False,
                'name': line.name,
                'category': line.category,
                'quantity': line.quantity,
                'uom': line.uom,
                'unit_cost': line.unit_cost,
            })

        # Also add site-specific DC cable based on surveyed cable distance
        if self.cable_distance_meters > 0:
            dc_cable_qty = round(self.cable_distance_meters * 2.2 + 10.0, 1)
            bom_lines.append({
                'survey_id': self.id,
                'name': f"UV-Resistant Solar DC Cable 4 sq. mm ({dc_cable_qty}m for {self.cable_distance_meters}m run)",
                'category': 'cable',
                'quantity': dc_cable_qty,
                'uom': 'Meters',
                'unit_cost': 1.65,
            })

        for item in bom_lines:
            self.env['solarflow.bom.line'].create(item)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Automatic BOM Generated'),
                'message': _('%d components populated from package %s.') % (len(bom_lines), pkg.name),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_create_sales_quotation(self):
        """Validation Rule 4: Quotation must not proceed using an unapproved survey."""
        self.ensure_one()
        if not (self.env.user.has_group('solarflow_management.group_solarflow_sales_manager') or
                self.env.user.has_group('solarflow_management.group_solarflow_admin')):
            raise AccessError(_("Security Violation: Only Sales Managers and Super Administrators can generate sales quotations from site surveys."))

        if self.state != 'approved':
            raise UserError(_("A quotation must not proceed using an unapproved survey! Please approve survey %s first.") % self.name)

        # Call the sales order creation helper
        return self.env['sale.order'].action_create_from_survey(self)

    def unlink(self):
        if not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
            raise AccessError(_("Security Violation: Only Super Administrators have permission to delete Site Survey records."))
        return super(SolarFlowSurvey, self).unlink()


class SolarFlowBomLine(models.Model):
    _name = 'solarflow.bom.line'
    _description = 'SolarFlow Bill of Materials Line'
    _order = 'category asc, id asc'

    survey_id = fields.Many2one('solarflow.survey', string='Site Survey', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Inventory Product')
    name = fields.Char(string='Component Description', required=True)
    category = fields.Selection([
        ('panel', 'PV Solar Modules'),
        ('inverter', 'Solar Inverter / PCU'),
        ('battery', 'Battery Storage Bank'),
        ('structure', 'Module Mounting Rails & Hardware'),
        ('cable', 'Solar DC & AC Armored Cables'),
        ('connector', 'MC4 Connectors & Accessories'),
        ('switch', 'DC Isolators & AC Breakers'),
        ('earthing', 'Chemical Earthing & Lightning Protection'),
        ('safety', 'Surge Protective Devices (SPDs) & Fuses'),
        ('bos', 'Balance of System Components'),
    ], string='Component Category', default='bos', required=True)

    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    uom = fields.Char(string='Unit of Measure', default='Units')
    unit_cost = fields.Monetary(string='Unit Price', default=0.0, required=True)
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.unit_cost
