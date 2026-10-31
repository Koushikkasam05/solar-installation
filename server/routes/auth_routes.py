# -*- coding: utf-8 -*-
"""SolarFlow ERP - Authentication & User Profile Routes."""
import hashlib
from flask import Blueprint, jsonify, request, session
from server.database import query_db, execute_db
from server.auth import login_required, ROLE_PERMISSIONS

auth_bp = Blueprint('auth', __name__)

# ROUTES: AUTHENTICATION
# ══════════════════════════════════════════════════════════════════════

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and create session."""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    pw_hash = hashlib.sha256(password.encode()).hexdigest()

    user = query_db("SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
                     [username, pw_hash], one=True)
    if not user:
        return jsonify({'error': 'Invalid username or password.'}), 401

    session['user_id'] = user['id']
    session['user_role'] = user['role']
    session['user_name'] = user['full_name']
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'email': user['email'],
            'role': user['role'],
            'title': user['title'],
            'permissions': ROLE_PERMISSIONS.get(user['role'], []),
        }
    })


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Clear user session."""
    session.clear()
    return jsonify({'message': 'Logged out successfully.'})


@auth_bp.route('/api/auth/me', methods=['GET'])
def current_user():
    """Get current authenticated user."""
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200
    user = query_db("SELECT * FROM users WHERE id = ?", [session['user_id']], one=True)
    if not user:
        return jsonify({'authenticated': False}), 200
    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'email': user['email'],
            'role': user['role'],
            'title': user['title'],
            'permissions': ROLE_PERMISSIONS.get(user['role'], []),
        }
    })


@auth_bp.route('/api/users', methods=['GET'])
def get_users():
    """Return system users list for User Management."""
    rows = query_db("SELECT id, username, full_name, email, role, title, is_active, created_at FROM users ORDER BY id ASC")
    return jsonify(rows)
