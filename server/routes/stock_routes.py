# -*- coding: utf-8 -*-
"""SolarFlow ERP - Serialized Equipment & Inventory Dispatch Routes."""
from datetime import datetime
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db

stock_bp = Blueprint('stock', __name__)

# ROUTES: STOCK / INVENTORY
# ══════════════════════════════════════════════════════════════════════

@stock_bp.route('/api/stock', methods=['GET'])
def get_stock():
    status_filter = request.args.get('status', None)
    if status_filter:
        rows = query_db("SELECT * FROM stock_lots WHERE status = ? ORDER BY id", [status_filter])
    else:
        rows = query_db("SELECT * FROM stock_lots ORDER BY id")
    return jsonify(rows)


@stock_bp.route('/api/stock', methods=['POST'])
def create_stock_lot():
    d = request.get_json()
    sid = execute_db("""INSERT INTO stock_lots (serial_number, product_name, category, status, warehouse, received_date)
        VALUES (?,?,?,?,?,?)""",
        [d['serial_number'], d['product_name'], d.get('category','pv_module'),
         'available', d.get('warehouse','Main Warehouse'), date.today().isoformat()])
    return jsonify({'id': sid, 'message': 'Stock lot created'}), 201


@stock_bp.route('/api/stock/<int:sid>/allocate', methods=['POST'])
def allocate_stock(sid):
    """Allocate a serial to an order/installation (single-active constraint)."""
    d = request.get_json()
    lot = query_db("SELECT * FROM stock_lots WHERE id = ?", [sid], one=True)
    if not lot:
        return jsonify({'error': 'Stock lot not found'}), 404
    if lot['status'] == 'allocated':
        return jsonify({'error': f'Serial {lot["serial_number"]} is already allocated. Single-active-allocation constraint violated.'}), 400

    execute_db("""UPDATE stock_lots SET status = 'allocated', allocated_to_order = ?,
        allocated_to_installation = ? WHERE id = ?""",
        [d.get('order_id'), d.get('installation_id'), sid])
    return jsonify({'message': f'Serial {lot["serial_number"]} allocated successfully.'})


# ══════════════════════════════════════════════════════════════════════

