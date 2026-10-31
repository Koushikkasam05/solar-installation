# -*- coding: utf-8 -*-
"""
SolarFlow ERP - Modular Application Entry Point
================================================
Divided into clean, individual modular components under /server:
- server/config.py     : Configuration & Path settings
- server/database.py   : SQLite Connection & Execution layer
- server/seed.py       : Initial Database Fixtures & Seeding
- server/helpers.py    : Domain Math & Solar Calculations
- server/auth.py       : RBAC Guards & Session Security
- server/routes/       : 10 domain-specific Flask Blueprints

Run:  python app.py
Open: http://localhost:5000
"""
from server import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  SolarFlow ERP – Modular Backend Server")
    print("=" * 60)
    print()
    print("  [URL] Server starting on: http://localhost:5000")
    print("  [API] API documentation:   http://localhost:5000/api/health")
    print("  [WEB]  Frontend:            http://localhost:5000")
    print()
    print("  Login Credentials (7 Enterprise Roles):")
    print("  ─────────────────────────────────────────")
    print("  admin    / admin123      (Super Administrator)")
    print("  sales    / sales123      (Sales Manager)")
    print("  warehouse/ warehouse123  (Warehouse Manager)")
    print("  tech     / tech123       (Installation Technician)")
    print("  support  / support123    (Support Manager)")
    print("  director / director123   (Managing Director)")
    print("  finance  / finance123    (Finance Controller)")
    print("  ─────────────────────────────────────────")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
