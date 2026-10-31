# -*- coding: utf-8 -*-
"""SolarFlow ERP - Serialized Equipment & Inventory Dispatch Routes."""
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db
from server.auth import role_required

stock_bp = Blueprint('stock', __name__)

# ROUTES: STOCK / INVENTORY (WAREHOUSE AUTHORIZATION GATES)
# ══════════════════════════════════════════════════════════════════════

@stock_bp.route('/api/stock', methods=['GET'])
@role_required('admin', 'warehouse', 'tech', 'support', 'director', 'finance', 'sales')
def get_stock():
    status_filter = request.args.get('status', None)
    if status_filter:
        rows = query_db("SELECT * FROM stock_lots WHERE status = ? ORDER BY id", [status_filter])
    else:
        rows = query_db("SELECT * FROM stock_lots ORDER BY id")
    return jsonify(rows)


@stock_bp.route('/api/stock', methods=['POST'])
@role_required('admin', 'warehouse')
def create_stock_lot():
    """Create equipment inventory item. Restricted to Admin and Warehouse."""
    d = request.get_json() or {}
    sid = execute_db("""INSERT INTO stock_lots (serial_number, product_name, category, status, warehouse, received_date)
        VALUES (?,?,?,?,?,?)""",
        [d['serial_number'], d['product_name'], d.get('category','pv_module'),
         'available', d.get('warehouse','Main Warehouse'), date.today().isoformat()])
    return jsonify({'id': sid, 'message': 'Stock lot created'}), 201


@stock_bp.route('/api/stock/<int:sid>/allocate', methods=['POST'])
@role_required('admin', 'warehouse')
def allocate_stock(sid):
    """Allocate a serial to an order/installation. Restricted to Admin and Warehouse."""
    d = request.get_json() or {}
    lot = query_db("SELECT * FROM stock_lots WHERE id = ?", [sid], one=True)
    if not lot:
        return jsonify({'error': 'Stock lot not found'}), 404
    if lot['status'] == 'allocated':
        return jsonify({'error': f'Serial {lot["serial_number"]} is already allocated. Single-active-allocation constraint violated.'}), 400

    if d.get('order_id'):
        order = query_db("SELECT dispatch_unlocked FROM orders WHERE id = ?", [d['order_id']], one=True)
        if order and not order['dispatch_unlocked']:
            return jsonify({'error': 'Dispatch Gate Blocked: Cannot dispatch equipment. Order requires minimum 50% advance payment before warehouse release.'}), 400

    execute_db("""UPDATE stock_lots SET status = 'allocated', allocated_to_order = ?,
        allocated_to_installation = ? WHERE id = ?""",
        [d.get('order_id'), d.get('installation_id'), sid])
    return jsonify({'message': f'Serial {lot["serial_number"]} allocated successfully.'})
