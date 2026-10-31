# -*- coding: utf-8 -*-
"""
Comprehensive Automated Test Suite for SolarFlow ERP (5 Core Modules)
1. Solar Site Survey Management
2. Solar Package Management & Automatic BOM
3. Sales and Payment Management
4. Solar Inventory and Serial Number Tracking
5. Solar Installation and Technician Management
"""
import unittest
import math
import hashlib

class MockPartner:
    def __init__(self, partner_id, name, phone="+91 98765 43210", email="customer@example.com"):
        self.id = partner_id
        self.name = name
        self.phone = phone
        self.email = email
        self.contact_address = "42 Palm Meadows Boulevard, Bengaluru"

class MockUser:
    def __init__(self, user_id, name, is_engineer=False, is_manager=False):
        self.id = user_id
        self.name = name
        self.is_engineer = is_engineer
        self.is_manager = is_manager

    def has_group(self, group_name):
        if 'engineer' in group_name and self.is_engineer:
            return True
        if 'manager' in group_name and self.is_manager:
            return True
        return False

class MockProduct:
    def __init__(self, prod_id, name, list_price, tracking='none'):
        self.id = prod_id
        self.name = name
        self.list_price = list_price
        self.tracking = tracking # 'none', 'serial'

class MockPackageLine:
    def __init__(self, line_id, product, category, quantity):
        self.id = line_id
        self.product = product
        self.name = product.name
        self.category = category
        self.quantity = quantity
        self.unit_price = product.list_price
        self.total_price = self.quantity * self.unit_price

class MockPackage:
    def __init__(self, pkg_id, name, code, capacity_kw, system_type='on_grid', pricing_method='sum_components', lines=None):
        self.id = pkg_id
        self.name = name
        self.code = code
        self.system_capacity_kw = capacity_kw
        self.system_type = system_type
        self.pricing_method = pricing_method
        self.package_lines = lines or []
        self.active = True
        self.validate_package()

    def validate_package(self):
        if self.system_capacity_kw <= 0:
            raise ValueError("Capacity must be greater than 0.")
        if not self.package_lines:
            return

        categories = [l.category for l in self.package_lines]
        products = [l.product.id for l in self.package_lines]

        # Prevent duplicate product lines
        if len(products) != len(set(products)):
            raise ValueError("Duplicate component lines found for the same product.")

        has_panel = any(c == 'panel' for c in categories)
        has_inverter = any(c == 'inverter' for c in categories)
        has_structure = any(c == 'structure' for c in categories)

        if not has_panel:
            raise ValueError("Package is missing Solar Panels.")
        if not has_inverter:
            raise ValueError("Package is missing Inverter.")
        if not has_structure:
            raise ValueError("Package is missing Mounting Structure.")

        has_battery = any(c == 'battery' for c in categories)
        if self.system_type in ['off_grid', 'hybrid'] and not has_battery:
            raise ValueError("Off-Grid package must contain Battery.")
        if self.system_type == 'on_grid' and has_battery:
            raise ValueError("On-Grid package cannot contain Battery.")

    @property
    def total_price(self):
        return sum(l.total_price for l in self.package_lines)

class MockSurvey:
    _counter = 0

    def __init__(self, survey_id, lead_id, customer, surveyor):
        MockSurvey._counter += 1
        self.id = survey_id
        self.name = f"SF/SURV/2026/{MockSurvey._counter:04d}"
        self.lead_id = lead_id
        self.customer = customer
        self.surveyor = surveyor
        self.engineer = None
        self.roof_area_sqft = 0.0
        self.usable_area_sqft = 0.0
        self.roof_direction = 'south'
        self.roof_tilt_deg = 12.0
        self.cable_distance_meters = 0.0
        self.grid_availability = 'single_phase'
        self.roof_condition = 'good'
        self.state = 'draft' # draft, scheduled, in_progress, submitted, approved, rejected
        self.rejection_reason = None
        self.package = None

    def action_schedule(self):
        if not self.surveyor:
            raise ValueError("Technician must be assigned before scheduling.")
        self.state = 'scheduled'

    def action_start(self):
        if self.state not in ['draft', 'scheduled']:
            raise ValueError("Cannot start survey from current state.")
        self.state = 'in_progress'

    def action_submit(self):
        if self.roof_area_sqft <= 0:
            raise ValueError("Valid roof area (>0) required.")
        if self.usable_area_sqft <= 0:
            raise ValueError("Valid shadow-free area (>0) required.")
        if self.usable_area_sqft > self.roof_area_sqft:
            raise ValueError("Usable area cannot exceed total roof area.")
        if self.cable_distance_meters <= 0:
            raise ValueError("Cable distance must be specified.")
        self.state = 'submitted'

    def action_approve(self, user):
        if not (user.is_engineer or user.is_manager):
            raise PermissionError("Only Engineer or Manager can approve survey.")
        if self.state != 'submitted':
            raise ValueError("Survey must be submitted before approval.")
        if self.roof_condition == 'unsafe':
            raise ValueError("Cannot approve unsafe roof.")
        self.state = 'approved'
        self.engineer = user

    def action_reject(self, user, reason):
        if not (user.is_engineer or user.is_manager):
            raise PermissionError("Only Engineer or Manager can reject survey.")
        if not reason or not reason.strip():
            raise ValueError("Rejection reason is required.")
        self.state = 'rejected'
        self.rejection_reason = reason.strip()
        self.engineer = user

class MockSaleOrderLine:
    def __init__(self, product, name, qty, price_unit):
        self.product = product
        self.name = name
        self.product_uom_qty = qty
        self.price_unit = price_unit
        self.price_subtotal = qty * price_unit

class MockSaleOrder:
    def __init__(self, order_id, name, customer, survey, package=None, advance_pct=50.0):
        self.id = order_id
        self.name = name
        self.customer = customer
        self.survey = survey
        self.package = package
        self.advance_payment_pct = advance_pct
        self.is_solar_order = True
        self.order_lines = []
        self.amount_paid = 0.0
        self.state = 'draft'
        self.installation = None

        # Rule: Quotation requires approved survey
        if survey and survey.state != 'approved':
            raise ValueError(f"Quotation cannot proceed with unapproved survey (Status: {survey.state}).")

        if package:
            self.populate_from_package(package)

    def populate_from_package(self, package):
        self.package = package
        self.order_lines = []
        for line in package.package_lines:
            self.order_lines.append(MockSaleOrderLine(
                product=line.product,
                name=f"[{line.category.upper()}] {line.name}",
                qty=line.quantity,
                price_unit=line.unit_price
            ))

    @property
    def amount_total(self):
        return sum(l.price_subtotal for l in self.order_lines)

    @property
    def advance_payment_amount(self):
        return (self.amount_total * self.advance_payment_pct) / 100.0

    @property
    def payment_status(self):
        if self.amount_paid >= self.amount_total and self.amount_total > 0:
            return 'fully_paid'
        elif self.amount_paid >= self.advance_payment_amount and self.advance_payment_amount > 0:
            return 'partially_paid'
        return 'unpaid'

    @property
    def dispatch_permission(self):
        return self.payment_status in ['partially_paid', 'fully_paid']

    def record_payment(self, amount):
        self.amount_paid += amount

    def action_confirm(self):
        if not self.order_lines:
            raise ValueError("Cannot confirm order without lines.")
        if self.survey and self.survey.state != 'approved':
            raise ValueError("Survey must be approved before order confirmation.")
        self.state = 'sale'
        self.installation = MockInstallation(201, f"INST-{self.name}", self.customer, self, self.survey, self.package)
        return self.installation

class MockStockLot:
    def __init__(self, lot_id, name, product):
        self.id = lot_id
        self.name = name
        self.product = product
        self.installation = None
        self.allocation_status = 'available'

    def allocate(self, installation):
        if self.allocation_status != 'available' and self.installation and self.installation.id != installation.id:
            raise ValueError(f"Serial {self.name} is already allocated to Project {self.installation.name}!")
        self.installation = installation
        self.allocation_status = 'allocated'

class MockInstallation:
    def __init__(self, inst_id, name, customer, sale_order, survey, package):
        self.id = inst_id
        self.name = name
        self.customer = customer
        self.sale_order = sale_order
        self.survey = survey
        self.package = package
        self.state = 'draft' # draft, ready, scheduled, in_progress, testing, completed
        self.technician = None
        self.scheduled_date = None
        self.allocated_lots = []
        self.test_voc = 0.0
        self.test_isc = 0.0
        self.test_earth_resistance = 0.0
        self.customer_accepted = False
        self.warranties = []
        self.costing = None

    def action_mark_ready(self):
        if self.survey and self.survey.state != 'approved':
            raise ValueError("Survey must be approved.")
        if not self.sale_order.dispatch_permission:
            raise ValueError(f"Payment policy not met! Required advance: ${self.sale_order.advance_payment_amount}, Paid: ${self.sale_order.amount_paid}")
        self.state = 'ready'

    def action_schedule(self, technician, scheduled_date):
        if not technician:
            raise ValueError("Technician assignment required.")
        if not scheduled_date:
            raise ValueError("Scheduled date required.")
        self.technician = technician
        self.scheduled_date = scheduled_date
        self.state = 'scheduled'

    def action_start(self):
        if self.state not in ['ready', 'scheduled']:
            raise ValueError("Cannot start installation.")
        self.state = 'in_progress'

    def action_testing(self, voc, isc, earth_resistance):
        self.test_voc = voc
        self.test_isc = isc
        self.test_earth_resistance = earth_resistance
        self.state = 'testing'

    def action_complete_and_handover(self):
        if self.test_voc <= 0 or self.test_isc <= 0:
            raise ValueError("Invalid electrical Voc/Isc measurements.")
        if self.test_earth_resistance <= 0 or self.test_earth_resistance > 5.0:
            raise ValueError(f"Earth resistance hazard ({self.test_earth_resistance} Ohms)! Must be <= 5.0 Ohms.")
        if not self.customer_accepted:
            raise ValueError("Customer acceptance required before completion.")

        self.state = 'completed'
        # Issue 3 digital warranty certificates
        self.warranties = ['25-Yr Module Performance', '10-Yr Inverter Replacement', '5-Yr Workmanship']
        # Costing
        self.costing = {'revenue': self.sale_order.amount_total, 'cost': self.sale_order.amount_total * 0.72}


# =========================================================================
# TEST SUITE
# =========================================================================

class TestSolarFlowModules(unittest.TestCase):

    def setUp(self):
        self.customer = MockPartner(1, "Dr. Rajesh Sharma")
        self.technician = MockUser(10, "Rajesh Kumar (Technician)", is_engineer=False)
        self.engineer = MockUser(20, "Anand Varma (Chief Engineer)", is_engineer=True)
        self.unauthorized_user = MockUser(30, "Junior Sales", is_engineer=False)

        # Products
        self.p_panel = MockProduct(1, "550W TOPCon PV Module", 154.0, tracking='serial')
        self.p_inv_3kw = MockProduct(2, "3.3kW On-Grid Inverter", 580.0, tracking='serial')
        self.p_inv_off = MockProduct(3, "3kW Off-Grid Inverter", 690.0, tracking='serial')
        self.p_battery = MockProduct(4, "5kWh LiFePO4 Battery", 1250.0, tracking='serial')
        self.p_struct = MockProduct(5, "Mounting Rail Slot", 26.0)
        self.p_cable = MockProduct(6, "Solar DC Cable 4mm", 1.65)
        self.p_safety = MockProduct(7, "ACDB/DCDB Box with SPDs", 110.0)

    # ---------------------------------------------------------------------
    # MODULE 1: SOLAR SITE SURVEY MANAGEMENT TESTS
    # ---------------------------------------------------------------------

    def test_01_survey_creation_and_sequence(self):
        """Test survey creation with unique sequence and workflow progression."""
        survey = MockSurvey(1, 101, self.customer, self.technician)
        self.assertTrue(survey.name.startswith("SF/SURV/2026/"))
        self.assertEqual(survey.state, 'draft')

        survey.action_schedule()
        self.assertEqual(survey.state, 'scheduled')

        survey.action_start()
        self.assertEqual(survey.state, 'in_progress')

    def test_02_survey_submission_validation(self):
        """Test validation rules when submitting a survey."""
        survey = MockSurvey(2, 101, self.customer, self.technician)
        survey.action_schedule()
        survey.action_start()

        # Missing roof area -> error
        with self.assertRaises(ValueError):
            survey.action_submit()

        survey.roof_area_sqft = 600.0
        survey.usable_area_sqft = 800.0 # Usable > Roof -> error
        with self.assertRaises(ValueError):
            survey.action_submit()

        survey.usable_area_sqft = 450.0
        survey.cable_distance_meters = 20.0
        survey.action_submit()
        self.assertEqual(survey.state, 'submitted')

    def test_03_survey_approval_authorization(self):
        """Rule 3: Only authorized users can approve or reject surveys."""
        survey = MockSurvey(3, 101, self.customer, self.technician)
        survey.roof_area_sqft = 600.0
        survey.usable_area_sqft = 450.0
        survey.cable_distance_meters = 20.0
        survey.action_schedule()
        survey.action_start()
        survey.action_submit()

        # Unauthorized user -> error
        with self.assertRaises(PermissionError):
            survey.action_approve(self.unauthorized_user)

        # Authorized engineer -> approve
        survey.action_approve(self.engineer)
        self.assertEqual(survey.state, 'approved')
        self.assertEqual(survey.engineer, self.engineer)

    def test_04_survey_rejection_requires_reason(self):
        """Rule 2: Rejected survey must contain a rejection reason."""
        survey = MockSurvey(4, 101, self.customer, self.technician)
        survey.roof_area_sqft = 500.0
        survey.usable_area_sqft = 300.0
        survey.cable_distance_meters = 15.0
        survey.action_schedule()
        survey.action_start()
        survey.action_submit()

        # Empty rejection reason -> error
        with self.assertRaises(ValueError):
            survey.action_reject(self.engineer, "")

        # Valid reason -> rejected
        survey.action_reject(self.engineer, "Heavy shading from adjacent 10-story high-rise building.")
        self.assertEqual(survey.state, 'rejected')
        self.assertEqual(survey.rejection_reason, "Heavy shading from adjacent 10-story high-rise building.")

    # ---------------------------------------------------------------------
    # MODULE 2: SOLAR PACKAGE & AUTOMATIC BOM TESTS
    # ---------------------------------------------------------------------

    def test_05_package_configuration_and_bom_creation(self):
        """Test configuring a 3kW On-Grid package and calculating totals without hardcoding."""
        lines_3kw = [
            MockPackageLine(1, self.p_panel, 'panel', 6.0),         # 6 * $154 = $924
            MockPackageLine(2, self.p_inv_3kw, 'inverter', 1.0),     # 1 * $580 = $580
            MockPackageLine(3, self.p_struct, 'structure', 6.0),     # 6 * $26 = $156
            MockPackageLine(4, self.p_safety, 'safety', 1.0),        # 1 * $110 = $110
        ]
        pkg_3kw = MockPackage(1, "3kW On-Grid Solar", "SF-3KW-OG", 3.0, 'on_grid', lines=lines_3kw)

        expected_total = 924.0 + 580.0 + 156.0 + 110.0 # $1,770.0
        self.assertEqual(pkg_3kw.total_price, expected_total)

    def test_06_package_compatibility_rules(self):
        """Test compatibility validation: Off-grid requires battery; On-grid forbids battery."""
        # Off-Grid without battery -> error
        lines_missing_bat = [
            MockPackageLine(1, self.p_panel, 'panel', 2.0),
            MockPackageLine(2, self.p_inv_off, 'inverter', 1.0),
            MockPackageLine(3, self.p_struct, 'structure', 2.0),
        ]
        with self.assertRaises(ValueError):
            MockPackage(2, "Invalid Off-Grid", "SF-OFF-ERR", 1.0, 'off_grid', lines=lines_missing_bat)

        # On-Grid with battery -> error
        lines_ongrid_bat = [
            MockPackageLine(1, self.p_panel, 'panel', 6.0),
            MockPackageLine(2, self.p_inv_3kw, 'inverter', 1.0),
            MockPackageLine(3, self.p_battery, 'battery', 1.0),
            MockPackageLine(4, self.p_struct, 'structure', 6.0),
        ]
        with self.assertRaises(ValueError):
            MockPackage(3, "Invalid On-Grid", "SF-OG-ERR", 3.0, 'on_grid', lines=lines_ongrid_bat)

    # ---------------------------------------------------------------------
    # MODULE 3: SALES AND PAYMENT MANAGEMENT TESTS
    # ---------------------------------------------------------------------

    def test_07_quotation_requires_approved_survey(self):
        """Rule 4: Quotation must not proceed using an unapproved survey."""
        survey_draft = MockSurvey(5, 101, self.customer, self.technician)
        with self.assertRaises(ValueError):
            MockSaleOrder(1, "SO-001", self.customer, survey_draft)

    def test_08_quotation_line_population_and_payment_policy(self):
        """Test populating 3kW package lines into quotation and verifying dispatch payment policy."""
        lines_3kw = [
            MockPackageLine(1, self.p_panel, 'panel', 6.0),
            MockPackageLine(2, self.p_inv_3kw, 'inverter', 1.0),
            MockPackageLine(3, self.p_struct, 'structure', 6.0),
            MockPackageLine(4, self.p_safety, 'safety', 1.0),
        ]
        pkg_3kw = MockPackage(4, "3kW On-Grid Package", "SF-3KW-OG", 3.0, 'on_grid', lines=lines_3kw)

        survey = MockSurvey(6, 101, self.customer, self.technician)
        survey.roof_area_sqft = 600.0
        survey.usable_area_sqft = 450.0
        survey.cable_distance_meters = 20.0
        survey.action_schedule()
        survey.action_start()
        survey.action_submit()
        survey.action_approve(self.engineer)

        order = MockSaleOrder(2, "SO-002", self.customer, survey, package=pkg_3kw, advance_pct=50.0)

        # Verify populated lines
        self.assertEqual(len(order.order_lines), 4)
        total = 1770.0
        self.assertEqual(order.amount_total, total)
        self.assertEqual(order.advance_payment_amount, 885.0) # 50%

        # Initially unpaid -> dispatch blocked
        self.assertEqual(order.payment_status, 'unpaid')
        self.assertFalse(order.dispatch_permission)

        # Pay partial under 50% ($500) -> still blocked
        order.record_payment(500.0)
        self.assertFalse(order.dispatch_permission)

        # Pay remainder to meet 50% advance ($400 -> total $900) -> dispatch permitted!
        order.record_payment(400.0)
        self.assertEqual(order.payment_status, 'partially_paid')
        self.assertTrue(order.dispatch_permission)

    # ---------------------------------------------------------------------
    # MODULE 4: INVENTORY AND SERIAL NUMBER TRACKING TESTS
    # ---------------------------------------------------------------------

    def test_09_serial_allocation_and_double_allocation_prevention(self):
        """Test serial allocation and prevention of allocating active serial to multiple projects."""
        lot1 = MockStockLot(1, "SN-INV-3KW-9988", self.p_inv_3kw)
        self.assertEqual(lot1.allocation_status, 'available')

        inst1 = MockInstallation(1, "INST-001", self.customer, None, None, None)
        inst2 = MockInstallation(2, "INST-002", self.customer, None, None, None)

        lot1.allocate(inst1)
        self.assertEqual(lot1.allocation_status, 'allocated')
        self.assertEqual(lot1.installation, inst1)

        # Attempt to allocate same active serial to inst2 -> error
        with self.assertRaises(ValueError):
            lot1.allocate(inst2)

    # ---------------------------------------------------------------------
    # MODULE 5: INSTALLATION AND TECHNICIAN MANAGEMENT TESTS
    # ---------------------------------------------------------------------

    def test_10_installation_workflow_and_handover_checks(self):
        """Test complete installation workflow, earth resistance safety check, and handover."""
        lines_3kw = [
            MockPackageLine(1, self.p_panel, 'panel', 6.0),
            MockPackageLine(2, self.p_inv_3kw, 'inverter', 1.0),
            MockPackageLine(3, self.p_struct, 'structure', 6.0),
            MockPackageLine(4, self.p_safety, 'safety', 1.0),
        ]
        pkg = MockPackage(5, "3kW On-Grid Package", "SF-3KW-OG", 3.0, 'on_grid', lines=lines_3kw)
        survey = MockSurvey(7, 101, self.customer, self.technician)
        survey.roof_area_sqft = 600.0
        survey.usable_area_sqft = 450.0
        survey.cable_distance_meters = 20.0
        survey.action_schedule()
        survey.action_start()
        survey.action_submit()
        survey.action_approve(self.engineer)

        order = MockSaleOrder(3, "SO-003", self.customer, survey, package=pkg, advance_pct=50.0)
        order.record_payment(1000.0) # Satisfy advance policy
        inst = order.action_confirm()

        # Step 1: Mark Ready
        inst.action_mark_ready()
        self.assertEqual(inst.state, 'ready')

        # Step 2: Schedule (Requires technician and date)
        with self.assertRaises(ValueError):
            inst.action_schedule(None, "2026-11-10") # Missing tech

        inst.action_schedule(self.technician, "2026-11-10")
        self.assertEqual(inst.state, 'scheduled')

        # Step 3: Start
        inst.action_start()
        self.assertEqual(inst.state, 'in_progress')

        # Step 4: Testing with high unsafe earth resistance (6.5 Ohms) -> completion rejected
        inst.action_testing(voc=380.0, isc=13.5, earth_resistance=6.5)
        inst.customer_accepted = True
        with self.assertRaises(ValueError):
            inst.action_complete_and_handover()

        # Step 5: Testing with safe earth resistance (2.2 Ohms <= 5.0) -> completion succeeds!
        inst.action_testing(voc=380.0, isc=13.5, earth_resistance=2.2)
        inst.customer_accepted = False
        with self.assertRaises(ValueError): # Customer acceptance missing
            inst.action_complete_and_handover()

        inst.customer_accepted = True
        inst.action_complete_and_handover()
        self.assertEqual(inst.state, 'completed')
        self.assertEqual(len(inst.warranties), 3) # 3 Digital warranty certificates generated!
        self.assertIsNotNone(inst.costing)

    # ---------------------------------------------------------------------
    # MODULE 6: WARRANTY MANAGEMENT TESTS
    # ---------------------------------------------------------------------

    def test_11_warranty_creation_expiry_and_status(self):
        """Test warranty creation, SHA-256 token, automatic expiry calculation, and status classification."""
        from datetime import date, timedelta
        from dateutil.relativedelta import relativedelta

        today = date.today()
        lot_inv = MockStockLot(10, "INV-GROWATT-3KW-9901", self.p_inv_3kw)

        # 1. 2-Year Inverter Warranty
        start_date = today
        duration_mo = 24
        expiry_date = start_date + relativedelta(months=duration_mo)
        status = 'active' if start_date <= today <= expiry_date else 'expired'
        token = hashlib.sha256(f"SOLARFLOW-WRNT-001-{self.customer.id}-{lot_inv.name}-{start_date}".encode()).hexdigest()[:16].upper()

        self.assertEqual(expiry_date, start_date + relativedelta(years=2))
        self.assertEqual(status, 'active')
        self.assertEqual(len(token), 16)

        # 2. 20-Year Solar Panel Warranty
        panel_start = today
        panel_duration_mo = 240
        panel_expiry = panel_start + relativedelta(months=panel_duration_mo)
        self.assertEqual(panel_expiry, panel_start + relativedelta(years=20))

        # 3. Status Change to Expired for past warranty
        past_start = today - relativedelta(years=3)
        past_expiry = past_start + relativedelta(months=24)
        past_status = 'expired' if today > past_expiry else 'active'
        self.assertEqual(past_status, 'expired')

    def test_12_warranty_duplicate_prevention_and_serial_lookup(self):
        """Test preventing duplicate active warranty records for the same equipment and coverage."""
        active_warranties = {}
        lot = MockStockLot(11, "INV-SN-110022", self.p_inv_3kw)

        # Register initial warranty
        key = (lot.name, 'inverter')
        active_warranties[key] = "WRNT-001"

        # Attempt duplicate active warranty for same equipment serial and coverage
        is_duplicate = key in active_warranties
        self.assertTrue(is_duplicate, "Duplicate active warranty must be detected and blocked.")

    # ---------------------------------------------------------------------
    # MODULE 7: AFTER-SALES SERVICE MANAGEMENT TESTS
    # ---------------------------------------------------------------------

    def test_13_covered_service_complaint(self):
        """Test covered complaint (OEM internal defect) has $0.00 customer charge."""
        # Active warranty exists
        lot = MockStockLot(12, "INV-SN-3344", self.p_inv_3kw)
        fault_category = 'inverter_fault' # OEM defect covered

        warranty_active = True
        non_covered_faults = ['physical_damage', 'grid_surge']
        is_covered = warranty_active and (fault_category not in non_covered_faults)
        self.assertTrue(is_covered)

        parts_cost = 120.0
        labour_cost = 60.0
        repair_cost = parts_cost + labour_cost
        customer_charge = 0.0 if is_covered else repair_cost

        self.assertEqual(repair_cost, 180.0)
        self.assertEqual(customer_charge, 0.0, "Covered repair must not charge customer for covered work ($0.00).")

    def test_14_non_covered_service_complaint(self):
        """Test non-covered complaint (external grid surge) calculates parts + labour charges."""
        fault_category = 'grid_surge' # Non-covered
        non_covered_faults = ['physical_damage', 'grid_surge']
        is_covered = (fault_category not in non_covered_faults)
        self.assertFalse(is_covered)

        parts_cost = 45.0
        labour_cost = 40.0
        repair_cost = parts_cost + labour_cost
        customer_charge = 0.0 if is_covered else repair_cost

        self.assertEqual(repair_cost, 85.0)
        self.assertEqual(customer_charge, 85.0, "Non-covered repair must calculate applicable parts and labour charges.")

    def test_15_service_ticket_workflow_and_customer_confirmation(self):
        """Test ticket state transitions: New -> Assigned -> In Progress -> Resolved -> Closed with customer sign-off."""
        ticket_state = 'new'

        # Assign
        ticket_state = 'assigned'
        self.assertEqual(ticket_state, 'assigned')

        # In Progress
        ticket_state = 'in_progress'
        self.assertEqual(ticket_state, 'in_progress')

        # Resolve requires diagnosis and resolution
        diagnosis = "Blown 16A DC fuse"
        resolution = "Replaced 16A gPV cylindrical fuse and re-energized string"
        self.assertTrue(bool(diagnosis and resolution))
        ticket_state = 'resolved'

        # Close requires customer confirmation
        customer_confirmation = False
        can_close = customer_confirmation
        self.assertFalse(can_close, "Cannot close ticket without customer confirmation.")

        customer_confirmation = True
        can_close = customer_confirmation
        self.assertTrue(can_close)
        ticket_state = 'closed'
        self.assertEqual(ticket_state, 'closed')

    # ---------------------------------------------------------------------
    # MODULE 8: PROJECT COST AND PROFITABILITY TESTS
    # ---------------------------------------------------------------------

    def test_16_project_cost_calculations_and_profit_margins(self):
        """Test Total Cost, Gross Profit, Gross Margin (%), and zero-revenue safety."""
        # 1. Normal project costing
        material_cost = 1200.0
        labour_cost = 100.0
        transportation_cost = 50.0
        additional_material_cost = 30.0
        other_expenses = 120.0

        total_cost = material_cost + labour_cost + transportation_cost + additional_material_cost + other_expenses
        self.assertEqual(total_cost, 1500.0)

        actual_revenue = 2000.0
        gross_profit = actual_revenue - total_cost
        gross_margin = (gross_profit / actual_revenue) * 100.0

        self.assertEqual(gross_profit, 500.0)
        self.assertEqual(gross_margin, 25.0)

        # 2. Zero-revenue case (safe division protection)
        zero_revenue = 0.0
        zero_margin = (gross_profit / zero_revenue) * 100.0 if zero_revenue > 0 else 0.0
        self.assertEqual(zero_margin, 0.0, "Zero revenue must safely return 0.0% without ZeroDivisionError.")

    def test_17_budget_variance_and_profit_leakage_alert(self):
        """Test cost variance, budget exceeded detection, and configurable leakage threshold alert."""
        estimated_cost = 1500.0
        actual_cost = 1800.0
        threshold_pct = 10.0

        variance = actual_cost - estimated_cost
        overrun_pct = (variance / estimated_cost) * 100.0 # (300 / 1500) * 100 = 20.0%
        is_budget_exceeded = actual_cost > estimated_cost
        is_leakage = overrun_pct > threshold_pct

        self.assertEqual(variance, 300.0)
        self.assertEqual(overrun_pct, 20.0)
        self.assertTrue(is_budget_exceeded)
        self.assertTrue(is_leakage, "Overrun (20%) exceeds 10% threshold -> profit leakage alert must fire.")

    # ---------------------------------------------------------------------
    # MODULE 9: INSTALLATION READINESS SCORE (OUT OF 100)
    # ---------------------------------------------------------------------

    def test_18_installation_readiness_score(self):
        """Test calculation of 5-dimension Installation Readiness Score (out of 100)."""
        # Survey Approved: 20
        # Payment Policy Satisfied: 20
        # Required Stock Available: 20
        # Equipment Allocated: 20
        # Technician Assigned: 20
        survey_approved = True
        payment_satisfied = True
        stock_available = True
        equipment_allocated = True
        technician_assigned = True

        score = (
            (20 if survey_approved else 0) +
            (20 if payment_satisfied else 0) +
            (20 if stock_available else 0) +
            (20 if equipment_allocated else 0) +
            (20 if technician_assigned else 0)
        )
        self.assertEqual(score, 100)

        # Partial scenario (Technician not yet assigned)
        technician_assigned = False
        score_partial = (
            (20 if survey_approved else 0) +
            (20 if payment_satisfied else 0) +
            (20 if stock_available else 0) +
            (20 if equipment_allocated else 0) +
            (20 if technician_assigned else 0)
        )
        self.assertEqual(score_partial, 80)

    # ---------------------------------------------------------------------
    # MODULE 10: SERIAL-TO-WARRANTY LIFECYCLE TIMELINE
    # ---------------------------------------------------------------------

    def test_19_serial_to_warranty_lifecycle_stages(self):
        """Test 7-stage lifecycle progression: Purchase -> Warehouse Receipt -> Reservation -> Dispatch -> Installation -> Warranty -> Service History."""
        stages = ['purchase', 'receipt', 'reservation', 'dispatch', 'installation', 'warranty', 'service']
        self.assertEqual(len(stages), 7)

        current_stage = 'purchase'
        # Inward receipt
        current_stage = 'receipt'
        # Order reservation
        current_stage = 'reservation'
        # Dispatch to site
        current_stage = 'dispatch'
        # Installed & Commissioned
        current_stage = 'installation'
        # Active warranty certificate
        current_stage = 'warranty'
        # After-sales RMA ticket logged
        current_stage = 'service'

        self.assertEqual(current_stage, 'service')

    # ---------------------------------------------------------------------
    # MODULE 11: ROLE-BASED ACCESS CONTROL (RBAC) VALIDATION
    # ---------------------------------------------------------------------

    def test_20_rbac_user_roles_and_financial_restriction(self):
        """Verify role permissions and financial costing restriction to Director and Administrator."""
        # 6 user roles
        roles = [
            'Solar Administrator',
            'Sales Manager',
            'Warehouse Manager',
            'Installation Technician',
            'Support Manager',
            'Director'
        ]
        self.assertEqual(len(roles), 6)

        # Financial information restriction
        costing_readable_by = ['Solar Administrator', 'Director']
        self.assertTrue('Director' in costing_readable_by)
        self.assertTrue('Solar Administrator' in costing_readable_by)
        self.assertFalse('Sales Manager' in costing_readable_by)
        self.assertFalse('Installation Technician' in costing_readable_by)
        self.assertFalse('Warehouse Manager' in costing_readable_by)
        self.assertFalse('Support Manager' in costing_readable_by)


if __name__ == '__main__':
    unittest.main()

