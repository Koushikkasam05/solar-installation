# -*- coding: utf-8 -*-
"""SolarFlow ERP - Authentication & Role-Based Access Control (RBAC)."""
from functools import wraps
from flask import session, jsonify

ROLE_PERMISSIONS = {
    'admin': ['all'],
    'sales': ['dashboard', 'enquiries', 'leads', 'followups', 'surveys', 'quotations', 'orders', 'installations', 'packages'],
    'warehouse': ['dashboard', 'stock', 'dispatches', 'inventory'],
    'technician': ['dashboard', 'installations', 'service'],
    'support': ['dashboard', 'warranties', 'service'],
    'director': ['dashboard', 'enquiries', 'leads', 'surveys', 'orders', 'installations', 'warranties', 'costing'],
    'finance': ['dashboard', 'orders', 'costing', 'warranties'],
}


def login_required(f):
    """Decorator: require authenticated session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required. Please login first.'}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """Decorator: require specific role(s)."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_role' not in session:
                return jsonify({'error': 'Authentication required.'}), 401
            user_role = session['user_role']
            if user_role != 'admin' and user_role not in allowed_roles:
                return jsonify({'error': f'Access Denied (HTTP 403): Role "{user_role}" is not authorized for this operation.'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
