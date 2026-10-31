# -*- coding: utf-8 -*-
"""SolarFlow ERP - Demo Data Seeder."""
import sqlite3
import hashlib
from server.config import DATABASE

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
    print("  [OK] Demo data seeded: 10 customers, 10 leads, 3 surveys, 3 packages, 2 orders, 8 stock lots, 1 installation, 2 warranties")
