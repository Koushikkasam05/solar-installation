# -*- coding: utf-8 -*-
"""SolarFlow ERP - Demo Data Seeder with Rich Enterprise Fixtures."""
import sqlite3
import hashlib
from datetime import datetime, date
from server.config import DATABASE

def seed_demo_data():
    """Populate database with realistic enterprise demo data."""
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()

    # ── Users (7 core roles) ──
    users = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'System Administrator', 'admin@solarflow.erp', 'admin', 'Chief Executive Officer'),
        ('sales', hashlib.sha256('sales123'.encode()).hexdigest(), 'Vikram Sales Manager', 'sales@solarflow.erp', 'sales', 'Head of Solar Sales'),
        ('warehouse', hashlib.sha256('warehouse123'.encode()).hexdigest(), 'Sanjay Warehouse Manager', 'warehouse@solarflow.erp', 'warehouse', 'Supply Chain Lead'),
        ('tech', hashlib.sha256('tech123'.encode()).hexdigest(), 'Ramesh Electrician', 'tech@solarflow.erp', 'technician', 'Senior Electrical Lead'),
        ('support', hashlib.sha256('support123'.encode()).hexdigest(), 'Neha Support Manager', 'support@solarflow.erp', 'support', 'After-Sales & Warranty Lead'),
        ('director', hashlib.sha256('director123'.encode()).hexdigest(), 'Aditya Director', 'director@solarflow.erp', 'director', 'Board Director (Read-Only)'),
        ('finance', hashlib.sha256('finance123'.encode()).hexdigest(), 'Kavita Finance Manager', 'finance@solarflow.erp', 'finance', 'Finance Controller'),
    ]
    for u in users:
        cur.execute("INSERT OR IGNORE INTO users (username, password_hash, full_name, email, role, title) VALUES (?,?,?,?,?,?)", u)

    # ── Customers (10) ──
    customers = [
        (1, 'Dr. Rajesh Sharma', '+91 98765 43210', 'rajesh@email.com', '42 Palm Meadows, Whitefield', 'Bengaluru', 'Karnataka', 'Residential', 5.0),
        (2, 'GreenTech Logistics Pvt Ltd', '+91 80 4567 8901', 'ops@greentech.in', 'Industrial Area Phase II', 'Hyderabad', 'Telangana', 'Industrial', 60.0),
        (3, 'Mrs. Sunita Kapoor', '+91 99887 65432', 'sunita@email.com', '15 Harmony Villas, Jubilee Hills', 'Hyderabad', 'Telangana', 'Residential', 7.0),
        (4, 'Mr. Arvind Patel', '+91 94567 12345', 'arvind@email.com', '88 Lake View Colony', 'Ahmedabad', 'Gujarat', 'Residential', 5.0),
        (5, 'Sunrise Apartments Association', '+91 44 2345 6789', 'rwa@sunrise.in', 'Sunrise Towers, OMR Road', 'Chennai', 'Tamil Nadu', 'Commercial', 12.0),
        (6, 'FreshCold Storage Pvt Ltd', '+91 22 8765 4321', 'facility@freshcold.in', 'MIDC Bhosari Complex', 'Pune', 'Maharashtra', 'Industrial', 100.0),
        (7, 'Mr. Deepak Verma', '+91 87654 32100', 'deepak@email.com', '5 Tin Shed Lane, Old City', 'Jaipur', 'Rajasthan', 'Residential', 3.0),
        (8, 'MegaMart Retail Chain', '+91 11 5678 9012', 'energy@megamart.in', 'Sector 62 Business Park', 'Noida', 'UP', 'Commercial', 150.0),
        (9, 'Mrs. Lakshmi Nair', '+91 97531 24680', 'lakshmi@email.com', '22 Coconut Grove, Vyttila', 'Kochi', 'Kerala', 'Residential', 4.0),
        (10, 'TechPark Innovation Hub', '+91 80 9876 5432', 'infra@techpark.in', 'Electronic City Phase I', 'Bengaluru', 'Karnataka', 'Commercial', 80.0),
    ]
    for c in customers:
        cur.execute("INSERT OR IGNORE INTO customers (id, name, phone, email, address, city, state, property_type, sanctioned_load_kw) VALUES (?,?,?,?,?,?,?,?,?)", c)

    # ── Enquiries (4) ──
    enquiries = [
        ('ENQ-2026-0101', 1, '2026-10-25', 'RCC Rooftop', '5.0 kW', 'qualified'),
        ('ENQ-2026-0102', 2, '2026-10-26', 'Metal Industrial Shed', '60.0 kW', 'new'),
        ('ENQ-2026-0103', 3, '2026-10-28', 'Terrace Villa', '7.0 kW', 'qualified'),
        ('ENQ-2026-0104', 5, '2026-10-30', 'Independent House', '12.0 kW', 'new'),
    ]
    for e in enquiries:
        cur.execute("INSERT OR IGNORE INTO enquiries (ref, customer_id, date, property_type, sanctioned_load, status) VALUES (?,?,?,?,?,?)", e)

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
    for l in leads:
        cur.execute("""INSERT OR IGNORE INTO leads (ref, customer_id, monthly_kwh, tariff_rate, sized_kw, system_type,
            subsidy_required, roof_area_sqft, sanctioned_load_kw, status, lead_source) VALUES (?,?,?,?,?,?,?,?,?,?,?)""", l)

    # ── Surveys (5) ──
    surveys = [
        ('SRV-2026-0001', 1, 1, 'RCC Flat Concrete', '650 sq.ft', '500 sq.ft', '180° South (Optimal)', '12°', 20, 'Single Phase 230V', 3.0, 'approved', 'Arun K. (Chief Engineer)', '', 'Rooftop is flat RCC with zero shading. Excellent structural load capacity.', '2026-10-20'),
        ('SRV-2026-0002', 3, 3, 'RCC Flat Terrace', '900 sq.ft', '700 sq.ft', '210° South-West', '15°', 25, 'Three Phase 415V', 5.0, 'scheduled', 'Pending Assignment', '', 'Scheduled shadow analysis and parapet height check.', '2026-11-05'),
        ('SRV-2026-0003', 7, 7, 'Asbestos Tin Shed', '350 sq.ft', '120 sq.ft', '0° North (Low Yield)', '25°', 55, 'Single Phase', 1.0, 'rejected', 'Arun K. (Chief Engineer)', 'Severe structural weakness in corrugated tin roof.', 'Infeasible for elevated module mounting.', '2026-10-18'),
        ('SRV-2026-0004', 5, 5, 'Reinforced Concrete Rooftop', '2200 sq.ft', '1800 sq.ft', '180° South', '14°', 35, 'Three Phase 415V', 10.0, 'approved', 'Arun K. (Chief Engineer)', '', 'Elevated GI super structure required for rainwater gutter clearance.', '2026-10-22'),
        ('SRV-2026-0005', 2, 2, 'Standing Seam Metal Roof', '5500 sq.ft', '4800 sq.ft', '175° South', '10°', 45, 'Three Phase 415V', 50.0, 'draft', 'Arun K. (Chief Engineer)', '', 'Non-penetrating clamp mounting approved.', '2026-10-28'),
    ]
    for s in surveys:
        cur.execute("""INSERT OR IGNORE INTO surveys (ref, customer_id, lead_id, roof_type, total_area, usable_area,
            azimuth, tilt, cable_distance_m, grid_phase, recommended_kw, state, engineer, rejection_reason, notes, survey_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", s)

    # ── Packages (4) ──
    packages = [
        (1, 'SF-PKG-3KW-OG', '3kW On-Grid Solar Package', 3.0, 'on_grid', 1770),
        (2, 'SF-PKG-5KW-HYB', '5kW Smart Hybrid Solar Package', 5.0, 'hybrid', 4530),
        (3, 'SF-PKG-5KW-OG', '5kW On-Grid Solar Package', 5.0, 'on_grid', 2850),
        (4, 'SF-PKG-10KW-COM', '10kW Commercial Three-Phase Package', 10.0, 'on_grid', 5600),
    ]
    for p in packages:
        cur.execute("INSERT OR IGNORE INTO packages (id, code, name, capacity_kw, system_type, total_price) VALUES (?,?,?,?,?,?)", p)

    bom_lines = [
        (1, 'Canadian Solar 550W Mono PERC Modules', 'panel', 6, 154, 924),
        (1, 'Growatt 3kW Dual MPPT Grid-Tie Inverter', 'inverter', 1, 580, 580),
        (1, 'Elevated HDGI Mounting Structure Rails', 'structure', 6, 26, 156),
        (1, 'Class II ACDB/DCDB, SPDs & DC Cables', 'electrical', 1, 110, 110),
        (2, 'Canadian Solar 550W Mono PERC Modules', 'panel', 10, 154, 1540),
        (2, 'Deye 5kW Hybrid Inverter with EMS', 'inverter', 1, 1150, 1150),
        (2, 'BYD LiFePO4 48V 100Ah Battery Bank (5kWh)', 'battery', 1, 1400, 1400),
        (2, 'Elevated HDGI Mounting Structure', 'structure', 10, 26, 260),
        (2, 'IP65 Hybrid ACDB/DCDB & Safety Kit', 'electrical', 1, 180, 180),
        (3, 'Canadian Solar 550W Mono PERC Modules', 'panel', 10, 154, 1540),
        (3, 'Growatt 5kW Dual MPPT Grid-Tie Inverter', 'inverter', 1, 850, 850),
        (3, 'Elevated HDGI Mounting Structure Rails', 'structure', 10, 26, 260),
        (3, 'Class II ACDB/DCDB, SPDs & DC Cables', 'electrical', 1, 200, 200),
        (4, 'Canadian Solar 550W Mono PERC Modules', 'panel', 20, 154, 3080),
        (4, 'Growatt 10kW Three-Phase Inverter', 'inverter', 1, 1450, 1450),
        (4, 'Heavy-Duty Ballasted Racking System', 'structure', 20, 32, 640),
        (4, 'Three Phase IP65 Distribution Panel', 'electrical', 1, 430, 430),
    ]
    cur.execute("DELETE FROM package_lines")
    cur.executemany("INSERT INTO package_lines (package_id, item_name, category, quantity, unit_price, subtotal) VALUES (?,?,?,?,?,?)", bom_lines)

    # ── Sales Orders / Quotations (4) ──
    orders = [
        ('SF/SO/2026/0001', 1, 1, 1, 1, 3.0, 'on_grid', 1770, 468, 1302, 1302, 100.0, 1, 'confirmed', '2026-10-22'),
        ('SF/SO/2026/0002', 3, 3, 2, 2, 5.0, 'hybrid', 4530, 0, 4530, 2265, 50.0, 1, 'confirmed', '2026-10-25'),
        ('SF/SO/2026/0003', 5, 5, 4, 4, 10.0, 'on_grid', 5600, 936, 4664, 2332, 50.0, 1, 'confirmed', '2026-10-27'),
        ('SF/SO/2026/0004', 2, 2, 5, 4, 50.0, 'on_grid', 26500, 0, 26500, 0, 0.0, 0, 'draft', '2026-10-30'),
    ]
    for o in orders:
        cur.execute("""INSERT OR IGNORE INTO orders (ref, customer_id, lead_id, survey_id, package_id, system_kw, system_type,
            package_price, subsidy_amount, net_price, amount_paid, payment_percent, dispatch_unlocked, status, order_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", o)

    # ── Stock Lots (12) ──
    stock_lots = [
        ('CS550-2026-A001', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A002', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A003', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A004', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A005', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('CS550-2026-A006', 'Canadian Solar 550W Module', 'pv_module', 'allocated', 'Main Warehouse', 1, 1, '2026-10-15'),
        ('GRW3K-2026-INV01', 'Growatt 3kW Grid-Tie Inverter', 'inverter', 'allocated', 'Main Warehouse', 1, 1, '2026-10-16'),
        ('DEYE5K-2026-INV02', 'Deye 5kW Hybrid Inverter', 'inverter', 'allocated', 'Main Warehouse', 2, 2, '2026-10-18'),
        ('BYD5K-2026-BAT01', 'BYD LiFePO4 5kWh Battery Bank', 'battery', 'allocated', 'Main Warehouse', 2, 2, '2026-10-18'),
        ('CS550-2026-B001', 'Canadian Solar 550W Module', 'pv_module', 'available', 'Main Warehouse', None, None, '2026-10-20'),
        ('CS550-2026-B002', 'Canadian Solar 550W Module', 'pv_module', 'available', 'Main Warehouse', None, None, '2026-10-20'),
        ('GRW5K-2026-INV03', 'Growatt 5kW Grid-Tie Inverter', 'inverter', 'available', 'Main Warehouse', None, None, '2026-10-22'),
    ]
    for s in stock_lots:
        cur.execute("""INSERT OR IGNORE INTO stock_lots (serial_number, product_name, category, status, warehouse,
            allocated_to_order, allocated_to_installation, received_date) VALUES (?,?,?,?,?,?,?,?)""", s)

    # ── Installations (4) ──
    installations = [
        ('SF/INST/2026/0001', 1, 1, 1, 1, 3.0, 'on_grid', '2026-10-25', '2026-10-25', '2026-10-26',
         'Ramesh Electrician', 'Ramesh, Suresh, Mahesh', 'completed',
         1, 1, 1, 1, 1, 1, 100.0,
         38.5, 9.2, 2.4, 1,
         100, 'Ready for Execution',
         1, '2026-10-26', 'Flawless 3kW commissioning completed. Customer handover complete.'),
        ('SF/INST/2026/0002', 3, 2, 2, 2, 5.0, 'hybrid', '2026-10-28', '2026-10-28', '',
         'Ramesh Electrician', 'Ramesh, Dinesh', 'in_progress',
         1, 1, 1, 0, 0, 0, 60.0,
         0, 0, 0, 0,
         85, 'Execution Phase Active',
         0, '', 'Modules and Deye hybrid inverter mounted. Earthing pit excavation underway.'),
        ('SF/INST/2026/0003', 5, 3, 4, 4, 10.0, 'on_grid', '2026-11-02', '2026-11-02', '',
         'Ramesh Electrician', 'Ramesh, Suresh, Imran', 'in_progress',
         1, 0, 0, 0, 0, 0, 25.0,
         0, 0, 0, 0,
         80, 'Racking Stage',
         0, '', 'Elevated HDGI racking installed. Module lifting scheduled tomorrow.'),
        ('SF/INST/2026/0004', 2, 4, 5, 4, 50.0, 'on_grid', '2026-11-12', '', '',
         'Pending Assignment', '', 'scheduled',
         0, 0, 0, 0, 0, 0, 0.0,
         0, 0, 0, 0,
         60, 'Staging / Unallocated',
         0, '', 'Advance payment confirmed. Supply chain dispatch queued.'),
    ]
    for inst in installations:
        cur.execute("""INSERT OR IGNORE INTO installations (ref, customer_id, order_id, survey_id, package_id,
            capacity_kw, system_type, scheduled_date, start_date, completion_date,
            technician, crew_members, state,
            phase_1_structure, phase_2_modules, phase_3_inverter, phase_4_earthing, phase_5_testing, phase_6_signoff,
            completion_percent, qc_voc, qc_isc, qc_earth_ohm, qc_passed,
            readiness_score, readiness_label,
            customer_signoff, signoff_date, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", inst)

    # ── Warranties (4) ──
    token_1 = hashlib.sha256(b"SF/WTY/2026/0001|1|CS550-2026-A001|pv_module|2026-10-26").hexdigest()
    token_2 = hashlib.sha256(b"SF/WTY/2026/0002|1|GRW3K-2026-INV01|inverter|2026-10-26").hexdigest()
    token_3 = hashlib.sha256(b"SF/WTY/2026/0003|3|DEYE5K-2026-INV02|inverter|2026-10-30").hexdigest()
    token_4 = hashlib.sha256(b"SF/WTY/2026/0004|3|BYD5K-2026-BAT01|battery|2026-10-30").hexdigest()

    warranties = [
        ('SF/WTY/2026/0001', 1, 1, 'CS550-2026-A001', 'pv_module', 25, '2026-10-26', '2051-10-26', token_1, 'active'),
        ('SF/WTY/2026/0002', 1, 1, 'GRW3K-2026-INV01', 'inverter', 10, '2026-10-26', '2036-10-26', token_2, 'active'),
        ('SF/WTY/2026/0003', 3, 2, 'DEYE5K-2026-INV02', 'inverter', 10, '2026-10-30', '2036-10-30', token_3, 'active'),
        ('SF/WTY/2026/0004', 3, 2, 'BYD5K-2026-BAT01', 'battery', 5, '2026-10-30', '2031-10-30', token_4, 'active'),
    ]
    for w in warranties:
        cur.execute("""INSERT OR IGNORE INTO warranties (ref, customer_id, installation_id, serial_number,
            equipment_type, warranty_years, start_date, expiry_date, sha256_token, status)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", w)

    # ── Service Tickets (3) ──
    service_tickets = [
        ('SF/SVC/2026/0001', 1, 1, 2, 'GRW3K-2026-INV01', 'inverter_fault',
         'Inverter showing grid voltage fluctuation alarm code E-014.', 1,
         0, 0, 0, 'resolved', 'high', 'Ramesh Electrician',
         'Firmware update resolved alarm. Grid synchronization restored.', '2026-10-28'),
        ('SF/SVC/2026/0002', 3, 2, 3, 'DEYE5K-2026-INV02', 'wiring_check',
         'Verify RS485 communication cable between hybrid inverter and smart energy meter.', 1,
         0, 0, 0, 'open', 'medium', 'Ramesh Electrician',
         '', ''),
        ('SF/SVC/2026/0003', 5, 3, None, 'GEN-MTR-0091', 'net_metering',
         'DISCOM synchronization and inspection for bidirectional bidirectional generation meter.', 0,
         45, 30, 75, 'in_progress', 'high', 'Vikram Sales Manager',
         '', ''),
    ]
    for t in service_tickets:
        cur.execute("""INSERT OR IGNORE INTO service_tickets (ref, customer_id, installation_id, warranty_id,
            serial_number, issue_type, description, is_under_warranty,
            parts_cost, labour_cost, total_cost, status, priority, assigned_to,
            resolution, resolved_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", t)

    # ── Project Costing (4) ──
    project_costs = [
        ('SF/COST/2026/0001', 1, 1, 1, 2040, 1200, 200, 60, 30, 10, 1500, 540, 26.47, 'healthy', 0, 10.0),
        ('SF/COST/2026/0002', 2, 3, 2, 5200, 3200, 450, 120, 50, 30, 3850, 1350, 25.96, 'healthy', 0, 10.0),
        ('SF/COST/2026/0003', 3, 5, 3, 8900, 5400, 750, 200, 80, 40, 6470, 2430, 27.30, 'healthy', 0, 10.0),
        ('SF/COST/2026/0004', 4, 2, 4, 32150, 21500, 2400, 650, 350, 200, 25100, 7050, 21.93, 'healthy', 0, 10.0),
    ]
    for pc in project_costs:
        cur.execute("""INSERT OR IGNORE INTO project_costs (ref, installation_id, customer_id, order_id,
            revenue, material_cost, labour_cost, transport_cost, additional_cost, other_cost,
            total_cost, gross_profit, gross_margin_percent, margin_health, leakage_alert, leakage_threshold)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", pc)

    # ── Follow-ups (4) ──
    followups = [
        (2, '2026-11-02', 'Vikram Sales Manager', 'Commercial Feasibility Review', 'Discuss 50kW industrial rooftop proposal with GreenTech.', 'High', 'Pending'),
        (3, '2026-11-03', 'Vikram Sales Manager', 'Hybrid System Consultation', 'Confirm BYD battery backup runtime with Mrs. Kapoor.', 'Medium', 'Scheduled'),
        (5, '2026-11-04', 'Vikram Sales Manager', 'Residential Proposal Follow-up', 'Answer DISCOM net-metering approval questions.', 'Normal', 'Open'),
        (8, '2026-11-06', 'Vikram Sales Manager', 'Corporate EPC Pitch', 'Present 100kW rooftop ROI projection to MegaMart executive board.', 'Urgent', 'Open'),
    ]
    cur.execute("DELETE FROM followups")
    for f in followups:
        cur.execute("INSERT INTO followups (customer_id, date, sales_rep, type, summary, priority, status) VALUES (?,?,?,?,?,?,?)", f)

    db.commit()
    db.close()
    print("  [OK] Enterprise demo data seeded successfully.")
