# -*- coding: utf-8 -*-
"""
SolarFlow ERP - Modular Application Factory
===========================================
Enterprise modular architecture separating concerns across:
- server/config.py     : Environment & storage paths
- server/database.py   : SQLite engine & connection lifecycle
- server/seed.py       : Initial database fixtures
- server/helpers.py    : Core solar math & domain business algorithms
- server/auth.py       : RBAC security decorators
- server/routes/       : 10 dedicated domain Blueprints
"""
import os
import sys
import subprocess

try:
    from flask import Flask
    from flask_cors import CORS
except ImportError:
    print("=" * 60)
    print("  Installing required dependencies: flask, flask-cors...")
    print("=" * 60)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    from flask import Flask
    from flask_cors import CORS

from server.config import SECRET_KEY, WEB_APP_DIR
from server.database import close_db, init_db
from server.seed import seed_demo_data
from server.routes import (
    frontend_bp, auth_bp, dashboard_bp, lead_bp,
    survey_bp, order_bp, stock_bp, install_bp,
    warranty_bp, cost_bp
)


def create_app():
    """Application factory for SolarFlow ERP."""
    app = Flask(__name__, static_folder=WEB_APP_DIR, static_url_path='/static')
    app.secret_key = SECRET_KEY
    CORS(app, supports_credentials=True)

    # Teardown database connection
    app.teardown_appcontext(close_db)

    # Initialize tables and seed demo data on startup
    with app.app_context():
        init_db()
        seed_demo_data()

    # Register modular Blueprints
    app.register_blueprint(frontend_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(lead_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(install_bp)
    app.register_blueprint(warranty_bp)
    app.register_blueprint(cost_bp)

    return app

