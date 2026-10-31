# -*- coding: utf-8 -*-
"""SolarFlow ERP - Frontend Static Delivery & Health Check."""
from flask import Blueprint, send_from_directory, jsonify
from datetime import datetime
from server.config import WEB_APP_DIR

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def serve_index():
    return send_from_directory(WEB_APP_DIR, 'index.html')

@frontend_bp.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(WEB_APP_DIR, filename)

@frontend_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'system': 'SolarFlow ERP - Modular Backend Engine',
        'version': '2.0.0',
        'database': 'SQLite',
        'timestamp': datetime.now().isoformat(),
    })
