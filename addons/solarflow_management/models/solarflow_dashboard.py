# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

class SolarFlowDashboard(models.Model):
    _name = 'solarflow.dashboard'
    _description = 'SolarFlow ERP Executive Operations Dashboard'

    name = fields.Char(string='Dashboard Name', default='SolarFlow EPC Executive Command Center')

    # -------------------------------------------------------------------------
    # 12 REAL DATABASE-DRIVEN KPIS (NO FAKE / HARDCODED NUMBERS)
    # -------------------------------------------------------------------------
    total_projects = fields.Integer(string='Total Projects', compute='_compute_kpis')
    pending_leads = fields.Integer(string='Pending Customer Leads', compute='_compute_kpis')
    pending_surveys = fields.Integer(string='Pending Site Surveys', compute='_compute_kpis')
    pending_quotations = fields.Integer(string='Pending Quotations', compute='_compute_kpis')
    confirmed_orders = fields.Integer(string='Confirmed Sales Orders', compute='_compute_kpis')
    scheduled_installations = fields.Integer(string='Scheduled Installations', compute='_compute_kpis')
    completed_installations = fields.Integer(string='Completed Installations', compute='_compute_kpis')
    low_stock_products = fields.Integer(string='Low Stock Products', compute='_compute_kpis')
    active_warranties = fields.Integer(string='Active Warranties', compute='_compute_kpis')
    open_service_tickets = fields.Integer(string='Open Service Tickets', compute='_compute_kpis')
    monthly_revenue = fields.Monetary(string='Monthly Revenue', compute='_compute_kpis', currency_field='currency_id')
    gross_project_profit = fields.Monetary(string='Gross Project Profit', compute='_compute_kpis', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def _compute_kpis(self):
        for rec in self:
            # 1. Total Projects
            rec.total_projects = self.env['solarflow.installation'].search_count([])

            # 2. Pending Customer Leads
            rec.pending_leads = self.env['crm.lead'].search_count([
                ('type', '=', 'lead'),
                ('stage_id.is_won', '=', False)
            ]) if 'stage_id' in self.env['crm.lead']._fields else self.env['crm.lead'].search_count([])

            # 3. Pending Site Surveys
            rec.pending_surveys = self.env['solarflow.survey'].search_count([
                ('state', 'in', ['draft', 'scheduled', 'in_progress', 'submitted'])
            ])

            # 4. Pending Quotations
            rec.pending_quotations = self.env['sale.order'].search_count([
                ('state', 'in', ['draft', 'sent']),
                ('is_solar_order', '=', True)
            ])

            # 5. Confirmed Sales Orders
            rec.confirmed_orders = self.env['sale.order'].search_count([
                ('state', 'in', ['sale', 'done']),
                ('is_solar_order', '=', True)
            ])

            # 6. Scheduled Installations
            rec.scheduled_installations = self.env['solarflow.installation'].search_count([
                ('state', '=', 'scheduled')
            ])

            # 7. Completed Installations
            rec.completed_installations = self.env['solarflow.installation'].search_count([
                ('state', '=', 'completed')
            ])

            # 8. Low Stock Products (On-hand <= 5)
            products = self.env['product.product'].search([
                ('detailed_type', '=', 'product')
            ])
            rec.low_stock_products = len(products.filtered(lambda p: p.qty_available <= 5.0))

            # 9. Active Warranties
            rec.active_warranties = self.env['solarflow.warranty'].search_count([
                ('status', '=', 'active')
            ])

            # 10. Open Service Tickets
            rec.open_service_tickets = self.env['solarflow.service.ticket'].search_count([
                ('state', 'in', ['new', 'assigned', 'in_progress', 'waiting_parts'])
            ])

            # 11. Monthly Revenue
            today = date.today()
            first_day = today.replace(day=1)
            orders = self.env['sale.order'].search([
                ('state', 'in', ['sale', 'done']),
                ('is_solar_order', '=', True),
                ('date_order', '>=', first_day)
            ])
            rec.monthly_revenue = sum(orders.mapped('amount_total'))

            # 12. Gross Project Profit (from actual costing sheets)
            costs = self.env['solarflow.project.cost'].search([])
            rec.gross_project_profit = sum(costs.mapped('gross_profit'))

    # -------------------------------------------------------------------------
    # STAT-BUTTON NAVIGATION ACTIONS
    # -------------------------------------------------------------------------
    def action_view_total_projects(self):
        return self.env['solarflow.installation']._get_records_action(
            name=_("All Solar Projects"),
            domain=[]
        )

    def action_view_pending_leads(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pending Customer Inquiries'),
            'res_model': 'crm.lead',
            'view_mode': 'kanban,tree,form',
            'domain': [('type', '=', 'lead')],
        }

    def action_view_pending_surveys(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pending Site Surveys'),
            'res_model': 'solarflow.survey',
            'view_mode': 'kanban,tree,form',
            'domain': [('state', 'in', ['draft', 'scheduled', 'in_progress', 'submitted'])],
        }

    def action_view_pending_quotations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pending Solar Quotations'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('state', 'in', ['draft', 'sent']), ('is_solar_order', '=', True)],
        }

    def action_view_confirmed_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirmed Solar Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('state', 'in', ['sale', 'done']), ('is_solar_order', '=', True)],
        }

    def action_view_scheduled_installations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scheduled Installations'),
            'res_model': 'solarflow.installation',
            'view_mode': 'kanban,tree,form',
            'domain': [('state', '=', 'scheduled')],
        }

    def action_view_completed_installations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Completed Commissioned Projects'),
            'res_model': 'solarflow.installation',
            'view_mode': 'kanban,tree,form',
            'domain': [('state', '=', 'completed')],
        }

    def action_view_low_stock_products(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inventory Products'),
            'res_model': 'product.product',
            'view_mode': 'tree,form',
            'domain': [('detailed_type', '=', 'product')],
        }

    def action_view_active_warranties(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Active Solar Warranties'),
            'res_model': 'solarflow.warranty',
            'view_mode': 'tree,form',
            'domain': [('status', '=', 'active')],
        }

    def action_view_open_service_tickets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Open After-Sales Tickets'),
            'res_model': 'solarflow.service.ticket',
            'view_mode': 'kanban,tree,form',
            'domain': [('state', 'in', ['new', 'assigned', 'in_progress', 'waiting_parts'])],
        }

    def action_view_revenue(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Solar Revenue Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('state', 'in', ['sale', 'done']), ('is_solar_order', '=', True)],
        }

    def action_view_gross_profit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project Costing & Profitability Sheets'),
            'res_model': 'solarflow.project.cost',
            'view_mode': 'tree,form',
        }

    @api.model
    def action_open_dashboard(self):
        """Opens or creates the singleton executive dashboard record."""
        dash = self.search([], limit=1)
        if not dash:
            dash = self.create({'name': 'SolarFlow EPC Executive Command Center'})
        return {
            'name': _('SolarFlow Executive Dashboard'),
            'type': 'ir.actions.act_window',
            'res_model': 'solarflow.dashboard',
            'res_id': dash.id,
            'view_mode': 'form',
            'target': 'current',
        }
