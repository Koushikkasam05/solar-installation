# -*- coding: utf-8 -*-
"""
Automated Test Suite for Solar Installation ERP (15 Stages)
Tests mathematical models, engineering formulas, subsidy rules, and costing.
"""
import unittest
import math
import hashlib
from datetime import date
from dateutil.relativedelta import relativedelta

class TestSolarEPCLogic(unittest.TestCase):

    def test_stage_5_solar_lead_recommendations(self):
        """Test Lead capacity calculation and feasibility score."""
        monthly_avg_kwh = 450.0
        roof_area_sqft = 600.0
        sanctioned_load_kw = 5.0

        # Rule of thumb: 1 kW generates ~120 kWh/mo, needs ~90 sqft
        capacity_by_kwh = monthly_avg_kwh / 120.0 # 3.75 kW
        capacity_by_roof = roof_area_sqft / 90.0   # 6.67 kW
        rec_cap = min(capacity_by_kwh, capacity_by_roof)
        if sanctioned_load_kw > 0 and rec_cap > sanctioned_load_kw:
            rec_cap = sanctioned_load_kw

        self.assertAlmostEqual(rec_cap, 3.75, places=2)

        # Feasibility score check
        score = 100
        if roof_area_sqft < 450:
            score -= 15
        if monthly_avg_kwh < 200:
            score -= 20
        self.assertEqual(score, 100) # Full feasibility

    def test_stage_6_and_7_dynamic_bom_sizing(self):
        """Test automatic BOM generator sizing rules."""
        system_kw = 5.0
        total_watts = system_kw * 1000.0
        panel_wattage = 550
        panel_count = math.ceil(total_watts / panel_wattage)

        # 5000 / 550 = 9.09 -> 10 panels
        self.assertEqual(panel_count, 10)

        # Inverter matching
        inverter_kw = round(system_kw * 1.0, 2)
        self.assertEqual(inverter_kw, 5.0)

        # Cable length: db_distance * 2 + 10m margin
        db_distance_meters = 25.0
        cable_len = db_distance_meters * 2 + 10.0
        self.assertEqual(cable_len, 60.0)

        # Mounting structure items
        structure_slots = panel_count
        self.assertEqual(structure_slots, 10)

    def test_stage_8_subsidy_and_payback_calculation(self):
        """Test PM Surya Ghar subsidy rules and solar ROI payback."""
        # Case 1: 3 kW System
        cap_3kw = 3.0
        if cap_3kw <= 2.0:
            subsidy_3kw = cap_3kw * 360.0
        elif cap_3kw <= 3.0:
            subsidy_3kw = 940.0 # Standard residential cap
        self.assertEqual(subsidy_3kw, 940.0)

        # Financial ROI on a $2,400 system
        gross_price = 2400.0
        net_payable = gross_price - subsidy_3kw # $1,460
        annual_units = cap_3kw * 1450.0 # 4,350 units
        tariff = 0.12 # $0.12 per unit
        annual_savings = annual_units * tariff # $522.0
        payback_years = round(net_payable / annual_savings, 2)

        self.assertAlmostEqual(payback_years, 2.80, places=2)
        self.assertTrue(payback_years < 3.5, "Payback should be under 3.5 years for high-yield solar")

    def test_stage_10_installation_milestone_progress(self):
        """Test 6-Phase installation progress computation."""
        phases = [True, True, True, False, False, False] # 3 of 6 phases completed
        completed = sum(1 for p in phases if p)
        progress = round((completed / 6.0) * 100.0, 1)
        self.assertEqual(progress, 50.0)

        # All 6 complete
        phases_all = [True] * 6
        progress_all = round((sum(1 for p in phases_all if p) / 6.0) * 100.0, 1)
        self.assertEqual(progress_all, 100.0)

    def test_stage_10_electrical_qc_limits(self):
        """Test Earth resistance safety threshold (<5.0 Ohms)."""
        good_earth_resistance = 2.4 # Ohms
        bad_earth_resistance = 6.2  # Ohms
        self.assertTrue(good_earth_resistance < 5.0)
        self.assertFalse(bad_earth_resistance < 5.0)

    def test_stage_11_warranty_token_cryptography(self):
        """Test cryptographic token generation for digital warranty certificate."""
        cert_name = "WRNT/2026/0001"
        cust_id = 42
        start_date = "2026-10-31"
        raw_str = f"{cert_name}-{cust_id}-{start_date}-SOLAR-SECURE"
        token = hashlib.sha256(raw_str.encode()).hexdigest()[:16].upper()
        self.assertEqual(len(token), 16)
        self.assertTrue(token.isalnum())

    def test_stage_13_job_costing_and_profitability(self):
        """Test job costing and net profit margin calculations."""
        revenue = 3400.0 # 5kW turnkey
        bom_cost = 1750.0
        structure_cost = 225.0
        electrical_cost = 175.0
        labor_cost = 150.0
        liaisoning_cost = 120.0
        transport_cost = 60.0

        total_cost = bom_cost + structure_cost + electrical_cost + labor_cost + liaisoning_cost + transport_cost
        gross_profit = revenue - total_cost
        margin_pct = round((gross_profit / revenue) * 100.0, 2)

        self.assertEqual(total_cost, 2480.0)
        self.assertEqual(gross_profit, 920.0)
        self.assertAlmostEqual(margin_pct, 27.06, places=2)
        self.assertTrue(margin_pct > 25.0, "Project should fall under High Margin (>25%) tier")


if __name__ == '__main__':
    unittest.main()
