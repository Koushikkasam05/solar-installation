# -*- coding: utf-8 -*-
"""SolarFlow ERP - Field Installations & 6-Phase QC Testing Routes."""
from datetime import datetime, date
from flask import Blueprint, jsonify, request, session
from server.database import query_db, execute_db
from server.helpers import calculate_readiness_score, get_next_ref
from server.auth import role_required, get_current_user_role

install_bp = Blueprint('installations', __name__)

# ROUTES: INSTALLATIONS
# ══════════════════════════════════════════════════════════════════════

@install_bp.route('/api/installations', methods=['GET'])
@role_required('admin', 'sales', 'warehouse', 'tech', 'finance', 'director', 'support')
def get_installations():
    """Fetch installations. Technicians are restricted to their assigned projects."""
    user_role = get_current_user_role()
    if user_role == 'tech':
        user_name = session.get('user_name', '')
        rows = query_db("""SELECT i.*, c.name as customer_name FROM installations i
            JOIN customers c ON i.customer_id = c.id
            WHERE (i.technician LIKE ? OR i.technician IS NULL OR i.technician = '')
            ORDER BY i.id DESC""", [f'%{user_name}%'])
    else:
        rows = query_db("""SELECT i.*, c.name as customer_name FROM installations i
            JOIN customers c ON i.customer_id = c.id ORDER BY i.id DESC""")
    return jsonify(rows)


@install_bp.route('/api/installations/<int:iid>', methods=['GET'])
@role_required('admin', 'sales', 'warehouse', 'tech', 'finance', 'director', 'support')
def get_installation(iid):
    """Fetch single installation with technician domain isolation guard."""
    row = query_db("""SELECT i.*, c.name as customer_name FROM installations i
        JOIN customers c ON i.customer_id = c.id WHERE i.id = ?""", [iid], one=True)
    if not row:
        return jsonify({'error': 'Not found'}), 404

    user_role = get_current_user_role()
    if user_role == 'tech':
        user_name = session.get('user_name', '')
        assigned_tech = row.get('technician') or ''
        if assigned_tech and user_name and (user_name.lower() not in assigned_tech.lower()):
            return jsonify({
                'error': f'Access Denied (HTTP 403): Installation #{iid} is assigned to "{assigned_tech}". Technician "{user_name}" is strictly restricted to assigned installations.',
                'role': 'tech',
                'installation_id': iid,
                'status': 403
            }), 403

    serials = query_db("SELECT * FROM stock_lots WHERE allocated_to_installation = ?", [iid])
    row['serials'] = serials
    return jsonify(row)


@install_bp.route('/api/installations', methods=['POST'])
@role_required('admin', 'sales')
def create_installation():
    """Create installation job. Restricted to Admin and Sales."""
    d = request.get_json() or {}
    ref = get_next_ref('SF/INST', 'installations')

    survey = query_db("SELECT * FROM surveys WHERE id = ?", [d.get('survey_id', 0)], one=True)
    order = query_db("SELECT * FROM orders WHERE id = ?", [d.get('order_id', 0)], one=True)
    survey_ok = survey and survey['state'] == 'approved' if survey else False
    payment_ok = order and order['dispatch_unlocked'] if order else False

    score, label = calculate_readiness_score(survey_ok, payment_ok, False, False, bool(d.get('technician')))

    iid = execute_db("""INSERT INTO installations (ref, customer_id, order_id, survey_id, package_id,
        capacity_kw, system_type, scheduled_date, technician, state,
        readiness_score, readiness_label)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('order_id'), d.get('survey_id'), d.get('package_id'),
         d.get('capacity_kw', 3.0), d.get('system_type', 'on_grid'),
         d.get('scheduled_date', ''), d.get('technician', ''), 'draft', score, label])
    return jsonify({'id': iid, 'ref': ref, 'readiness_score': score, 'readiness_label': label}), 201


@install_bp.route('/api/installations/<int:iid>/phase', methods=['POST'])
@role_required('admin', 'tech')
def update_phase(iid):
    """Update installation phase milestone with technician assignment check."""
    user_role = get_current_user_role()
    inst = query_db("SELECT * FROM installations WHERE id = ?", [iid], one=True)
    if not inst:
        return jsonify({'error': 'Installation not found'}), 404

    # Restrict technician to assigned project
    if user_role == 'tech':
        user_name = session.get('user_name', '')
        assigned_tech = inst.get('technician') or ''
        if assigned_tech and user_name and (user_name.lower() not in assigned_tech.lower()):
            return jsonify({
                'error': f'Access Denied (HTTP 403): Technician "{user_name}" cannot update Installation #{iid} because it is assigned to "{assigned_tech}".',
                'role': 'tech',
                'installation_id': iid,
                'status': 403
            }), 403

    d = request.get_json() or {}
    phase = d.get('phase', '')
    value = 1 if d.get('completed', True) else 0

    valid_phases = ['phase_1_structure', 'phase_2_modules', 'phase_3_inverter',
                    'phase_4_earthing', 'phase_5_testing', 'phase_6_signoff']
    if phase not in valid_phases:
        return jsonify({'error': f'Invalid phase. Must be one of: {valid_phases}'}), 400

    if phase == 'phase_6_signoff' and value == 1:
        inst_check = query_db("SELECT qc_passed, qc_earth_ohm FROM installations WHERE id = ?", [iid], one=True)
        if not inst_check or not inst_check['qc_passed']:
            return jsonify({'error': 'Safety Gate Blocked: Cannot complete final sign-off. Electrical QC test with Earth Pit resistance <= 5.0 Ohm has not passed.'}), 400

    execute_db(f"UPDATE installations SET {phase} = ? WHERE id = ?", [value, iid])

    inst = query_db("SELECT * FROM installations WHERE id = ?", [iid], one=True)
    phases_done = sum([inst[p] for p in valid_phases])
    pct = round((phases_done / 6) * 100, 1)
    state = 'completed' if phases_done == 6 else ('in_progress' if phases_done > 0 else 'draft')

    execute_db("UPDATE installations SET completion_percent = ?, state = ? WHERE id = ?", [pct, state, iid])
    return jsonify({'completion_percent': pct, 'state': state, 'phases_completed': phases_done})


@install_bp.route('/api/installations/<int:iid>/qc', methods=['POST'])
@role_required('admin', 'tech')
def submit_qc(iid):
    """Submit electrical QC test results (Voc, Isc, Earth Pit Resistance)."""
    user_role = get_current_user_role()
    inst = query_db("SELECT * FROM installations WHERE id = ?", [iid], one=True)
    if not inst:
        return jsonify({'error': 'Installation not found'}), 404

    if user_role == 'tech':
        user_name = session.get('user_name', '')
        assigned_tech = inst.get('technician') or ''
        if assigned_tech and user_name and (user_name.lower() not in assigned_tech.lower()):
            return jsonify({
                'error': f'Access Denied (HTTP 403): Technician "{user_name}" cannot submit QC for Installation #{iid} (assigned to {assigned_tech}).',
                'role': 'tech',
                'status': 403
            }), 403

    d = request.get_json() or {}
    voc = d.get('voc', 0)
    isc = d.get('isc', 0)
    earth = d.get('earth_ohm', 0)

    qc_passed = 1 if (voc > 0 and isc > 0 and earth <= 5.0) else 0
    state = 'testing' if not qc_passed else 'completed'

    execute_db("""UPDATE installations SET qc_voc = ?, qc_isc = ?, qc_earth_ohm = ?,
        qc_passed = ?, state = ? WHERE id = ?""", [voc, isc, earth, qc_passed, state, iid])

    if qc_passed:
        msg = f'✅ QC PASSED — Voc={voc}V, Isc={isc}A, Earth={earth}Ω (≤5.0Ω)'
    else:
        failures = []
        if voc <= 0: failures.append(f'Voc={voc}V (must be >0)')
        if isc <= 0: failures.append(f'Isc={isc}A (must be >0)')
        if earth > 5.0: failures.append(f'Earth={earth}Ω (must be ≤5.0Ω)')
        msg = f'❌ QC FAILED — {", ".join(failures)}'

    return jsonify({'qc_passed': bool(qc_passed), 'message': msg})


@install_bp.route('/api/installations/<int:iid>/readiness', methods=['GET'])
@role_required('admin', 'sales', 'warehouse', 'tech', 'finance', 'director', 'support')
def get_readiness(iid):
    """Calculate and return Installation Readiness Score."""
    inst = query_db("SELECT * FROM installations WHERE id = ?", [iid], one=True)
    if not inst:
        return jsonify({'error': 'Not found'}), 404

    survey_ok = False
    if inst['survey_id']:
        survey = query_db("SELECT state FROM surveys WHERE id = ?", [inst['survey_id']], one=True)
        survey_ok = survey and survey['state'] == 'approved'

    payment_ok = False
    if inst['order_id']:
        order = query_db("SELECT dispatch_unlocked FROM orders WHERE id = ?", [inst['order_id']], one=True)
        payment_ok = order and order['dispatch_unlocked']

    stock_count = query_db("SELECT COUNT(*) as c FROM stock_lots WHERE allocated_to_installation = ?", [iid], one=True)['c']
    stock_ok = stock_count > 0
    equipment_ok = stock_ok
    tech_ok = bool(inst['technician'])

    score, label = calculate_readiness_score(survey_ok, payment_ok, stock_ok, equipment_ok, tech_ok)
    execute_db("UPDATE installations SET readiness_score = ?, readiness_label = ? WHERE id = ?", [score, label, iid])

    return jsonify({
        'readiness_score': score,
        'readiness_label': label,
        'breakdown': {
            'survey_approved': {'value': survey_ok, 'points': 20 if survey_ok else 0},
            'payment_50_percent': {'value': payment_ok, 'points': 20 if payment_ok else 0},
            'stock_available': {'value': stock_ok, 'points': 20 if stock_ok else 0},
            'equipment_allocated': {'value': equipment_ok, 'points': 20 if equipment_ok else 0},
            'technician_assigned': {'value': tech_ok, 'points': 20 if tech_ok else 0},
        }
    })
