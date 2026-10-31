# -*- coding: utf-8 -*-
"""SolarFlow ERP - Digital Warranties & After-Sales Service Routes."""
from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db
from server.helpers import generate_warranty_token, get_next_ref
from server.auth import role_required

warranty_bp = Blueprint('warranties', __name__)

# ROUTES: WARRANTIES
# ══════════════════════════════════════════════════════════════════════

@warranty_bp.route('/api/warranties', methods=['GET'])
@role_required('admin', 'support', 'sales', 'director', 'finance')
def get_warranties():
    rows = query_db("""SELECT w.*, c.name as customer_name FROM warranties w
        JOIN customers c ON w.customer_id = c.id ORDER BY w.id DESC""")
    return jsonify(rows)


@warranty_bp.route('/api/warranties', methods=['POST'])
@role_required('admin', 'support')
def create_warranty():
    d = request.get_json() or {}
    ref = get_next_ref('SF/WTY', 'warranties')
    equip_type = d.get('equipment_type', 'pv_module')

    years_map = {'pv_module': 25, 'inverter': 10, 'battery': 5}
    years = years_map.get(equip_type, 5)

    start = d.get('start_date', date.today().isoformat())
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    expiry = (start_dt + timedelta(days=years * 365)).strftime('%Y-%m-%d')

    token = generate_warranty_token(ref, d['customer_id'], d.get('serial_number', ''), equip_type, start)

    existing = query_db("SELECT id FROM warranties WHERE serial_number = ? AND equipment_type = ? AND status = 'active'",
        [d.get('serial_number',''), equip_type], one=True)
    if existing:
        return jsonify({'error': f'Duplicate warranty: An active warranty already exists for serial {d.get("serial_number")}'}), 400

    wid = execute_db("""INSERT INTO warranties (ref, customer_id, installation_id, serial_number,
        equipment_type, warranty_years, start_date, expiry_date, sha256_token, status)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('installation_id'), d.get('serial_number',''),
         equip_type, years, start, expiry, token, 'active'])
    return jsonify({'id': wid, 'ref': ref, 'expiry_date': expiry, 'sha256_token': token, 'warranty_years': years}), 201


@warranty_bp.route('/api/warranties/<int:wid>/verify', methods=['GET'])
@role_required('admin', 'support', 'sales', 'director', 'finance', 'tech')
def verify_warranty(wid):
    """Verify warranty token and check expiry status."""
    w = query_db("SELECT * FROM warranties WHERE id = ?", [wid], one=True)
    if not w:
        return jsonify({'error': 'Warranty not found'}), 404

    expected_token = generate_warranty_token(w['ref'], w['customer_id'], w['serial_number'], w['equipment_type'], w['start_date'])
    token_valid = (w['sha256_token'] == expected_token)

    today = date.today().isoformat()
    is_expired = today > w['expiry_date'] if w['expiry_date'] else False

    return jsonify({
        'warranty': w,
        'token_valid': token_valid,
        'is_expired': is_expired,
        'status': 'expired' if is_expired else w['status'],
    })


# ══════════════════════════════════════════════════════════════════════
# ROUTES: SERVICE TICKETS
# ══════════════════════════════════════════════════════════════════════

@warranty_bp.route('/api/service-tickets', methods=['GET'])
@role_required('admin', 'support', 'tech', 'director', 'finance')
def get_tickets():
    rows = query_db("""SELECT t.*, c.name as customer_name FROM service_tickets t
        JOIN customers c ON t.customer_id = c.id ORDER BY t.id DESC""")
    return jsonify(rows)


@warranty_bp.route('/api/service-tickets', methods=['POST'])
@role_required('admin', 'support', 'sales')
def create_ticket():
    d = request.get_json() or {}
    ref = get_next_ref('SF/SVC', 'service_tickets')

    serial = d.get('serial_number', '')
    warranty = query_db("""SELECT * FROM warranties WHERE serial_number = ? AND status = 'active'
        AND expiry_date >= ?""", [serial, date.today().isoformat()], one=True)
    under_warranty = 1 if warranty else 0

    parts = 0 if under_warranty else d.get('parts_cost', 0)
    labour = 0 if under_warranty else d.get('labour_cost', 0)
    total = parts + labour

    tid = execute_db("""INSERT INTO service_tickets (ref, customer_id, installation_id, warranty_id,
        serial_number, issue_type, description, is_under_warranty,
        parts_cost, labour_cost, total_cost, status, priority, assigned_to)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('installation_id'), warranty['id'] if warranty else None,
         serial, d.get('issue_type', 'general'), d.get('description', ''),
         under_warranty, parts, labour, total, 'open', d.get('priority', 'medium'),
         d.get('assigned_to', '')])
    return jsonify({
        'id': tid, 'ref': ref,
        'under_warranty': bool(under_warranty),
        'total_cost': total,
        'message': '✅ Covered under warranty — $0.00 charge' if under_warranty else f'Out of warranty — total cost: ${total}'
    }), 201


@warranty_bp.route('/api/service-tickets/<int:tid>/resolve', methods=['POST'])
@role_required('admin', 'support', 'tech')
def resolve_ticket(tid):
    d = request.get_json() or {}
    execute_db("""UPDATE service_tickets SET status = 'resolved', resolution = ?,
        resolved_at = ? WHERE id = ?""", [d.get('resolution', ''), datetime.now().isoformat(), tid])
    return jsonify({'message': 'Ticket resolved'})
