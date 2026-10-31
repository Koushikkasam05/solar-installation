# -*- coding: utf-8 -*-
"""SolarFlow ERP - Executive Dashboard & KPI Metrics Routes."""
from flask import Blueprint, jsonify
from server.database import query_db

dashboard_bp = Blueprint('dashboard', __name__)

# ROUTES: DASHBOARD KPIs
# ══════════════════════════════════════════════════════════════════════

@dashboard_bp.route('/api/dashboard', methods=['GET'])
def dashboard():
    """Return real-time dashboard KPIs computed from database."""
    total_leads = query_db("SELECT COUNT(*) as c FROM leads", one=True)['c']
    active_leads = query_db("SELECT COUNT(*) as c FROM leads WHERE status NOT IN ('rejected')", one=True)['c']
    total_surveys = query_db("SELECT COUNT(*) as c FROM surveys", one=True)['c']
    approved_surveys = query_db("SELECT COUNT(*) as c FROM surveys WHERE state = 'approved'", one=True)['c']
    total_orders = query_db("SELECT COUNT(*) as c FROM orders", one=True)['c']
    confirmed_orders = query_db("SELECT COUNT(*) as c FROM orders WHERE status = 'confirmed'", one=True)['c']
    total_installations = query_db("SELECT COUNT(*) as c FROM installations", one=True)['c']
    completed_installations = query_db("SELECT COUNT(*) as c FROM installations WHERE state = 'completed'", one=True)['c']
    total_warranties = query_db("SELECT COUNT(*) as c FROM warranties", one=True)['c']
    active_tickets = query_db("SELECT COUNT(*) as c FROM service_tickets WHERE status != 'resolved'", one=True)['c']
    total_capacity = query_db("SELECT COALESCE(SUM(sized_kw), 0) as c FROM leads", one=True)['c']
    total_revenue = query_db("SELECT COALESCE(SUM(revenue), 0) as c FROM project_costs", one=True)['c']
    avg_margin = query_db("SELECT COALESCE(AVG(gross_margin_percent), 0) as c FROM project_costs", one=True)['c']
    stock_available = query_db("SELECT COUNT(*) as c FROM stock_lots WHERE status = 'available'", one=True)['c']
    stock_allocated = query_db("SELECT COUNT(*) as c FROM stock_lots WHERE status = 'allocated'", one=True)['c']

    return jsonify({
        'total_leads': total_leads,
        'active_leads': active_leads,
        'total_surveys': total_surveys,
        'approved_surveys': approved_surveys,
        'total_orders': total_orders,
        'confirmed_orders': confirmed_orders,
        'total_installations': total_installations,
        'completed_installations': completed_installations,
        'total_warranties': total_warranties,
        'active_tickets': active_tickets,
        'total_pipeline_kw': round(total_capacity, 1),
        'total_revenue': round(total_revenue, 2),
        'avg_gross_margin': round(avg_margin, 2),
        'stock_available': stock_available,
        'stock_allocated': stock_allocated,
    })


# ══════════════════════════════════════════════════════════════════════

