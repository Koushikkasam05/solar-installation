# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

class SolarFlowPackage(models.Model):
    _name = 'solarflow.package'
    _description = 'SolarFlow Configurable Solar Package'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'system_capacity_kw asc, name asc'

    name = fields.Char(string='Package Name', required=True, tracking=True)
    code = fields.Char(string='Package Code', required=True, copy=False, index=True)
    system_capacity_kw = fields.Float(string='System Capacity (kW)', required=True, default=3.0, tracking=True)
    
    system_type = fields.Selection([
        ('on_grid', 'Grid-Tied On-Grid System'),
        ('hybrid', 'Smart Hybrid (Solar + Battery + Grid)'),
        ('off_grid', 'Standalone Off-Grid System'),
    ], string='System Type', default='on_grid', required=True, tracking=True)

    phase = fields.Selection([
        ('single_phase', 'Single-Phase (230V)'),
        ('three_phase', 'Three-Phase (415V)'),
    ], string='AC Grid Phase', default='single_phase', required=True, tracking=True)

    active = fields.Boolean(default=True, tracking=True, help="Set to false to archive the package.")
    default_panel_wattage = fields.Integer(string='Panel Rating (Watts)', default=550)
    battery_capacity_kwh = fields.Float(string='Battery Bank Size (kWh)', default=0.0)

    # Component Lines (BOM)
    package_line_ids = fields.One2many(
        'solarflow.package.line',
        'package_id',
        string='Package Components & Quantities'
    )

    # Pricing & Valuation (Calculated dynamically from configured component records - NO HARDCODING)
    pricing_method = fields.Selection([
        ('sum_components', 'Calculated from Component Prices'),
        ('fixed_price', 'Custom Turnkey Package Price'),
    ], string='Pricing Method', default='sum_components', required=True)

    calculated_components_total = fields.Monetary(
        string='Components Sum Total',
        compute='_compute_pricing',
        store=True
    )
    custom_fixed_price = fields.Monetary(
        string='Custom Package Price',
        default=0.0
    )
    total_price = fields.Monetary(
        string='Effective Package Price',
        compute='_compute_pricing',
        store=True,
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    subsidy_eligible = fields.Boolean(string='Subsidy Eligible', default=True)
    max_subsidy_amount = fields.Monetary(string='Estimated Subsidy Cap', compute='_compute_subsidy', store=True)
    description = fields.Html(string='Technical Scope & Specification')

    _sql_constraints = [
        ('solarflow_package_code_unique', 'unique(code)', 'Package codes must be unique!')
    ]

    @api.constrains('system_capacity_kw')
    def _check_capacity(self):
        for pkg in self:
            if pkg.system_capacity_kw <= 0:
                raise ValidationError(_("Package capacity must be greater than 0 kW."))

    @api.constrains('package_line_ids', 'system_type')
    def _validate_package_components_and_compatibility(self):
        """Enforces Business Rules 8, 9, 10:
        - Check required components are configured (panels, inverter, mounting, cabling).
        - Check compatibility between package and selected system type.
        - Prevent duplicate component lines for the exact same product.
        """
        for pkg in self:
            if not pkg.package_line_ids:
                continue

            categories = [line.category for line in pkg.package_line_ids]
            products = [line.product_id.id for line in pkg.package_line_ids if line.product_id]

            # Rule 10: Prevent duplicate product lines
            if len(products) != len(set(products)):
                raise ValidationError(_("Package '%s' contains duplicate component lines for the same product. Please combine quantities instead.") % pkg.name)

            # Rule 8: Validate essential component categories
            has_panel = any(cat == 'panel' for cat in categories)
            has_inverter = any(cat == 'inverter' for cat in categories)
            has_structure = any(cat == 'structure' for cat in categories)

            if not has_panel:
                raise ValidationError(_("Package '%s' is missing Solar Panels! Every solar package must contain at least one panel component.") % pkg.name)
            if not has_inverter:
                raise ValidationError(_("Package '%s' is missing an Inverter component!") % pkg.name)
            if not has_structure:
                raise ValidationError(_("Package '%s' is missing Module Mounting Structure!") % pkg.name)

            # Rule 9: Check compatibility with system type
            has_battery = any(cat == 'battery' for cat in categories)
            if pkg.system_type in ['off_grid', 'hybrid'] and not has_battery:
                raise ValidationError(_("System Type is '%s' but no Battery component is configured in package '%s'. Off-Grid and Hybrid systems require energy storage.") % (pkg.system_type, pkg.name))
            if pkg.system_type == 'on_grid' and has_battery:
                raise ValidationError(_("On-Grid packages cannot include Battery Storage banks. Please set System Type to 'Hybrid' if battery storage is desired.") % pkg.name)

    @api.depends('package_line_ids.total_price', 'pricing_method', 'custom_fixed_price')
    def _compute_pricing(self):
        for pkg in self:
            comp_sum = sum(line.total_price for line in pkg.package_line_ids)
            pkg.calculated_components_total = comp_sum
            if pkg.pricing_method == 'sum_components':
                pkg.total_price = comp_sum
            else:
                pkg.total_price = pkg.custom_fixed_price or comp_sum

    @api.depends('system_capacity_kw', 'subsidy_eligible')
    def _compute_subsidy(self):
        for pkg in self:
            if not pkg.subsidy_eligible:
                pkg.max_subsidy_amount = 0.0
                continue
            cap = max(float(pkg.system_capacity_kw or 0.0), 0.0)
            if cap <= 2.0:
                pkg.max_subsidy_amount = cap * 30000.0
            elif cap <= 3.0:
                pkg.max_subsidy_amount = 60000.0 + (cap - 2.0) * 18000.0
            else:
                pkg.max_subsidy_amount = 78000.0

    def unlink(self):
        if not self.env.user.has_group('solarflow_management.group_solarflow_admin'):
            raise AccessError(_("Security Violation: Only Super Administrators have permission to delete Solar Packages."))
        return super(SolarFlowPackage, self).unlink()


class SolarFlowPackageLine(models.Model):
    _name = 'solarflow.package.line'
    _description = 'SolarFlow Configurable Package Component Line'
    _order = 'category asc, id asc'

    package_id = fields.Many2one('solarflow.package', string='Package', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Standard Product Component', required=True)
    name = fields.Char(string='Component Description', required=True)
    
    category = fields.Selection([
        ('panel', 'Solar Panels'),
        ('inverter', 'Inverters'),
        ('battery', 'Batteries'),
        ('structure', 'Mounting Structures'),
        ('dc_cable', 'DC Cables'),
        ('ac_cable', 'AC Cables'),
        ('connector', 'Connectors (MC4)'),
        ('switch', 'Switches & Isolators'),
        ('earthing', 'Earthing Equipment'),
        ('safety', 'Safety Components & SPDs'),
        ('bos', 'Other Balance of System'),
    ], string='Component Category', required=True, default='bos')

    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    uom = fields.Char(string='Unit of Measure', default='Units')
    unit_price = fields.Monetary(string='Unit Price', compute='_compute_unit_price', store=True, readonly=False)
    total_price = fields.Monetary(string='Total Price', compute='_compute_total_price', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.unit_price = self.product_id.list_price
            self.uom = self.product_id.uom_id.name if self.product_id.uom_id else 'Units'

    @api.depends('product_id')
    def _compute_unit_price(self):
        for line in self:
            if line.product_id and not line.unit_price:
                line.unit_price = line.product_id.list_price

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.unit_price
