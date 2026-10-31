# -*- coding: utf-8 -*-
"""SolarFlow ERP - Site Survey Feasibility & BOM Routes."""
import json
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db
from server.helpers import calculate_auto_bom, generate_auto_bom, get_next_ref
from server.auth import role_required

survey_bp = Blueprint('surveys', __name__)

# ROUTES: SITE SURVEYS (ENGINEERING & SALES RBAC GATES)
# ══════════════════════════════════════════════════════════════════════

@survey_bp.route('/api/surveys', methods=['GET'])
@role_required('admin', 'sales', 'tech', 'director', 'finance')
def get_surveys():
    rows = query_db("""SELECT s.*, c.name as customer_name FROM surveys s
        JOIN customers c ON s.customer_id = c.id ORDER BY s.id DESC""")
    return jsonify(rows)


@survey_bp.route('/api/surveys/<int:sid>', methods=['GET'])
@role_required('admin', 'sales', 'tech', 'director', 'finance')
def get_survey(sid):
    row = query_db("""SELECT s.*, c.name as customer_name FROM surveys s
        JOIN customers c ON s.customer_id = c.id WHERE s.id = ?""", [sid], one=True)
    return jsonify(row) if row else (jsonify({'error': 'Not found'}), 404)


@survey_bp.route('/api/surveys', methods=['POST'])
@role_required('admin', 'sales', 'tech')
def create_survey():
    d = request.get_json() or {}
    if not d.get('customer_id'):
        return jsonify({'error': 'Validation Error: Customer ID is required for site survey.'}), 400
    if not d.get('usable_area') or str(d.get('usable_area')).strip() == '':
        return jsonify({'error': 'Validation Error: Usable shadow-free roof area is mandatory.'}), 400
    if not d.get('roof_type') or str(d.get('roof_type')).strip() == '':
        return jsonify({'error': 'Validation Error: Roof type is mandatory.'}), 400

    ref = get_next_ref('SRV', 'surveys').replace('/', '-')
    sid = execute_db("""INSERT INTO surveys (ref, customer_id, lead_id, roof_type, total_area, usable_area,
        azimuth, tilt, cable_distance_m, grid_phase, recommended_kw, state, engineer, notes, survey_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('lead_id'), d.get('roof_type','RCC Flat'),
         d.get('total_area',''), d.get('usable_area',''), d.get('azimuth','180° South'),
         d.get('tilt','15°'), d.get('cable_distance_m', 20), d.get('grid_phase','Single Phase 230V'),
         d.get('recommended_kw', 3.0), 'draft', d.get('engineer',''), d.get('notes',''),
         d.get('survey_date', date.today().isoformat())])
    return jsonify({'id': sid, 'ref': ref, 'message': 'Survey created'}), 201


@survey_bp.route('/api/surveys/<int:sid>/approve', methods=['POST'])
@role_required('admin', 'sales')
def approve_survey(sid):
    """Chief Engineer / Sales Manager approval. Technicians and Directors blocked."""
    execute_db("UPDATE surveys SET state = 'approved' WHERE id = ? AND state IN ('draft','submitted')", [sid])
    return jsonify({'message': 'Survey approved'})


@survey_bp.route('/api/surveys/<int:sid>/reject', methods=['POST'])
@role_required('admin', 'sales')
def reject_survey(sid):
    d = request.get_json() or {}
    execute_db("UPDATE surveys SET state = 'rejected', rejection_reason = ? WHERE id = ?",
        [d.get('reason', 'No reason provided'), sid])
    return jsonify({'message': 'Survey rejected'})


# ══════════════════════════════════════════════════════════════════════
# ROUTES: SOLAR PACKAGES
# ══════════════════════════════════════════════════════════════════════

@survey_bp.route('/api/packages', methods=['GET'])
@role_required('admin', 'sales', 'warehouse', 'tech', 'director', 'finance')
def get_packages():
    packages = query_db("SELECT * FROM packages WHERE is_active = 1 ORDER BY capacity_kw")
    for pkg in packages:
        pkg['bom'] = query_db("SELECT * FROM package_lines WHERE package_id = ?", [pkg['id']])
    return jsonify(packages)


@survey_bp.route('/api/packages/<int:pid>', methods=['GET'])
@role_required('admin', 'sales', 'warehouse', 'tech', 'director', 'finance')
def get_package(pid):
    pkg = query_db("SELECT * FROM packages WHERE id = ?", [pid], one=True)
    if not pkg:
        return jsonify({'error': 'Package not found'}), 404
    pkg['bom'] = query_db("SELECT * FROM package_lines WHERE package_id = ?", [pid])
    return jsonify(pkg)


@survey_bp.route('/api/bom/calculate', methods=['POST'])
@role_required('admin', 'sales', 'warehouse', 'tech', 'director', 'finance')
def calculate_bom_api():
    """Calculate Auto-BOM for a given system size."""
    d = request.get_json() or {}
    bom = calculate_auto_bom(d.get('system_kw', 3.0), d.get('cable_distance_m', 20))
    return jsonify(bom)
