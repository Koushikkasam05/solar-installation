# -*- coding: utf-8 -*-
"""SolarFlow ERP - Project Job Costing & Profit Leakage Audit Routes."""
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db
from server.helpers import calculate_project_cost, get_next_ref
from server.auth import role_required

cost_bp = Blueprint('costing', __name__)

# ROUTES: PROJECT COSTING (FINANCIAL INFORMATION PROTECTION)
# ══════════════════════════════════════════════════════════════════════

@cost_bp.route('/api/costing', methods=['GET'])
@role_required('admin', 'finance', 'director')
def get_costs():
    """Confidential financial costing sheet access restricted to Finance, Executive Directors, and Admins."""
    rows = query_db("""SELECT pc.*, c.name as customer_name FROM project_costs pc
        LEFT JOIN customers c ON pc.customer_id = c.id ORDER BY pc.id DESC""")
    return jsonify(rows)


@cost_bp.route('/api/costing', methods=['POST'])
@role_required('admin', 'finance')
def create_cost():
    """Create project job cost sheet. Directors blocked (read-only); non-finance roles blocked (HTTP 403)."""
    d = request.get_json() or {}
    ref = get_next_ref('SF/COST', 'project_costs')

    revenue = d.get('revenue', 0)
    material = d.get('material_cost', 0)
    labour = d.get('labour_cost', 0)
    transport = d.get('transport_cost', 0)
    additional = d.get('additional_cost', 0)
    other = d.get('other_cost', 0)
    threshold = d.get('leakage_threshold', 10.0)

    calc = calculate_project_cost(revenue, material, labour, transport, additional, other, threshold)

    cid = execute_db("""INSERT INTO project_costs (ref, installation_id, customer_id, order_id,
        revenue, material_cost, labour_cost, transport_cost, additional_cost, other_cost,
        total_cost, gross_profit, gross_margin_percent, margin_health, leakage_alert, leakage_threshold)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d.get('installation_id'), d.get('customer_id'), d.get('order_id'),
         revenue, material, labour, transport, additional, other,
         calc['total_cost'], calc['gross_profit'], calc['gross_margin_percent'],
         calc['margin_health'], calc['leakage_alert'], threshold])
    return jsonify({
        'id': cid, 'ref': ref,
        'revenue': revenue,
        'material_cost': material,
        'labour_cost': labour,
        'transport_cost': transport,
        'additional_cost': additional,
        'other_cost': other,
        **calc,
        'message': '⚠️ PROFIT LEAKAGE ALERT — margin below threshold!' if calc['leakage_alert'] else '✅ Margin healthy'
    }), 201
