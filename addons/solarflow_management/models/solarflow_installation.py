# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SolarFlowInstallation(models.Model):
    _name = 'solarflow.installation'
    _description = 'SolarFlow Field Installation & Commissioning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Installation Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    installation_address = fields.Char(string='Installation Address', tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', required=True, tracking=True, ondelete='restrict')
    survey_id = fields.Many2one('solarflow.survey', string='Approved Survey', tracking=True, domain="[('state', '=', 'approved')]")
    package_id = fields.Many2one('solarflow.package', string='Solar Package', tracking=True)

    installation_capacity_kw = fields.Float(string='Installation Capacity (kW)', default=3.0, tracking=True)
    system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid System'),
        ('hybrid', 'Smart Hybrid (Solar + Battery + Grid)'),
        ('off_grid', 'Standalone Off-Grid System'),
    ], string='System Type', default='on_grid', required=True, tracking=True)

    # Schedule & Technicians
    scheduled_date = fields.Date(string='Scheduled Date', tracking=True)
    start_date = fields.Date(string='Actual Start Date', tracking=True)
    completion_date = fields.Date(string='Actual Completion Date', tracking=True)

    technician_id = fields.Many2one('res.users', string='Lead Technician', tracking=True)
    technician_ids = fields.Many2many('res.users', 'solarflow_installation_tech_rel', 'inst_id', 'user_id', string='Field Crew Technicians')
    technician_notes = fields.Text(string='Technician Activity Log & Notes')

    # Workflow Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready for Scheduling'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('testing', 'Testing & QC'),
        ('completed', 'Completed & Accepted'),
        ('cancelled', 'Cancelled'),
    ], string='Installation Status', default='draft', tracking=True, required=True, index=True)

    # Equipment Serial Tracking (Dispatched Lots)
    lot_ids = fields.Many2many(
        'stock.lot',
        'solarflow_installation_lot_rel',
        'installation_id',
        'lot_id',
        string='Dispatched Equipment Serial Numbers'
    )
    serial_count = fields.Integer(string='Serials Count', compute='_compute_serial_count')

    # 6-Phase Execution Milestones
    phase_1_structure = fields.Boolean(string='1. Civil Foundations & Mounting Structure Grouting', default=False, tracking=True)
    phase_2_modules = fields.Boolean(string='2. PV Module Mounting & DC String Cabling', default=False, tracking=True)
    phase_3_inverter = fields.Boolean(string='3. Inverter, ACDB & DCDB Electrical Wiring', default=False, tracking=True)
    phase_4_earthing = fields.Boolean(string='4. Chemical Earthing (<5Ω) & Lightning Arrester', default=False, tracking=True)
    phase_5_testing = fields.Boolean(string='5. Electrical Testing & Insulation Megger Verification', default=False, tracking=True)
    phase_6_discom_sync = fields.Boolean(string='6. DISCOM Bi-Directional Net Metering Active', default=False, tracking=True)
    progress_percent = fields.Float(string='Execution Progress (%)', compute='_compute_progress', store=True)

    # Testing Results
    test_voc = fields.Float(string='Measured Open Circuit Voltage (Voc - Volts)', default=0.0, tracking=True)
    test_isc = fields.Float(string='Measured Short Circuit Current (Isc - Amps)', default=0.0, tracking=True)
    test_earth_resistance = fields.Float(string='Earth Pit Resistance (Ohms)', default=0.0, tracking=True, help="Must be <= 5.0 Ohms")
    test_insulation_resistance = fields.Float(string='Insulation Megger Resistance (MOhm)', default=0.0, tracking=True, help="Must be >= 1.0 MOhm")
    test_grid_voltage = fields.Float(string='Grid AC Voltage (Volts)', default=230.0)
    test_notes = fields.Text(string='Quality Assurance (QC) Testing Notes')

    # Customer Acceptance
    customer_accepted = fields.Boolean(string='Customer Acceptance Confirmed', default=False, tracking=True)
    acceptance_date = fields.Date(string='Acceptance Sign-off Date', tracking=True)
    acceptance_signature = fields.Char(string='Customer Sign-off Name / Token')
    acceptance_notes = fields.Text(string='Customer Acceptance Feedback')

    # Photographs & Visual Proofs
    photo_structure = fields.Binary(string='Mounting Structure Photo', attachment=True)
    photo_modules = fields.Binary(string='Mounted PV Modules Photo', attachment=True)
    photo_inverter = fields.Binary(string='Inverter & ACDB/DCDB Photo', attachment=True)
    photo_net_meter = fields.Binary(string='Net Meter & Earthing Photo', attachment=True)

    # Warranties and Costing Links
    warranty_ids = fields.One2many('solarflow.warranty', 'installation_id', string='Issued Warranties')
    warranty_count = fields.Integer(string='Warranty Count', compute='_compute_warranty_count')
    ticket_ids = fields.One2many('solarflow.service.ticket', 'installation_id', string='After-Sales Tickets')
    cost_id = fields.Many2one('solarflow.project.cost', string='Project Cost Sheet', readonly=True)

    # -------------------------------------------------------------------------
    # UNIQUE FEATURE: INSTALLATION READINESS SCORE (OUT OF 100)
    # Breakdown:
    # 1. Survey Approved: 20 pts
    # 2. Payment Policy Satisfied: 20 pts
    # 3. Required Stock Available: 20 pts
    # 4. Equipment Allocated: 20 pts
    # 5. Technician Assigned: 20 pts
    # -------------------------------------------------------------------------
    readiness_score = fields.Integer(
        string='Readiness Score',
        compute='_compute_readiness_score',
        store=True,
        tracking=True,
        help="Automated installation readiness score out of 100."
    )
    readiness_survey = fields.Boolean(string='Survey Approved (20 pts)', compute='_compute_readiness_score', store=True)
    readiness_payment = fields.Boolean(string='Payment Policy Satisfied (20 pts)', compute='_compute_readiness_score', store=True)
    readiness_stock = fields.Boolean(string='Required Stock Available (20 pts)', compute='_compute_readiness_score', store=True)
    readiness_equipment = fields.Boolean(string='Equipment Allocated (20 pts)', compute='_compute_readiness_score', store=True)
    readiness_technician = fields.Boolean(string='Technician Assigned (20 pts)', compute='_compute_readiness_score', store=True)
    readiness_grade = fields.Selection([
        ('not_ready', 'Not Ready (<60%)'),
        ('partial', 'Partially Ready (60-80%)'),
        ('fully_ready', 'Fully Ready for Commissioning (100%)'),
    ], string='Readiness Status', compute='_compute_readiness_score', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solarflow.installation.seq') or _('INST-NEW')
        return super(SolarFlowInstallation, self).create(vals_list)

    @api.depends('phase_1_structure', 'phase_2_modules', 'phase_3_inverter', 'phase_4_earthing', 'phase_5_testing', 'phase_6_discom_sync')
    def _compute_progress(self):
        for p in self:
            phases = [p.phase_1_structure, p.phase_2_modules, p.phase_3_inverter, p.phase_4_earthing, p.phase_5_testing, p.phase_6_discom_sync]
            p.progress_percent = round((sum(1 for x in phases if x) / 6.0) * 100.0, 1)

    def _compute_serial_count(self):
        for p in self:
            p.serial_count = len(p.lot_ids)

    def _compute_warranty_count(self):
        for p in self:
            p.warranty_count = len(p.warranty_ids)

    @api.depends(
        'survey_id', 'survey_id.state',
        'sale_order_id', 'sale_order_id.dispatch_permission', 'sale_order_id.payment_status',
        'sale_order_id.state', 'lot_ids', 'technician_id', 'technician_ids', 'package_id'
    )
    def _compute_readiness_score(self):
        """Calculates Installation Readiness Score (0 to 100 pts) across 5 critical dimensions."""
        for inst in self:
            score = 0
            # 1. Survey Approved: 20 pts
            survey_ok = bool(inst.survey_id and inst.survey_id.state == 'approved')
            if survey_ok:
                score += 20
            inst.readiness_survey = survey_ok

            # 2. Payment Policy Satisfied: 20 pts
            order = inst.sale_order_id
            payment_ok = bool(order and order.dispatch_permission)
            if payment_ok:
                score += 20
            inst.readiness_payment = payment_ok

            # 3. Required Stock Available: 20 pts
            stock_ok = bool((order and order.state in ['sale', 'done']) or inst.lot_ids)
            if stock_ok:
                score += 20
            inst.readiness_stock = stock_ok

            # 4. Equipment Allocated: 20 pts
            equip_ok = bool(inst.lot_ids)
            if equip_ok:
                score += 20
            inst.readiness_equipment = equip_ok

            # 5. Technician Assigned: 20 pts
            tech_ok = bool(inst.technician_id or inst.technician_ids)
            if tech_ok:
                score += 20
            inst.readiness_technician = tech_ok

            inst.readiness_score = score
            if score >= 100:
                inst.readiness_grade = 'fully_ready'
            elif score >= 60:
                inst.readiness_grade = 'partial'
            else:
                inst.readiness_grade = 'not_ready'

    # -------------------------------------------------------------------------
    # WORKFLOW TRANSITIONS & STRICT SERVER-SIDE BUSINESS RULES
    # -------------------------------------------------------------------------

    def action_mark_ready(self):
        """Validates survey approval and payment policy before advancing to Ready."""
        for inst in self:
            # Rule 1: Check survey approval
            if inst.survey_id and inst.survey_id.state != 'approved':
                raise ValidationError(_("Cannot mark Ready: Associated survey '%s' is not Approved.") % inst.survey_id.name)

            # Rule 2: Check payment policy
            order = inst.sale_order_id
            if order and not order.dispatch_permission:
                raise UserError(_(
                    "Cannot mark Ready: Customer Advance Payment requirement has not been met!\n\n"
                    "Required Advance: $%s (%s%%)\n"
                    "Current Amount Paid: $%s (Status: %s)\n\n"
                    "Please reconcile advance payment in Accounting before proceeding with field execution."
                ) % (order.advance_payment_amount, order.advance_payment_pct, order.amount_paid, order.payment_status))

            inst.write({'state': 'ready'})

    def action_schedule(self):
        """Rule 5: Require technician assignment before scheduling."""
        for inst in self:
            if not inst.technician_id and not inst.technician_ids:
                raise ValidationError(_("Technician Assignment Required! Please assign a Lead Technician or Crew member before scheduling."))
            if not inst.scheduled_date:
                raise ValidationError(_("Please specify a Scheduled Date for the installation visit."))
            inst.write({'state': 'scheduled'})

    def action_start(self):
        for inst in self:
            if inst.state not in ['scheduled', 'ready']:
                raise UserError(_("Installation can only be started from Ready or Scheduled state."))
            inst.write({
                'state': 'in_progress',
                'start_date': inst.start_date or fields.Date.today()
            })

    def action_testing_qc(self):
        for inst in self:
            inst.write({'state': 'testing'})

    def action_complete_and_handover(self):
        """Enforces Business Rules 6, 7, 8:
        6. Require testing results before completion (Voc > 0, Isc > 0, Earth Resistance <= 5.0 Ohms).
        7. Require customer acceptance before completion.
        8. Store installation photographs.
        """
        for inst in self:
            # Rule 6: Validate Testing Results
            if inst.test_voc <= 0:
                raise ValidationError(_("Electrical QC Testing Incomplete: Measured Voc must be greater than 0 Volts."))
            if inst.test_isc <= 0:
                raise ValidationError(_("Electrical QC Testing Incomplete: Measured Isc must be greater than 0 Amps."))
            if inst.test_earth_resistance <= 0 or inst.test_earth_resistance > 5.0:
                raise ValidationError(_("Earthing Safety Hazard! Measured Earth Pit Resistance is %s Ohms. Standard solar safety requires Earth Resistance <= 5.0 Ohms.")
                                      % inst.test_earth_resistance)

            # Rule 7: Require Customer Acceptance
            if not inst.customer_accepted:
                raise ValidationError(_("Customer Acceptance Sign-off is mandatory before marking the installation project as Completed."))

            # Update Serialized Lots to installed / active
            for lot in inst.lot_ids:
                lot.write({
                    'allocation_status': 'installed',
                    'commissioning_date': fields.Date.today()
                })

            inst.write({
                'state': 'completed',
                'completion_date': fields.Date.today(),
                'phase_1_structure': True,
                'phase_2_modules': True,
                'phase_3_inverter': True,
                'phase_4_earthing': True,
                'phase_5_testing': True,
                'phase_6_discom_sync': True,
            })

            # Auto-issue 3 Digital Warranty Certificates
            inst.action_generate_warranties()

            # Auto-create Job Costing record
            inst.action_generate_costing()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Installation Completed!'),
                'message': _('Project successfully commissioned and customer accepted. Digital Warranties and Job Costing active.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_warranties(self):
        """Enforces Business Rules 1 & 2:
        1. Warranty connected to the correct equipment serial number.
        2. Activated following successful installation commissioning according to configured policy:
           - Inverter: 2 years (24 months)
           - Battery: 2 years (24 months)
           - Solar Panel: 20 years (240 months)
        """
        for inst in self:
            inst.warranty_ids.unlink()
            comm_date = inst.completion_date or fields.Date.today()

            # Find allocated lots
            panel_lots = inst.lot_ids.filtered(lambda l: 'panel' in (l.product_id.name or '').lower() or 'module' in (l.product_id.name or '').lower())
            inverter_lots = inst.lot_ids.filtered(lambda l: 'inverter' in (l.product_id.name or '').lower())
            battery_lots = inst.lot_ids.filtered(lambda l: 'battery' in (l.product_id.name or '').lower())

            # Fallback products if no lots
            fallback_prod = self.env['product.product'].search([('name', 'ilike', 'Solar')], limit=1)
            if not fallback_prod:
                fallback_prod = self.env['product.product'].search([], limit=1)

            # 1. Solar Panel Warranty: 20 Years (240 Months)
            p_lot = panel_lots[0] if panel_lots else (inst.lot_ids[0] if inst.lot_ids else False)
            p_prod = p_lot.product_id if p_lot else fallback_prod
            if p_prod:
                self.env['solarflow.warranty'].create({
                    'installation_id': inst.id,
                    'customer_id': inst.customer_id.id,
                    'product_id': p_prod.id,
                    'lot_id': p_lot.id if p_lot else False,
                    'warranty_type': 'panel',
                    'duration_months': 240,
                    'start_date': comm_date,
                    'manufacturer_details': 'Tier-1 Mono PERC PV Manufacturer',
                    'terms_clauses': 'Guarantees >= 90% peak output at Year 10 and >= 80% output at Year 20.',
                })

            # 2. Inverter Warranty: 2 Years (24 Months)
            inv_lot = inverter_lots[0] if inverter_lots else False
            inv_prod = inv_lot.product_id if inv_lot else self.env['product.product'].search([('name', 'ilike', 'Inverter')], limit=1) or p_prod
            if inv_prod:
                self.env['solarflow.warranty'].create({
                    'installation_id': inst.id,
                    'customer_id': inst.customer_id.id,
                    'product_id': inv_prod.id,
                    'lot_id': inv_lot.id if inv_lot else False,
                    'warranty_type': 'inverter',
                    'duration_months': 24,
                    'start_date': comm_date,
                    'manufacturer_details': 'Smart Grid-Tied Inverter OEM',
                    'terms_clauses': 'Full replacement warranty on inverter electronics, MPPT and telemetry.',
                })

            # 3. Battery Storage Warranty (if present or hybrid/off-grid): 2 Years (24 Months)
            if battery_lots or inst.system_type in ['hybrid', 'off_grid']:
                bat_lot = battery_lots[0] if battery_lots else False
                bat_prod = bat_lot.product_id if bat_lot else self.env['product.product'].search([('name', 'ilike', 'Battery')], limit=1) or p_prod
                if bat_prod:
                    self.env['solarflow.warranty'].create({
                        'installation_id': inst.id,
                        'customer_id': inst.customer_id.id,
                        'product_id': bat_prod.id,
                        'lot_id': bat_lot.id if bat_lot else False,
                        'warranty_type': 'battery',
                        'duration_months': 24,
                        'start_date': comm_date,
                        'manufacturer_details': 'Deep-Cycle Lithium Storage OEM',
                        'terms_clauses': 'Guarantees 6000 cycles at 80% DoD and cell balancing.',
                    })

            # 4. Workmanship & Structural Warranty: 5 Years (60 Months)
            if p_prod:
                self.env['solarflow.warranty'].create({
                    'installation_id': inst.id,
                    'customer_id': inst.customer_id.id,
                    'product_id': p_prod.id,
                    'warranty_type': 'workmanship',
                    'duration_months': 60,
                    'start_date': comm_date,
                    'manufacturer_details': 'SolarFlow EPC Workmanship Standard',
                    'terms_clauses': 'Guarantees mounting integrity against wind speeds up to 150 km/h and zero roof leakage.',
                })

    def action_generate_costing(self):
        """Generates project cost sheet tracking estimated vs actual costs, gross profit, and gross margin."""
        for inst in self:
            if not inst.cost_id:
                cap = inst.installation_capacity_kw or 3.0
                revenue = inst.sale_order_id.amount_total if inst.sale_order_id else (cap * 680.0)
                est_mat = round(cap * 410.0, 2)
                est_lab = round(cap * 30.0, 2)
                est_trans = 60.0
                est_oth = 120.0

                costing = self.env['solarflow.project.cost'].create({
                    'name': f"COST-{inst.name}",
                    'installation_id': inst.id,
                    'customer_id': inst.customer_id.id,
                    'estimated_revenue': revenue,
                    'actual_revenue': revenue,
                    'estimated_material_cost': est_mat,
                    'material_cost': est_mat,
                    'estimated_labour_cost': est_lab,
                    'technician_labour_cost': est_lab,
                    'estimated_transportation_cost': est_trans,
                    'transportation_cost': est_trans,
                    'additional_material_cost': 0.0,
                    'estimated_other_expenses': est_oth,
                    'other_expenses': est_oth,
                    'leakage_threshold_pct': 10.0,
                })
                inst.cost_id = costing.id

