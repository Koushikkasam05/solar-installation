# -*- coding: utf-8 -*-
"""SolarFlow ERP - Customer Pipeline & CRM Leads Routes."""
from datetime import datetime
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db
from server.helpers import calculate_recommended_capacity, calculate_feasibility_score, calculate_auto_bom, calculate_subsidy, get_next_ref

lead_bp = Blueprint('leads', __name__)

# ROUTES: CUSTOMERS
# ══════════════════════════════════════════════════════════════════════

@lead_bp.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(query_db("SELECT * FROM customers ORDER BY id"))


@lead_bp.route('/api/customers/<int:cid>', methods=['GET'])
def get_customer(cid):
    c = query_db("SELECT * FROM customers WHERE id = ?", [cid], one=True)
    return jsonify(c) if c else (jsonify({'error': 'Not found'}), 404)


@lead_bp.route('/api/customers', methods=['POST'])
def create_customer():
    d = request.get_json()
    cid = execute_db("""INSERT INTO customers (name, phone, email, address, city, state, property_type, sanctioned_load_kw)
        VALUES (?,?,?,?,?,?,?,?)""",
        [d['name'], d.get('phone',''), d.get('email',''), d.get('address',''),
         d.get('city',''), d.get('state',''), d.get('property_type','Residential'), d.get('sanctioned_load_kw', 5.0)])
    return jsonify({'id': cid, 'message': 'Customer created'}), 201


# ══════════════════════════════════════════════════════════════════════
# ROUTES: ENQUIRIES
# ══════════════════════════════════════════════════════════════════════

@lead_bp.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    rows = query_db("""SELECT e.*, c.name as customer_name FROM enquiries e
        JOIN customers c ON e.customer_id = c.id ORDER BY e.id DESC""")
    return jsonify(rows)


@lead_bp.route('/api/enquiries', methods=['POST'])
def create_enquiry():
    d = request.get_json()
    ref = f"ENQ-{datetime.now().year}-{datetime.now().strftime('%m%d')}"
    eid = execute_db("""INSERT INTO enquiries (ref, customer_id, date, property_type, sanctioned_load, status)
        VALUES (?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('date', date.today().isoformat()),
         d.get('property_type',''), d.get('sanctioned_load',''), 'new'])
    return jsonify({'id': eid, 'ref': ref, 'message': 'Enquiry created'}), 201


# ══════════════════════════════════════════════════════════════════════
# ROUTES: LEADS
# ══════════════════════════════════════════════════════════════════════

@lead_bp.route('/api/leads', methods=['GET'])
def get_leads():
    rows = query_db("""SELECT l.*, c.name as customer_name, c.phone as customer_phone
        FROM leads l JOIN customers c ON l.customer_id = c.id ORDER BY l.id DESC""")
    return jsonify(rows)


@lead_bp.route('/api/leads/<int:lid>', methods=['GET'])
def get_lead(lid):
    row = query_db("""SELECT l.*, c.name as customer_name FROM leads l
        JOIN customers c ON l.customer_id = c.id WHERE l.id = ?""", [lid], one=True)
    return jsonify(row) if row else (jsonify({'error': 'Not found'}), 404)


@lead_bp.route('/api/leads', methods=['POST'])
def create_lead():
    d = request.get_json()
    ref = get_next_ref('SF/LEAD', 'leads')
    monthly_kwh = d.get('monthly_kwh', 300)
    roof_area = d.get('roof_area_sqft', 500)
    sanctioned = d.get('sanctioned_load_kw', 5.0)
    rec_kw = calculate_recommended_capacity(monthly_kwh, roof_area, sanctioned)
    feasibility = calculate_feasibility_score(roof_area, monthly_kwh)

    lid = execute_db("""INSERT INTO leads (ref, customer_id, monthly_kwh, tariff_rate, sized_kw,
        system_type, subsidy_required, roof_area_sqft, sanctioned_load_kw,
        recommended_kw, feasibility_score, status, lead_source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], monthly_kwh, d.get('tariff_rate', 0.10),
         d.get('sized_kw', rec_kw), d.get('system_type', 'on_grid'),
         d.get('subsidy_required', 1), roof_area, sanctioned,
         rec_kw, feasibility, 'draft', d.get('lead_source', 'web_inbound')])
    return jsonify({'id': lid, 'ref': ref, 'recommended_kw': rec_kw, 'feasibility_score': feasibility}), 201


@lead_bp.route('/api/leads/<int:lid>', methods=['PUT'])
def update_lead(lid):
    d = request.get_json()
    execute_db("UPDATE leads SET status=?, sized_kw=?, system_type=?, notes=? WHERE id=?",
        [d.get('status', 'draft'), d.get('sized_kw', 3.0), d.get('system_type', 'on_grid'), d.get('notes', ''), lid])
    return jsonify({'message': 'Lead updated'})


@lead_bp.route('/api/leads/<int:lid>/calculate', methods=['GET'])
def calculate_lead(lid):
    """Calculate recommended capacity and feasibility for a lead."""
    lead = query_db("SELECT * FROM leads WHERE id = ?", [lid], one=True)
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    rec_kw = calculate_recommended_capacity(lead['monthly_kwh'], lead['roof_area_sqft'], lead['sanctioned_load_kw'])
    feasibility = calculate_feasibility_score(lead['roof_area_sqft'], lead['monthly_kwh'])
    bom = calculate_auto_bom(rec_kw)
    subsidy = calculate_subsidy(rec_kw) if lead['subsidy_required'] else 0
    return jsonify({
        'recommended_kw': rec_kw,
        'feasibility_score': feasibility,
        'auto_bom': bom,
        'subsidy_amount': subsidy,
    })


# ══════════════════════════════════════════════════════════════════════
# ROUTES: FOLLOW-UPS
# ══════════════════════════════════════════════════════════════════════

@lead_bp.route('/api/followups', methods=['GET'])
def get_followups():
    rows = query_db("""SELECT f.*, c.name as customer_name FROM followups f
        JOIN customers c ON f.customer_id = c.id ORDER BY f.date""")
    return jsonify(rows)


@lead_bp.route('/api/followups', methods=['POST'])
def create_followup():
    d = request.get_json()
    fid = execute_db("""INSERT INTO followups (customer_id, date, sales_rep, type, summary, priority, status)
        VALUES (?,?,?,?,?,?,?)""",
        [d['customer_id'], d.get('date', date.today().isoformat()), d.get('sales_rep',''),
         d.get('type',''), d.get('summary',''), d.get('priority','Normal'), 'Pending'])
    return jsonify({'id': fid, 'message': 'Follow-up created'}), 201


# ══════════════════════════════════════════════════════════════════════

