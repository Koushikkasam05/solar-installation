# -*- coding: utf-8 -*-
"""SolarFlow ERP - Authentication & Role-Based Access Control (RBAC)."""
from functools import wraps
from flask import session, jsonify, request
from server.database import query_db

ROLE_PERMISSIONS = {
    'admin': ['all'],
    'sales': ['dashboard', 'customers', 'leads', 'surveys', 'packages', 'quotations', 'orders', 'installations', 'reports'],
    'warehouse': ['dashboard', 'packages', 'inventory', 'installations'],
    'tech': ['dashboard', 'surveys', 'inventory', 'installations', 'service'],
    'technician': ['dashboard', 'surveys', 'inventory', 'installations', 'service'],
    'support': ['dashboard', 'customers', 'inventory', 'warranties', 'service'],
    'finance': ['dashboard', 'quotations', 'payments', 'costing', 'reports'],
    'director': ['dashboard', 'customers', 'leads', 'surveys', 'packages', 'quotations', 'payments', 'inventory', 'installations', 'warranties', 'service', 'costing', 'reports'],
}


def normalize_role(role):
    """Normalize role aliases (e.g. technician -> tech)."""
    if not role:
        return None
    r = str(role).strip().lower()
    if r in ('technician', 'tech'):
        return 'tech'
    return r


def get_current_user_role():
    """Retrieve normalized current user role from session, or return None."""
    role = session.get('user_role')
    return normalize_role(role)


def login_required(f):
    """Decorator: require active authenticated user session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'error': 'Authentication Required (HTTP 401): Please login with valid credentials first.',
                'authenticated': False,
                'status': 401
            }), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """Decorator: require specific enterprise role(s) to access route.
    
    Rules enforced:
    1. Unauthenticated requests receive HTTP 401 Unauthorized.
    2. 'admin' role has universal authorization across all endpoints.
    3. 'director' role has strict read-only access (GET, HEAD, OPTIONS);
       any mutating request (POST, PUT, DELETE, PATCH) is rejected with HTTP 403.
    4. Roles not in allowed_roles receive HTTP 403 Forbidden with security context.
    """
    normalized_allowed = [normalize_role(r) for r in allowed_roles]
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({
                    'error': 'Authentication Required (HTTP 401): Access to this endpoint requires an active login session.',
                    'authenticated': False,
                    'status': 401
                }), 401

            user_role = get_current_user_role()

            # Super Administrator has universal access
            if user_role == 'admin':
                return f(*args, **kwargs)

            # Director has strict Read-Only executive privileges
            if user_role == 'director':
                if request.method not in ('GET', 'HEAD', 'OPTIONS'):
                    return jsonify({
                        'error': 'Access Denied (HTTP 403): Managing Director role has strict read-only executive privileges. Modifying records is forbidden.',
                        'role': user_role,
                        'attempted_method': request.method,
                        'status': 403
                    }), 403
                if 'director' in normalized_allowed or 'all' in normalized_allowed:
                    return f(*args, **kwargs)

            # Check if user's role is in authorized list
            if user_role not in normalized_allowed and 'all' not in normalized_allowed:
                return jsonify({
                    'error': f'Access Denied (HTTP 403): Role "{user_role}" is not authorized for this operation. Required role: {", ".join(allowed_roles)}.',
                    'role': user_role,
                    'allowed_roles': list(allowed_roles),
                    'status': 403
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator


def technician_assignment_guard(f):
    """Decorator: restricts technicians to updating only installations assigned to them."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_role = get_current_user_role()
        if user_role == 'tech':
            inst_id = kwargs.get('id')
            user_name = session.get('user_name', '')
            user_id = session.get('user_id')
            if inst_id:
                inst = query_db("SELECT * FROM installations WHERE id = ?", [inst_id], one=True)
                if inst:
                    assigned_name = inst.get('technician') or ''
                    # If this installation is assigned to another technician, block access
                    if assigned_name and user_name and (user_name.lower() not in assigned_name.lower()):
                        return jsonify({
                            'error': f'Access Denied (HTTP 403): Technician "{user_name}" is not assigned to Installation #{inst_id} (assigned to: {assigned_name}). Technicians may only update their assigned projects.',
                            'role': 'tech',
                            'installation_id': inst_id,
                            'assigned_technician': assigned_name,
                            'status': 403
                        }), 403
        return f(*args, **kwargs)
    return decorated
