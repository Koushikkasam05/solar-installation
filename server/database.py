# -*- coding: utf-8 -*-
"""SolarFlow ERP - Database Connection & SQLite Engine Layer."""
import sqlite3
from flask import g
from server.config import DATABASE

def get_db():
    """Get database connection for current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(exception=None):
    """Close connection at teardown."""
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
