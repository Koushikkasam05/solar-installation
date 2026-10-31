# -*- coding: utf-8 -*-
"""
SolarFlow ERP – Flask Backend API Server
=========================================
Complete REST API backend for Solar Installation Management System.
- SQLite database (zero external dependencies)
- Full CRUD for all 10 business modules
- JWT-free session auth with 6 RBAC roles
- All business logic: Readiness Score, Auto-BOM, SHA-256 Warranty, Profit Alerts
- Serves the frontend from /web_app

Run:  py app.py
Open: http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory, session, g
from flask_cors import CORS
import sqlite3
import hashlib
import math
import os
import json
from datetime import datetime, date, timedelta
from functools import wraps

# ── App Configuration ─────────────────────────────────────────────────
app = Flask(__name__, static_folder='web_app', static_url_path='/static')
app.secret_key = 'solarflow_secret_key_2026'
CORS(app, supports_credentials=True)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solarflow.db')


# ══════════════════════════════════════════════════════════════════════
# DATABASE LAYER
# ══════════════════════════════════════════════════════════════════════

def get_db():
    """Get database connection for current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Execute a query and return results as list of dicts."""
    cur = get_db().execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE and return lastrowid."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


# ── Create All Tables ─────────────────────────────────────────────────

def init_db():
    """Initialize all database tables."""
    db = sqlite3.connect(DATABASE)
    db.executescript('''
        -- ──────────────── Users & Authentication ────────────────
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'sales',
            title TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ──────────────── Customers ────────────────
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            city TEXT DEFAULT '',
            state TEXT DEFAULT '',
            property_type TEXT DEFAULT 'Residential',
            sanctioned_load_kw REAL DEFAULT 5.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ──────────────── Enquiries ────────────────
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            date TEXT,
            property_type TEXT,
            sanctioned_load TEXT,
            status TEXT DEFAULT 'new',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        -- ──────────────── Solar Leads ────────────────
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            monthly_kwh REAL DEFAULT 0,
            tariff_rate REAL DEFAULT 0.10,
            sized_kw REAL DEFAULT 3.0,
            system_type TEXT DEFAULT 'on_grid',
            subsidy_required INTEGER DEFAULT 1,
            roof_area_sqft REAL DEFAULT 500,
            sanctioned_load_kw REAL DEFAULT 5.0,
            recommended_kw REAL DEFAULT 0,
            feasibility_score INTEGER DEFAULT 100,
            status TEXT DEFAULT 'draft',
            lead_source TEXT DEFAULT 'web_inbound',
            assigned_to INTEGER,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        -- ──────────────── Site Surveys ────────────────
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            lead_id INTEGER,
            roof_type TEXT DEFAULT 'RCC Flat',
            total_area TEXT,
            usable_area TEXT,
            azimuth TEXT DEFAULT '180° South',
            tilt TEXT DEFAULT '15°',
            cable_distance_m REAL DEFAULT 20,
            grid_phase TEXT DEFAULT 'Single Phase 230V',
            recommended_kw REAL DEFAULT 3.0,
            shadow_analysis TEXT DEFAULT '',
            state TEXT DEFAULT 'draft',
            engineer TEXT DEFAULT '',
            rejection_reason TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            survey_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        );

        -- ──────────────── Solar Packages ────────────────
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT NOT NULL,
            capacity_kw REAL NOT NULL,
            system_type TEXT DEFAULT 'on_grid',
            total_price REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1
        );

        -- ──────────────── Package BOM Lines ────────────────
        CREATE TABLE IF NOT EXISTS package_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT DEFAULT 'component',
            quantity INTEGER DEFAULT 1,
            unit_price REAL DEFAULT 0,
            subtotal REAL DEFAULT 0,
            FOREIGN KEY (package_id) REFERENCES packages(id)
        );

        -- ──────────────── Sales Orders ────────────────
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            lead_id INTEGER,
            survey_id INTEGER,
            package_id INTEGER,
            system_kw REAL DEFAULT 3.0,
            system_type TEXT DEFAULT 'on_grid',
            package_price REAL DEFAULT 0,
            subsidy_amount REAL DEFAULT 0,
            net_price REAL DEFAULT 0,
            amount_paid REAL DEFAULT 0,
            payment_percent REAL DEFAULT 0,
            dispatch_unlocked INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            order_date TEXT,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        -- ──────────────── Inventory / Stock Lots ────────────────
        CREATE TABLE IF NOT EXISTS stock_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT DEFAULT 'pv_module',
            status TEXT DEFAULT 'available',
            warehouse TEXT DEFAULT 'Main Warehouse',
            allocated_to_order INTEGER,
            allocated_to_installation INTEGER,
            received_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ──────────────── Installations ────────────────
        CREATE TABLE IF NOT EXISTS installations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            order_id INTEGER,
            survey_id INTEGER,
            package_id INTEGER,
            capacity_kw REAL DEFAULT 3.0,
            system_type TEXT DEFAULT 'on_grid',
            scheduled_date TEXT,
            start_date TEXT,
            completion_date TEXT,
            technician TEXT DEFAULT '',
            crew_members TEXT DEFAULT '',
            state TEXT DEFAULT 'draft',
            -- 6-Phase Milestones
            phase_1_structure INTEGER DEFAULT 0,
            phase_2_modules INTEGER DEFAULT 0,
            phase_3_inverter INTEGER DEFAULT 0,
            phase_4_earthing INTEGER DEFAULT 0,
            phase_5_testing INTEGER DEFAULT 0,
            phase_6_signoff INTEGER DEFAULT 0,
            completion_percent REAL DEFAULT 0,
            -- Electrical QC
            qc_voc REAL DEFAULT 0,
            qc_isc REAL DEFAULT 0,
            qc_earth_ohm REAL DEFAULT 0,
            qc_passed INTEGER DEFAULT 0,
            -- Readiness Score
            readiness_score INTEGER DEFAULT 0,
            readiness_label TEXT DEFAULT 'Not Ready',
            -- Customer Sign-off
            customer_signoff INTEGER DEFAULT 0,
            signoff_date TEXT,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        -- ──────────────── Digital Warranties ────────────────
        CREATE TABLE IF NOT EXISTS warranties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            installation_id INTEGER,
            serial_number TEXT,
            equipment_type TEXT DEFAULT 'pv_module',
            warranty_years INTEGER DEFAULT 25,
            start_date TEXT,
            expiry_date TEXT,
            sha256_token TEXT,
            status TEXT DEFAULT 'active',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        -- ──────────────── Service Tickets ────────────────
        CREATE TABLE IF NOT EXISTS service_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            customer_id INTEGER NOT NULL,
            installation_id INTEGER,
            warranty_id INTEGER,
            serial_number TEXT,
            issue_type TEXT DEFAULT 'inverter_fault',
            description TEXT DEFAULT '',
            is_under_warranty INTEGER DEFAULT 0,
            parts_cost REAL DEFAULT 0,
            labour_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            assigned_to TEXT DEFAULT '',
            resolution TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        -- ──────────────── Project Costing ────────────────
        CREATE TABLE IF NOT EXISTS project_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref TEXT UNIQUE,
            installation_id INTEGER,
            customer_id INTEGER,
            order_id INTEGER,
            revenue REAL DEFAULT 0,
            material_cost REAL DEFAULT 0,
            labour_cost REAL DEFAULT 0,
            transport_cost REAL DEFAULT 0,
            additional_cost REAL DEFAULT 0,
            other_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            gross_profit REAL DEFAULT 0,
            gross_margin_percent REAL DEFAULT 0,
            margin_health TEXT DEFAULT 'healthy',
            leakage_alert INTEGER DEFAULT 0,
            leakage_threshold REAL DEFAULT 10.0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (installation_id) REFERENCES installations(id)
        );

        -- ──────────────── Follow-ups ────────────────
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            date TEXT,
            sales_rep TEXT DEFAULT '',
            type TEXT DEFAULT '',
            summary TEXT DEFAULT '',
            priority TEXT DEFAULT 'Normal',
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    ''')
    db.commit()
    db.close()


# ── Seed Demo Data ────────────────────────────────────────────────────

def seed_demo_data():
    """Populate database with realistic demo data (runs only if empty)."""
    db = sqlite3.connect(DATABASE)

    # Check if already seeded
    count = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    if count > 0:
        db.close()
        return

    # ── Users (6 roles) ──
    users = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'System Administrator', 'admin@solarflow.erp', 'admin', 'Chief Executive Officer'),
        ('sales', hashlib.sha256('sales123'.encode()).hexdigest(), 'Vikram Sales Manager', 'sales@solarflow.erp', 'sales', 'Head of Solar Sales'),
        ('survey', hashlib.sha256('survey123'.encode()).hexdigest(), 'Arun Survey Tech', 'survey@solarflow.erp', 'survey_tech', 'Field Solar Surveyor'),
        ('warehouse', hashlib.sha256('warehouse123'.encode()).hexdigest(), 'Sanjay Warehouse Manager', 'warehouse@solarflow.erp', 'warehouse', 'Supply Chain Lead'),
        ('tech', hashlib.sha256('tech123'.encode()).hexdigest(), 'Ramesh Electrician', 'tech@solarflow.erp', 'technician', 'Senior Electrical Lead'),
        ('support', hashlib.sha256('support123'.encode()).hexdigest(), 'Priya Support Manager', 'support@solarflow.erp', 'support', 'After-Sales Manager'),
        ('director', hashlib.sha256('director123'.encode()).hexdigest(), 'Anand Mehta', 'director@solarflow.erp', 'director', 'Managing Director'),
        ('finance', hashlib.sha256('finance123'.encode()).hexdigest(), 'Kavitha Finance', 'finance@solarflow.erp', 'finance', 'Finance Controller'),
    ]
    db.executemany("INSERT INTO users (username, password_hash, full_name, email, role, title) VALUES (?,?,?,?,?,?)", users)

    # ── Customers (10) ──
    customers = [
        ('Dr. Rajesh Sharma', '+91 98765 43210', 'rajesh@email.com', '42 Palm Meadows, Whitefield', 'Bengaluru', 'Karnataka', 'Residential', 5.0),
        ('GreenTech Logistics Pvt Ltd', '+91 80 4567 8901', 'ops@greentech.in', 'Industrial Area Phase II', 'Hyderabad', 'Telangana', 'Industrial', 60.0),
        ('Mrs. Sunita Kapoor', '+91 99887 65432', 'sunita@email.com', '15 Harmony Villas, Jubilee Hills', 'Hyderabad', 'Telangana', 'Residential', 7.0),
        ('Mr. Arvind Patel', '+91 94567 12345', 'arvind@email.com', '88 Lake View Colony', 'Ahmedabad', 'Gujarat', 'Residential', 5.0),
        ('Sunrise Apartments Association', '+91 44 2345 6789', 'rwa@sunrise.in', 'Sunrise Towers, OMR Road', 'Chennai', 'Tamil Nadu', 'Commercial', 12.0),
        ('FreshCold Storage Pvt Ltd', '+91 22 8765 4321', 'facility@freshcold.in', 'MIDC Bhosari Complex', 'Pune', 'Maharashtra', 'Industrial', 100.0),
        ('Mr. Deepak Verma', '+91 87654 32100', 'deepak@email.com', '5 Tin Shed Lane, Old City', 'Jaipur', 'Rajasthan', 'Residential', 3.0),
        ('MegaMart Retail Chain', '+91 11 5678 9012', 'energy@megamart.in', 'Sector 62 Business Park', 'Noida', 'UP', 'Commercial', 150.0),
        ('Mrs. Lakshmi Nair', '+91 97531 24680', 'lakshmi@email.com', '22 Coconut Grove, Vyttila', 'Kochi', 'Kerala', 'Residential', 4.0),
        ('TechPark Innovation Hub', '+91 80 9876 5432', 'infra@techpark.in', 'Electronic City Phase I', 'Bengaluru', 'Karnataka', 'Commercial', 80.0),
    ]
    db.executemany("INSERT INTO customers (name, phone, email, address, city, state, property_type, sanctioned_load_kw) VALUES (?,?,?,?,?,?,?,?)", customers)

    # ── Enquiries (4) ──
    enquiries = [
        ('ENQ-2026-0101', 1, '2026-10-25', 'RCC Rooftop', '5.0 kW', 'qualified'),
        ('ENQ-2026-0102', 2, '2026-10-26', 'Metal Industrial Shed', '60.0 kW', 'new'),
        ('ENQ-2026-0103', 3, '2026-10-28', 'Terrace Villa', '7.0 kW', 'qualified'),
        ('ENQ-2026-0104', 5, '2026-10-30', 'Independent House', '12.0 kW', 'new'),
    ]
    db.executemany("INSERT INTO enquiries (ref, customer_id, date, property_type, sanctioned_load, status) VALUES (?,?,?,?,?,?)", enquiries)

    # ── Leads (10) ──
    leads = [
        ('SF/LEAD/2026/0001', 1, 380, 0.10, 3.0, 'on_grid', 1, 650, 5.0, 'approved', 'web_inbound'),
        ('SF/LEAD/2026/0002', 2, 6500, 0.13, 50.0, 'on_grid', 0, 5000, 60.0, 'draft', 'direct_walkin'),
        ('SF/LEAD/2026/0003', 3, 550, 0.10, 5.0, 'hybrid', 1, 900, 7.0, 'scheduled', 'referral'),
        ('SF/LEAD/2026/0004', 4, 420, 0.12, 5.0, 'off_grid', 0, 600, 5.0, 'draft', 'expo'),
        ('SF/LEAD/2026/0005', 5, 1200, 0.10, 10.0, 'on_grid', 1, 2000, 12.0, 'draft', 'channel_partner'),
        ('SF/LEAD/2026/0006', 6, 3200, 0.11, 25.0, 'on_grid', 0, 4000, 100.0, 'draft', 'telemarketing'),
        ('SF/LEAD/2026/0007', 7, 240, 0.10, 2.0, 'on_grid', 1, 350, 3.0, 'rejected', 'web_inbound'),
        ('SF/LEAD/2026/0008', 8, 14000, 0.14, 100.0, 'on_grid', 0, 10000, 150.0, 'draft', 'expo'),
        ('SF/LEAD/2026/0009', 9, 340, 0.10, 3.0, 'hybrid', 1, 500, 4.0, 'draft', 'referral'),
        ('SF/LEAD/2026/0010', 10, 5200, 0.12, 40.0, 'on_grid', 0, 6000, 80.0, 'draft', 'channel_partner'),
    ]
    db.executemany("""INSERT INTO leads (ref, customer_id, monthly_kwh, tariff_rate, sized_kw, system_type,
        subsidy_required, roof_area_sqft, sanctioned_load_kw, status, lead_source) VALUES (?,?,?,?,?,?,?,?,?,?,?)""", leads)

    # ── Surveys (3) ──
    surveys = [
        ('SRV-2026-0001', 1, 1, 'RCC Flat Concrete', '650 sq.ft', '500 sq.ft', '180° South (Optimal)', '12°', 20, 'Single Phase 230V', 3.0, 'approved', 'Arun K. (Chief Engineer)', '', 'Rooftop is flat RCC with zero shading.', '2026-10-20'),
        ('SRV-2026-0002', 3, 3, 'RCC Flat Terrace', '900 sq.ft', '700 sq.ft', '210° South-West', '15°', 25, 'Three Phase 415V', 5.0, 'scheduled', 'Pending Assignment', '', 'Scheduled shadow analysis.', '2026-11-05'),
        ('SRV-2026-0003', 7, 7, 'Asbestos Tin Shed', '350 sq.ft', '120 sq.ft', '0° North (Low Yield)', '25°', 55, 'Single Phase', 1.0, 'rejected', 'Arun K. (Chief Engineer)', 'Severe structural weakness in corrugated tin roof.', 'Infeasible for mounting.', '2026-10-18'),
    ]
    db.executemany("""INSERT INTO surveys (ref, customer_id, lead_id, roof_type, total_area, usable_area,
        azimuth, tilt, cable_distance_m, grid_phase, recommended_kw, state, engineer, rejection_reason, notes, survey_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", surveys)

    # ── Packages (3) with BOM Lines ──
    packages = [
        ('SF-PKG-3KW-OG', '3kW On-Grid Solar Package', 3.0, 'on_grid', 1770),
        ('SF-PKG-5KW-HYB', '5kW Smart Hybrid Solar Package', 5.0, 'hybrid', 4530),
        ('SF-PKG-5KW-OG', '5kW On-Grid Solar Package', 5.0, 'on_grid', 2850),
    ]
    db.executemany("INSERT INTO packages (code, name, capacity_kw, system_type, total_price) VALUES (?,?,?,?,?)", packages)

    bom_lines = [
        # Package 1: 3kW On-Grid
        (1, 'Canadian Solar 550W Mono PERC Modules', 'panel', 6, 154, 924),
        (1, 'Growatt 3kW Dual MPPT Grid-Tie Inverter', 'inverter', 1, 580, 580),
        (1, 'Elevated HDGI Mounting Structure Rails', 'structure', 6, 26, 156),
        (1, 'Class II ACDB/DCDB, SPDs & DC Cables', 'electrical', 1, 110, 110),
        # Package 2: 5kW Hybrid
        (2, 'Canadian Solar 550W Mono PERC Modules', 'panel', 10, 154, 1540),
        (2, 'Deye 5kW Hybrid Inverter with EMS', 'inverter', 1, 1150, 1150),
        (2, 'BYD LiFePO4 48V 100Ah Battery Bank (5kWh)', 'battery', 1, 1400, 1400),
        (2, 'Elevated HDGI Mounting Structure', 'structure', 10, 26, 260),
        (2, 'IP65 Hybrid ACDB/DCDB & Safety Kit', 'electrical', 1, 180, 180),
        # Package 3: 5kW On-Grid
        (3, 'Canadian Solar 550W Mono PERC Modules', 'panel', 10, 154, 1540),
        (3, 'Growatt 5kW Dual MPPT Grid-Tie Inverter', 'inverter', 1, 850, 850),
        (3, 'Elevated HDGI Mounting Structure Rails', 'structure', 10, 26, 260),
        (3, 'Class II ACDB/DCDB, SPDs & DC Cables', 'electrical', 1, 200, 200),
    ]
    db.executemany("INSERT INTO package_lines (package_id, item_name, category, quantity, unit_price, subtotal) VALUES (?,?,?,?,?,?)", bom_lines)

    # ── Sales Orders (2) ──
    orders = [
        ('SF/SO/2026/0001', 1, 1, 1, 1, 3.0, 'on_grid', 1770, 468, 1302, 651, 50.0, 1, 'confirmed', '2026-10-22'),
        ('SF/SO/2026/0002', 3, 3, 2, 2, 5.0, 'hybrid', 4530, 0, 4530, 0, 0.0, 0, 'draft', '2026-10-30'),
    ]
    db.executemany("""INSERT INTO orders (ref, customer_id, lead_id, survey_id, package_id, system_kw, system_type,
        package_price, subsidy_amount, net_price, amount_paid, payment_percent, dispatch_unlocked, status, order_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", orders)

    # ── Stock Lots (8) ──
    stock_lots = [
        ('CS550-2026-A001', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A002', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A003', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A004', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A005', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A006', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('GRW3K-2026-INV01', 'Growatt 3kW Grid-Tie Inverter', 'inverter', 'allocated', 'Main Warehouse', 1, 1, '2026-10-16'),
        ('CS550-2026-B001', 'Canadian Solar 550W Module', 'pv_module', 'available', 'Main Warehouse', None, None, '2026-10-20'),
    ]
    db.executemany("""INSERT INTO stock_lots (serial_number, product_name, category, status, warehouse,
        allocated_to_order, allocated_to_installation, received_date) VALUES (?,?,?,?,?,?,?,?)""", stock_lots)

    # ── Installation (1 completed showcase) ──
    installations = [
        ('SF/INST/2026/0001', 1, 1, 1, 1, 3.0, 'on_grid', '2026-10-25', '2026-10-25', '2026-10-26',
         'Ramesh Electrician', 'Ramesh, Suresh, Mahesh', 'completed',
         1, 1, 1, 1, 1, 1, 100.0,
         38.5, 9.2, 2.4, 1,
         100, 'Ready for Execution',
         1, '2026-10-26', 'Flawless 3kW commissioning completed.'),
    ]
    db.executemany("""INSERT INTO installations (ref, customer_id, order_id, survey_id, package_id,
        capacity_kw, system_type, scheduled_date, start_date, completion_date,
        technician, crew_members, state,
        phase_1_structure, phase_2_modules, phase_3_inverter, phase_4_earthing, phase_5_testing, phase_6_signoff,
        completion_percent, qc_voc, qc_isc, qc_earth_ohm, qc_passed,
        readiness_score, readiness_label,
        customer_signoff, signoff_date, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", installations)

    # ── Warranties (2) ──
    token_data_1 = "SF/WTY/2026/0001|1|CS550-2026-A001|pv_module|2026-10-26"
    token_1 = hashlib.sha256(token_data_1.encode()).hexdigest()
    token_data_2 = "SF/WTY/2026/0002|1|GRW3K-2026-INV01|inverter|2026-10-26"
    token_2 = hashlib.sha256(token_data_2.encode()).hexdigest()

    warranties = [
        ('SF/WTY/2026/0001', 1, 1, 'CS550-2026-A001', 'pv_module', 25, '2026-10-26', '2051-10-26', token_1, 'active'),
        ('SF/WTY/2026/0002', 1, 1, 'GRW3K-2026-INV01', 'inverter', 10, '2026-10-26', '2036-10-26', token_2, 'active'),
    ]
    db.executemany("""INSERT INTO warranties (ref, customer_id, installation_id, serial_number,
        equipment_type, warranty_years, start_date, expiry_date, sha256_token, status)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", warranties)

    # ── Service Tickets (1) ──
    service_tickets = [
        ('SF/SVC/2026/0001', 1, 1, 1, 'GRW3K-2026-INV01', 'inverter_fault',
         'Inverter showing grid voltage fluctuation alarm code E-014.', 1,
         0, 0, 0, 'resolved', 'high', 'Ramesh Electrician',
         'Firmware update resolved alarm. No hardware replacement needed.', '2026-10-28'),
    ]
    db.executemany("""INSERT INTO service_tickets (ref, customer_id, installation_id, warranty_id,
        serial_number, issue_type, description, is_under_warranty,
        parts_cost, labour_cost, total_cost, status, priority, assigned_to,
        resolution, resolved_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", service_tickets)

    # ── Project Costing (1) ──
    project_costs = [
        ('SF/COST/2026/0001', 1, 1, 1, 2040, 1200, 200, 60, 30, 10, 1500, 540, 26.47, 'healthy', 0, 10.0),
    ]
    db.executemany("""INSERT INTO project_costs (ref, installation_id, customer_id, order_id,
        revenue, material_cost, labour_cost, transport_cost, additional_cost, other_cost,
        total_cost, gross_profit, gross_margin_percent, margin_health, leakage_alert, leakage_threshold)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", project_costs)

    # ── Follow-ups (3) ──
    followups = [
        (2, '2026-11-02', 'Vikram Solar Rep', 'Commercial Feasibility Review', 'Discuss 50kW industrial rooftop proposal.', 'High', 'Pending'),
        (3, '2026-11-03', 'Aisha Khan', 'Hybrid System Consultation', 'Finalize BYD battery backup sizing.', 'Medium', 'Scheduled'),
        (5, '2026-11-04', 'Vikram Solar Rep', 'Residential Proposal Follow-up', 'Answer net-metering approval questions.', 'Normal', 'Open'),
    ]
    db.executemany("INSERT INTO followups (customer_id, date, sales_rep, type, summary, priority, status) VALUES (?,?,?,?,?,?,?)", followups)

    db.commit()
    db.close()
    print("  ✅ Demo data seeded: 10 customers, 10 leads, 3 surveys, 3 packages, 2 orders, 8 stock lots, 1 installation, 2 warranties")


# ══════════════════════════════════════════════════════════════════════
# BUSINESS LOGIC HELPERS
# ══════════════════════════════════════════════════════════════════════

def calculate_recommended_capacity(monthly_kwh, roof_area_sqft, sanctioned_load_kw):
    """Calculate recommended solar capacity (kW) based on consumption, roof, and load."""
    capacity_by_kwh = monthly_kwh / 120.0
    capacity_by_roof = roof_area_sqft / 90.0
    rec = min(capacity_by_kwh, capacity_by_roof)
    if sanctioned_load_kw > 0 and rec > sanctioned_load_kw:
        rec = sanctioned_load_kw
    return round(rec, 2)


def calculate_feasibility_score(roof_area_sqft, monthly_kwh):
    """Calculate site feasibility score (0-100)."""
    score = 100
    if roof_area_sqft < 450:
        score -= 15
    if monthly_kwh < 200:
        score -= 20
    return max(score, 0)


def calculate_auto_bom(system_kw, cable_distance_m=20):
    """Generate automatic Bill of Materials for a given system size."""
    total_watts = system_kw * 1000
    panel_wattage = 550
    panel_count = math.ceil(total_watts / panel_wattage)
    inverter_kw = round(system_kw * 1.0, 2)
    cable_length = cable_distance_m * 2 + 10
    return {
        'panel_count': panel_count,
        'panel_wattage': panel_wattage,
        'inverter_kw': inverter_kw,
        'cable_length_m': cable_length,
        'mounting_slots': panel_count,
    }


def calculate_subsidy(system_kw):
    """PM Surya Ghar subsidy calculation in INR for rooftop solar systems.

    Structure: up to 2 kW -> ₹30,000/kW, 2-3 kW -> ₹18,000/kW for additional capacity,
    capped at ₹78,000 for 3 kW and above.
    """
    if system_kw is None:
        return 0.0
    cap = max(float(system_kw), 0.0)
    if cap <= 2.0:
        return cap * 30000.0
    if cap <= 3.0:
        return 60000.0 + (cap - 2.0) * 18000.0
    return 78000.0


def calculate_readiness_score(survey_approved, payment_ok, stock_available, equipment_allocated, technician_assigned):
    """Calculate Installation Readiness Score (0-100)."""
    score = 0
    if survey_approved:
        score += 20
    if payment_ok:
        score += 20
    if stock_available:
        score += 20
    if equipment_allocated:
        score += 20
    if technician_assigned:
        score += 20

    if score >= 80:
        label = 'Ready for Execution'
    elif score >= 40:
        label = 'Partially Ready'
    else:
        label = 'Not Ready'
    return score, label


def generate_warranty_token(ref, customer_id, serial, equip_type, start_date):
    """Generate SHA-256 warranty verification token."""
    data = f"{ref}|{customer_id}|{serial}|{equip_type}|{start_date}"
    return hashlib.sha256(data.encode()).hexdigest()


def calculate_project_cost(revenue, material, labour, transport, additional, other, threshold=10.0):
    """Calculate project costing with profit leakage detection."""
    total_cost = material + labour + transport + additional + other
    gross_profit = revenue - total_cost
    margin = (gross_profit / revenue * 100) if revenue > 0 else 0

    if margin >= 20:
        health = 'healthy'
    elif margin >= 10:
        health = 'moderate'
    else:
        health = 'critical'

    leakage = 1 if (margin < threshold) else 0
    return {
        'total_cost': round(total_cost, 2),
        'gross_profit': round(gross_profit, 2),
        'gross_margin_percent': round(margin, 2),
        'margin_health': health,
        'leakage_alert': leakage,
    }


def get_next_ref(prefix, table, field='ref'):
    """Generate next sequential reference number."""
    result = query_db(f"SELECT {field} FROM {table} ORDER BY id DESC LIMIT 1", one=True)
    if result and result[field]:
        parts = result[field].split('/')
        try:
            num = int(parts[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    year = datetime.now().year
    return f"{prefix}/{year}/{num:04d}"


# ══════════════════════════════════════════════════════════════════════
# AUTHENTICATION & RBAC
# ══════════════════════════════════════════════════════════════════════

# Role permissions map
ROLE_PERMISSIONS = {
    'admin': ['all'],
    'sales': ['dashboard', 'enquiries', 'leads', 'followups', 'surveys', 'quotations', 'orders', 'installations', 'packages'],
    'survey_tech': ['dashboard', 'surveys'],
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


# ══════════════════════════════════════════════════════════════════════
# ROUTES: FRONTEND SERVING
# ══════════════════════════════════════════════════════════════════════

@app.route('/')
def serve_index():
    """Serve the main frontend page."""
    return send_from_directory('web_app', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static frontend assets (CSS, JS)."""
    return send_from_directory('web_app', filename)


# ══════════════════════════════════════════════════════════════════════
# ROUTES: AUTHENTICATION
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/auth/login', methods=['POST'])
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


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Clear user session."""
    session.clear()
    return jsonify({'message': 'Logged out successfully.'})


@app.route('/api/auth/me', methods=['GET'])
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


# ══════════════════════════════════════════════════════════════════════
# ROUTES: DASHBOARD KPIs
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    """Return real-time dashboard KPIs computed from database."""
    total_leads = query_db("SELECT COUNT(*) as c FROM leads", one=True)['c']
    active_leads = query_db("SELECT COUNT(*) as c FROM leads WHERE status NOT IN ('rejected')", one=True)['c']
    total_surveys = query_db("SELECT COUNT(*) as c FROM surveys", one=True)['c']
    approved_surveys = query_db("SELECT COUNT(*) as c FROM surveys WHERE state = 'approved'", one=True)['c']
    total_orders = query_db("SELECT COUNT(*) as c FROM orders", one=True)['c']
    confirmed_orders = query_db("SELECT COUNT(*) as c FROM orders WHERE status = 'confirmed'", one=True)['c']
    total_installations = query_db("SELECT COUNT(*) as c FROM installations", one=True)['c']
    completed_installations = query_db("SELECT COUNT(*) as c FROM installations WHERE state = 'completed'", one=True)['c']
    total_warranties = query_db("SELECT COUNT(*) as c FROM warranties", one=True)['c']
    active_tickets = query_db("SELECT COUNT(*) as c FROM service_tickets WHERE status != 'resolved'", one=True)['c']
    total_capacity = query_db("SELECT COALESCE(SUM(sized_kw), 0) as c FROM leads", one=True)['c']
    total_revenue = query_db("SELECT COALESCE(SUM(revenue), 0) as c FROM project_costs", one=True)['c']
    avg_margin = query_db("SELECT COALESCE(AVG(gross_margin_percent), 0) as c FROM project_costs", one=True)['c']
    stock_available = query_db("SELECT COUNT(*) as c FROM stock_lots WHERE status = 'available'", one=True)['c']
    stock_allocated = query_db("SELECT COUNT(*) as c FROM stock_lots WHERE status = 'allocated'", one=True)['c']

    return jsonify({
        'total_leads': total_leads,
        'active_leads': active_leads,
        'total_surveys': total_surveys,
        'approved_surveys': approved_surveys,
        'total_orders': total_orders,
        'confirmed_orders': confirmed_orders,
        'total_installations': total_installations,
        'completed_installations': completed_installations,
        'total_warranties': total_warranties,
        'active_tickets': active_tickets,
        'total_pipeline_kw': round(total_capacity, 1),
        'total_revenue': round(total_revenue, 2),
        'avg_gross_margin': round(avg_margin, 2),
        'stock_available': stock_available,
        'stock_allocated': stock_allocated,
    })


# ══════════════════════════════════════════════════════════════════════
# ROUTES: CUSTOMERS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(query_db("SELECT * FROM customers ORDER BY id"))


@app.route('/api/customers/<int:cid>', methods=['GET'])
def get_customer(cid):
    c = query_db("SELECT * FROM customers WHERE id = ?", [cid], one=True)
    return jsonify(c) if c else (jsonify({'error': 'Not found'}), 404)


@app.route('/api/customers', methods=['POST'])
def create_customer():
    d = request.get_json()
    cid = execute_db("""INSERT INTO customers (name, phone, email, address, city, state, property_type, sanctioned_load_kw)
        VALUES (?,?,?,?,?,?,?,?)""",
        [d['name'], d.get('phone',''), d.get('email',''), d.get('address',''),
         d.get('city',''), d.get('state',''), d.get('property_type','Residential'), d.get('sanctioned_load_kw', 5.0)])
    return jsonify({'id': cid, 'message': 'Customer created'}), 201


# ══════════════════════════════════════════════════════════════════════
# ROUTES: ENQUIRIES
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    rows = query_db("""SELECT e.*, c.name as customer_name FROM enquiries e
        JOIN customers c ON e.customer_id = c.id ORDER BY e.id DESC""")
    return jsonify(rows)


@app.route('/api/enquiries', methods=['POST'])
def create_enquiry():
    d = request.get_json()
    ref = f"ENQ-{datetime.now().year}-{datetime.now().strftime('%m%d')}"
    eid = execute_db("""INSERT INTO enquiries (ref, customer_id, date, property_type, sanctioned_load, status)
        VALUES (?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('date', date.today().isoformat()),
         d.get('property_type',''), d.get('sanctioned_load',''), 'new'])
    return jsonify({'id': eid, 'ref': ref, 'message': 'Enquiry created'}), 201


# ══════════════════════════════════════════════════════════════════════
# ROUTES: LEADS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/leads', methods=['GET'])
def get_leads():
    rows = query_db("""SELECT l.*, c.name as customer_name, c.phone as customer_phone
        FROM leads l JOIN customers c ON l.customer_id = c.id ORDER BY l.id DESC""")
    return jsonify(rows)


@app.route('/api/leads/<int:lid>', methods=['GET'])
def get_lead(lid):
    row = query_db("""SELECT l.*, c.name as customer_name FROM leads l
        JOIN customers c ON l.customer_id = c.id WHERE l.id = ?""", [lid], one=True)
    return jsonify(row) if row else (jsonify({'error': 'Not found'}), 404)


@app.route('/api/leads', methods=['POST'])
def create_lead():
    d = request.get_json()
    ref = get_next_ref('SF/LEAD', 'leads')
    monthly_kwh = d.get('monthly_kwh', 300)
    roof_area = d.get('roof_area_sqft', 500)
    sanctioned = d.get('sanctioned_load_kw', 5.0)
    rec_kw = calculate_recommended_capacity(monthly_kwh, roof_area, sanctioned)
    feasibility = calculate_feasibility_score(roof_area, monthly_kwh)

    lid = execute_db("""INSERT INTO leads (ref, customer_id, monthly_kwh, tariff_rate, sized_kw,
        system_type, subsidy_required, roof_area_sqft, sanctioned_load_kw,
        recommended_kw, feasibility_score, status, lead_source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], monthly_kwh, d.get('tariff_rate', 0.10),
         d.get('sized_kw', rec_kw), d.get('system_type', 'on_grid'),
         d.get('subsidy_required', 1), roof_area, sanctioned,
         rec_kw, feasibility, 'draft', d.get('lead_source', 'web_inbound')])
    return jsonify({'id': lid, 'ref': ref, 'recommended_kw': rec_kw, 'feasibility_score': feasibility}), 201


@app.route('/api/leads/<int:lid>', methods=['PUT'])
def update_lead(lid):
    d = request.get_json()
    execute_db("UPDATE leads SET status=?, sized_kw=?, system_type=?, notes=? WHERE id=?",
        [d.get('status', 'draft'), d.get('sized_kw', 3.0), d.get('system_type', 'on_grid'), d.get('notes', ''), lid])
    return jsonify({'message': 'Lead updated'})


@app.route('/api/leads/<int:lid>/calculate', methods=['GET'])
def calculate_lead(lid):
    """Calculate recommended capacity and feasibility for a lead."""
    lead = query_db("SELECT * FROM leads WHERE id = ?", [lid], one=True)
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    rec_kw = calculate_recommended_capacity(lead['monthly_kwh'], lead['roof_area_sqft'], lead['sanctioned_load_kw'])
    feasibility = calculate_feasibility_score(lead['roof_area_sqft'], lead['monthly_kwh'])
    bom = calculate_auto_bom(rec_kw)
    subsidy = calculate_subsidy(rec_kw) if lead['subsidy_required'] else 0
    return jsonify({
        'recommended_kw': rec_kw,
        'feasibility_score': feasibility,
        'auto_bom': bom,
        'subsidy_amount': subsidy,
    })


# ══════════════════════════════════════════════════════════════════════
# ROUTES: FOLLOW-UPS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/followups', methods=['GET'])
def get_followups():
    rows = query_db("""SELECT f.*, c.name as customer_name FROM followups f
        JOIN customers c ON f.customer_id = c.id ORDER BY f.date""")
    return jsonify(rows)


@app.route('/api/followups', methods=['POST'])
def create_followup():
    d = request.get_json()
    fid = execute_db("""INSERT INTO followups (customer_id, date, sales_rep, type, summary, priority, status)
        VALUES (?,?,?,?,?,?,?)""",
        [d['customer_id'], d.get('date', date.today().isoformat()), d.get('sales_rep',''),
         d.get('type',''), d.get('summary',''), d.get('priority','Normal'), 'Pending'])
    return jsonify({'id': fid, 'message': 'Follow-up created'}), 201


# ══════════════════════════════════════════════════════════════════════
# ROUTES: SITE SURVEYS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/surveys', methods=['GET'])
def get_surveys():
    rows = query_db("""SELECT s.*, c.name as customer_name FROM surveys s
        JOIN customers c ON s.customer_id = c.id ORDER BY s.id DESC""")
    return jsonify(rows)


@app.route('/api/surveys/<int:sid>', methods=['GET'])
def get_survey(sid):
    row = query_db("""SELECT s.*, c.name as customer_name FROM surveys s
        JOIN customers c ON s.customer_id = c.id WHERE s.id = ?""", [sid], one=True)
    return jsonify(row) if row else (jsonify({'error': 'Not found'}), 404)


@app.route('/api/surveys', methods=['POST'])
def create_survey():
    d = request.get_json()
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


@app.route('/api/surveys/<int:sid>/approve', methods=['POST'])
def approve_survey(sid):
    execute_db("UPDATE surveys SET state = 'approved' WHERE id = ? AND state IN ('draft','submitted')", [sid])
    return jsonify({'message': 'Survey approved'})


@app.route('/api/surveys/<int:sid>/reject', methods=['POST'])
def reject_survey(sid):
    d = request.get_json()
    execute_db("UPDATE surveys SET state = 'rejected', rejection_reason = ? WHERE id = ?",
        [d.get('reason', 'No reason provided'), sid])
    return jsonify({'message': 'Survey rejected'})


# ══════════════════════════════════════════════════════════════════════
# ROUTES: SOLAR PACKAGES
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/packages', methods=['GET'])
def get_packages():
    packages = query_db("SELECT * FROM packages WHERE is_active = 1 ORDER BY capacity_kw")
    for pkg in packages:
        pkg['bom'] = query_db("SELECT * FROM package_lines WHERE package_id = ?", [pkg['id']])
    return jsonify(packages)


@app.route('/api/packages/<int:pid>', methods=['GET'])
def get_package(pid):
    pkg = query_db("SELECT * FROM packages WHERE id = ?", [pid], one=True)
    if not pkg:
        return jsonify({'error': 'Package not found'}), 404
    pkg['bom'] = query_db("SELECT * FROM package_lines WHERE package_id = ?", [pid])
    return jsonify(pkg)


@app.route('/api/bom/calculate', methods=['POST'])
def calculate_bom_api():
    """Calculate Auto-BOM for a given system size."""
    d = request.get_json()
    bom = calculate_auto_bom(d.get('system_kw', 3.0), d.get('cable_distance_m', 20))
    return jsonify(bom)


# ══════════════════════════════════════════════════════════════════════
# ROUTES: SALES ORDERS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/orders', methods=['GET'])
def get_orders():
    rows = query_db("""SELECT o.*, c.name as customer_name FROM orders o
        JOIN customers c ON o.customer_id = c.id ORDER BY o.id DESC""")
    return jsonify(rows)


@app.route('/api/orders/<int:oid>', methods=['GET'])
def get_order(oid):
    row = query_db("""SELECT o.*, c.name as customer_name FROM orders o
        JOIN customers c ON o.customer_id = c.id WHERE o.id = ?""", [oid], one=True)
    return jsonify(row) if row else (jsonify({'error': 'Not found'}), 404)


@app.route('/api/orders', methods=['POST'])
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
    subsidy = calculate_subsidy(system_kw) if d.get('subsidy', False) else 0
    net_price = pkg_price - subsidy

    oid = execute_db("""INSERT INTO orders (ref, customer_id, lead_id, survey_id, package_id,
        system_kw, system_type, package_price, subsidy_amount, net_price,
        amount_paid, payment_percent, dispatch_unlocked, status, order_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('lead_id'), d.get('survey_id'), d.get('package_id'),
         system_kw, d.get('system_type', 'on_grid'), pkg_price, subsidy, net_price,
         0, 0, 0, 'draft', date.today().isoformat()])
    return jsonify({'id': oid, 'ref': ref, 'net_price': net_price}), 201


@app.route('/api/orders/<int:oid>/payment', methods=['POST'])
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


@app.route('/api/orders/<int:oid>/confirm', methods=['POST'])
def confirm_order(oid):
    execute_db("UPDATE orders SET status = 'confirmed' WHERE id = ? AND status = 'draft'", [oid])
    return jsonify({'message': 'Order confirmed'})


# ══════════════════════════════════════════════════════════════════════
# ROUTES: STOCK / INVENTORY
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/stock', methods=['GET'])
def get_stock():
    status_filter = request.args.get('status', None)
    if status_filter:
        rows = query_db("SELECT * FROM stock_lots WHERE status = ? ORDER BY id", [status_filter])
    else:
        rows = query_db("SELECT * FROM stock_lots ORDER BY id")
    return jsonify(rows)


@app.route('/api/stock', methods=['POST'])
def create_stock_lot():
    d = request.get_json()
    sid = execute_db("""INSERT INTO stock_lots (serial_number, product_name, category, status, warehouse, received_date)
        VALUES (?,?,?,?,?,?)""",
        [d['serial_number'], d['product_name'], d.get('category','pv_module'),
         'available', d.get('warehouse','Main Warehouse'), date.today().isoformat()])
    return jsonify({'id': sid, 'message': 'Stock lot created'}), 201


@app.route('/api/stock/<int:sid>/allocate', methods=['POST'])
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
# ROUTES: INSTALLATIONS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/installations', methods=['GET'])
def get_installations():
    rows = query_db("""SELECT i.*, c.name as customer_name FROM installations i
        JOIN customers c ON i.customer_id = c.id ORDER BY i.id DESC""")
    return jsonify(rows)


@app.route('/api/installations/<int:iid>', methods=['GET'])
def get_installation(iid):
    row = query_db("""SELECT i.*, c.name as customer_name FROM installations i
        JOIN customers c ON i.customer_id = c.id WHERE i.id = ?""", [iid], one=True)
    if not row:
        return jsonify({'error': 'Not found'}), 404
    # Get assigned serials
    serials = query_db("SELECT * FROM stock_lots WHERE allocated_to_installation = ?", [iid])
    row['serials'] = serials
    return jsonify(row)


@app.route('/api/installations', methods=['POST'])
def create_installation():
    d = request.get_json()
    ref = get_next_ref('SF/INST', 'installations')

    # Calculate readiness score
    survey = query_db("SELECT * FROM surveys WHERE id = ?", [d.get('survey_id', 0)], one=True)
    order = query_db("SELECT * FROM orders WHERE id = ?", [d.get('order_id', 0)], one=True)
    survey_ok = survey and survey['state'] == 'approved' if survey else False
    payment_ok = order and order['dispatch_unlocked'] if order else False

    score, label = calculate_readiness_score(survey_ok, payment_ok, False, False, bool(d.get('technician')))

    iid = execute_db("""INSERT INTO installations (ref, customer_id, order_id, survey_id, package_id,
        capacity_kw, system_type, scheduled_date, technician, state,
        readiness_score, readiness_label)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('order_id'), d.get('survey_id'), d.get('package_id'),
         d.get('capacity_kw', 3.0), d.get('system_type', 'on_grid'),
         d.get('scheduled_date', ''), d.get('technician', ''), 'draft', score, label])
    return jsonify({'id': iid, 'ref': ref, 'readiness_score': score, 'readiness_label': label}), 201


@app.route('/api/installations/<int:iid>/phase', methods=['POST'])
def update_phase(iid):
    """Update installation phase milestone and recalculate completion %."""
    d = request.get_json()
    phase = d.get('phase', '')
    value = 1 if d.get('completed', True) else 0

    valid_phases = ['phase_1_structure', 'phase_2_modules', 'phase_3_inverter',
                    'phase_4_earthing', 'phase_5_testing', 'phase_6_signoff']
    if phase not in valid_phases:
        return jsonify({'error': f'Invalid phase. Must be one of: {valid_phases}'}), 400

    execute_db(f"UPDATE installations SET {phase} = ? WHERE id = ?", [value, iid])

    # Recalculate completion %
    inst = query_db("SELECT * FROM installations WHERE id = ?", [iid], one=True)
    phases_done = sum([inst[p] for p in valid_phases])
    pct = round((phases_done / 6) * 100, 1)
    state = 'completed' if phases_done == 6 else ('in_progress' if phases_done > 0 else 'draft')

    execute_db("UPDATE installations SET completion_percent = ?, state = ? WHERE id = ?", [pct, state, iid])
    return jsonify({'completion_percent': pct, 'state': state, 'phases_completed': phases_done})


@app.route('/api/installations/<int:iid>/qc', methods=['POST'])
def submit_qc(iid):
    """Submit electrical QC test results."""
    d = request.get_json()
    voc = d.get('voc', 0)
    isc = d.get('isc', 0)
    earth = d.get('earth_ohm', 0)

    # QC validation: Voc > 0, Isc > 0, Earth ≤ 5.0 Ω
    qc_passed = 1 if (voc > 0 and isc > 0 and earth <= 5.0) else 0
    state = 'testing' if not qc_passed else 'completed'

    execute_db("""UPDATE installations SET qc_voc = ?, qc_isc = ?, qc_earth_ohm = ?,
        qc_passed = ?, state = ? WHERE id = ?""", [voc, isc, earth, qc_passed, state, iid])

    if qc_passed:
        msg = f'✅ QC PASSED — Voc={voc}V, Isc={isc}A, Earth={earth}Ω (≤5.0Ω)'
    else:
        failures = []
        if voc <= 0: failures.append(f'Voc={voc}V (must be >0)')
        if isc <= 0: failures.append(f'Isc={isc}A (must be >0)')
        if earth > 5.0: failures.append(f'Earth={earth}Ω (must be ≤5.0Ω)')
        msg = f'❌ QC FAILED — {", ".join(failures)}'

    return jsonify({'qc_passed': bool(qc_passed), 'message': msg})


@app.route('/api/installations/<int:iid>/readiness', methods=['GET'])
def get_readiness(iid):
    """Calculate and return Installation Readiness Score."""
    inst = query_db("SELECT * FROM installations WHERE id = ?", [iid], one=True)
    if not inst:
        return jsonify({'error': 'Not found'}), 404

    survey_ok = False
    if inst['survey_id']:
        survey = query_db("SELECT state FROM surveys WHERE id = ?", [inst['survey_id']], one=True)
        survey_ok = survey and survey['state'] == 'approved'

    payment_ok = False
    if inst['order_id']:
        order = query_db("SELECT dispatch_unlocked FROM orders WHERE id = ?", [inst['order_id']], one=True)
        payment_ok = order and order['dispatch_unlocked']

    stock_count = query_db("SELECT COUNT(*) as c FROM stock_lots WHERE allocated_to_installation = ?", [iid], one=True)['c']
    stock_ok = stock_count > 0
    equipment_ok = stock_ok
    tech_ok = bool(inst['technician'])

    score, label = calculate_readiness_score(survey_ok, payment_ok, stock_ok, equipment_ok, tech_ok)
    execute_db("UPDATE installations SET readiness_score = ?, readiness_label = ? WHERE id = ?", [score, label, iid])

    return jsonify({
        'readiness_score': score,
        'readiness_label': label,
        'breakdown': {
            'survey_approved': {'value': survey_ok, 'points': 20 if survey_ok else 0},
            'payment_50_percent': {'value': payment_ok, 'points': 20 if payment_ok else 0},
            'stock_available': {'value': stock_ok, 'points': 20 if stock_ok else 0},
            'equipment_allocated': {'value': equipment_ok, 'points': 20 if equipment_ok else 0},
            'technician_assigned': {'value': tech_ok, 'points': 20 if tech_ok else 0},
        }
    })


# ══════════════════════════════════════════════════════════════════════
# ROUTES: WARRANTIES
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/warranties', methods=['GET'])
def get_warranties():
    rows = query_db("""SELECT w.*, c.name as customer_name FROM warranties w
        JOIN customers c ON w.customer_id = c.id ORDER BY w.id DESC""")
    return jsonify(rows)


@app.route('/api/warranties', methods=['POST'])
def create_warranty():
    d = request.get_json()
    ref = get_next_ref('SF/WTY', 'warranties')
    equip_type = d.get('equipment_type', 'pv_module')

    # Warranty duration by type
    years_map = {'pv_module': 25, 'inverter': 10, 'battery': 5}
    years = years_map.get(equip_type, 5)

    start = d.get('start_date', date.today().isoformat())
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    expiry = (start_dt + timedelta(days=years * 365)).strftime('%Y-%m-%d')

    token = generate_warranty_token(ref, d['customer_id'], d.get('serial_number', ''), equip_type, start)

    # Duplicate check
    existing = query_db("SELECT id FROM warranties WHERE serial_number = ? AND equipment_type = ? AND status = 'active'",
        [d.get('serial_number',''), equip_type], one=True)
    if existing:
        return jsonify({'error': f'Duplicate warranty: An active warranty already exists for serial {d.get("serial_number")}'}), 400

    wid = execute_db("""INSERT INTO warranties (ref, customer_id, installation_id, serial_number,
        equipment_type, warranty_years, start_date, expiry_date, sha256_token, status)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('installation_id'), d.get('serial_number',''),
         equip_type, years, start, expiry, token, 'active'])
    return jsonify({'id': wid, 'ref': ref, 'expiry_date': expiry, 'sha256_token': token, 'warranty_years': years}), 201


@app.route('/api/warranties/<int:wid>/verify', methods=['GET'])
def verify_warranty(wid):
    """Verify warranty token and check expiry status."""
    w = query_db("SELECT * FROM warranties WHERE id = ?", [wid], one=True)
    if not w:
        return jsonify({'error': 'Warranty not found'}), 404

    expected_token = generate_warranty_token(w['ref'], w['customer_id'], w['serial_number'], w['equipment_type'], w['start_date'])
    token_valid = (w['sha256_token'] == expected_token)

    today = date.today().isoformat()
    is_expired = today > w['expiry_date'] if w['expiry_date'] else False

    return jsonify({
        'warranty': w,
        'token_valid': token_valid,
        'is_expired': is_expired,
        'status': 'expired' if is_expired else w['status'],
    })


# ══════════════════════════════════════════════════════════════════════
# ROUTES: SERVICE TICKETS
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/service-tickets', methods=['GET'])
def get_tickets():
    rows = query_db("""SELECT t.*, c.name as customer_name FROM service_tickets t
        JOIN customers c ON t.customer_id = c.id ORDER BY t.id DESC""")
    return jsonify(rows)


@app.route('/api/service-tickets', methods=['POST'])
def create_ticket():
    d = request.get_json()
    ref = get_next_ref('SF/SVC', 'service_tickets')

    # Auto-detect warranty coverage by serial number
    serial = d.get('serial_number', '')
    warranty = query_db("""SELECT * FROM warranties WHERE serial_number = ? AND status = 'active'
        AND expiry_date >= ?""", [serial, date.today().isoformat()], one=True)
    under_warranty = 1 if warranty else 0

    # If under warranty, cost is $0.00
    parts = 0 if under_warranty else d.get('parts_cost', 0)
    labour = 0 if under_warranty else d.get('labour_cost', 0)
    total = parts + labour

    tid = execute_db("""INSERT INTO service_tickets (ref, customer_id, installation_id, warranty_id,
        serial_number, issue_type, description, is_under_warranty,
        parts_cost, labour_cost, total_cost, status, priority, assigned_to)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d['customer_id'], d.get('installation_id'), warranty['id'] if warranty else None,
         serial, d.get('issue_type', 'general'), d.get('description', ''),
         under_warranty, parts, labour, total, 'open', d.get('priority', 'medium'),
         d.get('assigned_to', '')])
    return jsonify({
        'id': tid, 'ref': ref,
        'under_warranty': bool(under_warranty),
        'total_cost': total,
        'message': '✅ Covered under warranty — $0.00 charge' if under_warranty else f'Out of warranty — total cost: ${total}'
    }), 201


@app.route('/api/service-tickets/<int:tid>/resolve', methods=['POST'])
def resolve_ticket(tid):
    d = request.get_json()
    execute_db("""UPDATE service_tickets SET status = 'resolved', resolution = ?,
        resolved_at = ? WHERE id = ?""", [d.get('resolution', ''), datetime.now().isoformat(), tid])
    return jsonify({'message': 'Ticket resolved'})


# ══════════════════════════════════════════════════════════════════════
# ROUTES: PROJECT COSTING
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/costing', methods=['GET'])
def get_costs():
    rows = query_db("""SELECT pc.*, c.name as customer_name FROM project_costs pc
        LEFT JOIN customers c ON pc.customer_id = c.id ORDER BY pc.id DESC""")
    return jsonify(rows)


@app.route('/api/costing', methods=['POST'])
def create_cost():
    d = request.get_json()
    ref = get_next_ref('SF/COST', 'project_costs')

    revenue = d.get('revenue', 0)
    material = d.get('material_cost', 0)
    labour = d.get('labour_cost', 0)
    transport = d.get('transport_cost', 0)
    additional = d.get('additional_cost', 0)
    other = d.get('other_cost', 0)
    threshold = d.get('leakage_threshold', 10.0)

    calc = calculate_project_cost(revenue, material, labour, transport, additional, other, threshold)

    cid = execute_db("""INSERT INTO project_costs (ref, installation_id, customer_id, order_id,
        revenue, material_cost, labour_cost, transport_cost, additional_cost, other_cost,
        total_cost, gross_profit, gross_margin_percent, margin_health, leakage_alert, leakage_threshold)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [ref, d.get('installation_id'), d.get('customer_id'), d.get('order_id'),
         revenue, material, labour, transport, additional, other,
         calc['total_cost'], calc['gross_profit'], calc['gross_margin_percent'],
         calc['margin_health'], calc['leakage_alert'], threshold])
    return jsonify({
        'id': cid, 'ref': ref,
        **calc,
        'message': '⚠️ PROFIT LEAKAGE ALERT — margin below threshold!' if calc['leakage_alert'] else '✅ Margin healthy'
    }), 201


# ══════════════════════════════════════════════════════════════════════
# ROUTES: HEALTH CHECK
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'system': 'SolarFlow ERP – Flask Backend',
        'version': '1.0.0',
        'database': 'SQLite',
        'timestamp': datetime.now().isoformat(),
    })


# ══════════════════════════════════════════════════════════════════════
# APPLICATION STARTUP
# ══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("  SolarFlow ERP – Flask Backend Server")
    print("=" * 60)
    print()

    # Initialize database
    print("  📦 Initializing database...")
    init_db()

    # Seed demo data
    print("  🌱 Seeding demo data...")
    seed_demo_data()

    print()
    print("  🌐 Server starting on: http://localhost:5000")
    print("  📊 API documentation:   http://localhost:5000/api/health")
    print("  🖥️  Frontend:            http://localhost:5000")
    print()
    print("  Login Credentials:")
    print("  ─────────────────────────────────────────")
    print("  admin    / admin123      (Super Administrator)")
    print("  sales    / sales123      (Sales Manager)")
    print("  survey   / survey123     (Survey Technician)")
    print("  warehouse/ warehouse123  (Warehouse Manager)")
    print("  tech     / tech123       (Installation Technician)")
    print("  support  / support123    (Support Manager)")
    print("  director / director123   (Managing Director)")
    print("  finance  / finance123    (Finance Controller)")
    print("  ─────────────────────────────────────────")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)

