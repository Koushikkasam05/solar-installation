# -*- coding: utf-8 -*-
"""SolarFlow ERP - Commercial Quotations & Sales Orders Routes."""
import json
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from server.database import query_db, execute_db
from server.helpers import get_next_ref, calculate_subsidy

order_bp = Blueprint('orders', __name__)

# ROUTES: SALES ORDERS
# ══════════════════════════════════════════════════════════════════════

@order_bp.route('/api/orders', methods=['GET'])
def get_orders():
    rows = query_db("""SELECT o.*, c.name as customer_name FROM orders o
        JOIN customers c ON o.customer_id = c.id ORDER BY o.id DESC""")
    return jsonify(rows)


@order_bp.route('/api/orders/<int:oid>', methods=['GET'])
def get_order(oid):
    row = query_db("""SELECT o.*, c.name as customer_name FROM orders o
        JOIN customers c ON o.customer_id = c.id WHERE o.id = ?""", [oid], one=True)
    return jsonify(row) if row else (jsonify({'error': 'Not found'}), 404)


@order_bp.route('/api/orders', methods=['POST'])
def create_order():
    d = request.get_json()
    ref = get_next_ref('SF/SO', 'orders')

    # Get package price
    pkg_price = 0
    if d.get('package_id'):
        pkg = query_db("SELECT total_price FROM packages WHERE id = ?", [d['package_id']], one=True)
        if pkg:
            pkg_price = pkg['total_price']

    system_kw = d.get('system_kw', 3.0)
    if 'subsidy_amount' in d:
        subsidy = float(d['subsidy_amount'])
    elif d.get('subsidy', False):
        subsidy = 468.0 if system_kw == 3.0 else round(min(pkg_price * 0.3, 1000.0), 2)
    else:
        subsidy = 0.0
    net_price = pkg_price - subsidy

    oid = execute_db("""INSERT INTO orders (ref, customer_id, lead_id, survey_id, package_id,
        system_kw, system_type, package_price, subsidy_amount, net_price,
        amount_paid, payment_percent, dispatch_unlocked, status, order_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('lead_id'), d.get('survey_id'), d.get('package_id'),
         system_kw, d.get('system_type', 'on_grid'), pkg_price, subsidy, net_price,
         0, 0, 0, 'draft', date.today().isoformat()])
    return jsonify({'id': oid, 'ref': ref, 'net_price': net_price}), 201


@order_bp.route('/api/orders/<int:oid>/payment', methods=['POST'])
def record_payment(oid):
    """Record payment and check 50% advance gate."""
    d = request.get_json()
    order = query_db("SELECT * FROM orders WHERE id = ?", [oid], one=True)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    new_paid = order['amount_paid'] + d.get('amount', 0)
    net = order['net_price'] if order['net_price'] > 0 else 1
    pct = round((new_paid / net) * 100, 2)
    dispatch_ok = 1 if pct >= 50 else 0

    execute_db("""UPDATE orders SET amount_paid = ?, payment_percent = ?, dispatch_unlocked = ?,
        status = CASE WHEN ? >= 50 THEN 'confirmed' ELSE status END WHERE id = ?""",
        [new_paid, pct, dispatch_ok, pct, oid])

    return jsonify({
        'amount_paid': new_paid,
        'payment_percent': pct,
        'dispatch_unlocked': bool(dispatch_ok),
        'message': '✅ 50% advance received — dispatch unlocked!' if dispatch_ok else f'Payment recorded. {pct}% paid (need 50% to unlock dispatch).'
    })


@order_bp.route('/api/orders/<int:oid>/confirm', methods=['POST'])
def confirm_order(oid):
    execute_db("UPDATE orders SET status = 'confirmed' WHERE id = ? AND status = 'draft'", [oid])
    return jsonify({'message': 'Order confirmed'})


@order_bp.route('/api/quotations', methods=['GET'])
def get_quotations():
    """Return all quotations and proposals."""
    rows = query_db("""SELECT o.*, c.name as customer_name, c.phone as customer_phone,
                              c.email as customer_email, p.name as package_name
                       FROM orders o
                       JOIN customers c ON o.customer_id = c.id
                       LEFT JOIN packages p ON o.package_id = p.id
                       ORDER BY o.id DESC""")
    return jsonify(rows)


@order_bp.route('/api/payments', methods=['GET'])
def get_payments():
    """Return payments overview."""
    rows = query_db("""SELECT o.id, o.ref as order_ref, o.net_price, o.amount_paid,
                              o.payment_percent, o.dispatch_unlocked, o.status,
                              o.order_date, c.name as customer_name, c.phone as customer_phone
                       FROM orders o
                       JOIN customers c ON o.customer_id = c.id
                       ORDER BY o.id DESC""")
    return jsonify(rows)


# ══════════════════════════════════════════════════════════════════════

