# -*- coding: utf-8 -*-
"""
Standalone Test Runner for SolarFlow Customer Lead Management
Validates business logic, unique sequence formatting, customer validation, and survey conversion.
"""
import unittest
import re

class MockPartner:
    def __init__(self, partner_id, name, phone, email):
        self.id = partner_id
        self.name = name
        self.phone = phone
        self.email = email

class MockSurvey:
    def __init__(self, survey_id, lead_id, partner, capacity_kw, system_type):
        self.id = survey_id
        self.name = f"SF/SURV/2026/{survey_id:04d}"
        self.lead_id = lead_id
        self.partner = partner
        self.capacity_kw = capacity_kw
        self.system_type = system_type
        self.state = 'draft'

class MockLead:
    _seq_counter = 0

    def __init__(self, lead_id, name, partner, capacity_kw, system_type='on_grid', subsidy=True, expected_install_date=None, monthly_kwh=450.0, tariff=8.5, roof_area=600.0, phone=None, email=None):
        MockLead._seq_counter += 1
        self.id = lead_id
        self.solarflow_reference = f"SF/LEAD/2026/{MockLead._seq_counter:04d}"
        self.name = name
        self.partner = partner
        self.phone = phone or (partner.phone if partner else None)
        self.email = email or (partner.email if partner else None)
        self.solar_capacity_kw = capacity_kw
        self.solar_system_type = system_type
        self.subsidy_required = subsidy
        self.expected_install_date = expected_install_date
        self.survey_status = 'not_scheduled'
        self.monthly_consumption_kwh = monthly_kwh
        self.current_electricity_tariff = tariff
        self.estimated_roof_area_sqft = roof_area
        self.survey = None

        # Run Validation
        self.validate()

        # Compute Feasibility
        self.compute_estimates()

    def validate(self):
        has_name = bool(self.name or (self.partner and self.partner.name))
        if not has_name:
            raise ValueError("Customer Name or Company Name is mandatory.")
        if not self.phone and not self.email:
            raise ValueError("Customer Phone or Email must be provided.")
        if self.solar_capacity_kw <= 0:
            raise ValueError("Required solar capacity must be strictly greater than 0 kW.")

    def compute_estimates(self):
        self.estimated_monthly_bill = self.monthly_consumption_kwh * self.current_electricity_tariff
        req_space = self.solar_capacity_kw * 80.0
        score = 100
        if self.estimated_roof_area_sqft < req_space:
            deficit = req_space - self.estimated_roof_area_sqft
            penalty = min(50, int((deficit / req_space) * 50))
            score -= penalty
        if self.monthly_consumption_kwh < 150:
            score -= 15
        self.solar_feasibility_score = max(0, min(100, score))

    def action_schedule_site_survey(self):
        survey = MockSurvey(101, self.id, self.partner, self.solar_capacity_kw, self.solar_system_type)
        self.survey = survey
        self.survey_status = 'scheduled'
        return survey


class TestSolarFlowLeadManagementSuite(unittest.TestCase):

    def setUp(self):
        self.customer = MockPartner(1, "Dr. Rajesh Sharma", "+91 98765 43210", "rajesh.sharma@example.com")

    def test_01_lead_creation_and_unique_sequence(self):
        """Verify unique sequence format: SF/LEAD/2026/XXXX."""
        lead1 = MockLead(1, "Rooftop Solar 5kW", self.customer, 5.0)
        lead2 = MockLead(2, "Villa Solar 3kW", self.customer, 3.0)

        self.assertTrue(re.match(r"^SF/LEAD/2026/\d{4}$", lead1.solarflow_reference))
        self.assertTrue(re.match(r"^SF/LEAD/2026/\d{4}$", lead2.solarflow_reference))
        self.assertNotEqual(lead1.solarflow_reference, lead2.solarflow_reference)

    def test_02_validation_invalid_capacity(self):
        """Verify that capacity <= 0 raises ValueError."""
        with self.assertRaises(ValueError):
            MockLead(3, "Invalid Lead", self.customer, 0.0)

    def test_03_validation_missing_contact_info(self):
        """Verify that missing both phone and email raises ValueError."""
        with self.assertRaises(ValueError):
            MockLead(4, "No Contact Lead", None, 5.0, phone=None, email=None)

    def test_04_feasibility_score_computation(self):
        """Verify feasibility score: good roof area vs constrained roof."""
        # Adequate roof: 5 kW needs 400 sq.ft, given 850 sq.ft -> 100%
        lead_good = MockLead(5, "Good Roof Lead", self.customer, 5.0, roof_area=850.0)
        self.assertEqual(lead_good.solar_feasibility_score, 100)

        # Tight roof: 5 kW needs 400 sq.ft, given 200 sq.ft -> penalized
        lead_tight = MockLead(6, "Constrained Roof Lead", self.customer, 5.0, roof_area=200.0)
        self.assertTrue(lead_tight.solar_feasibility_score < 100)

    def test_05_schedule_survey_conversion(self):
        """Verify conversion from lead to site survey."""
        lead = MockLead(7, "Survey Ready Lead", self.customer, 5.0, system_type='hybrid')
        self.assertEqual(lead.survey_status, 'not_scheduled')

        survey = lead.action_schedule_site_survey()
        self.assertEqual(lead.survey_status, 'scheduled')
        self.assertEqual(survey.capacity_kw, 5.0)
        self.assertEqual(survey.system_type, 'hybrid')
        self.assertEqual(survey.partner.name, "Dr. Rajesh Sharma")

    def test_06_filtering_and_search_simulation(self):
        """Simulate search filters (On-Grid, Subsidy Required, Survey Status)."""
        leads = [
            MockLead(8, "Lead A", self.customer, 3.0, system_type='on_grid', subsidy=True),
            MockLead(9, "Lead B", self.customer, 10.0, system_type='on_grid', subsidy=False),
            MockLead(10, "Lead C", self.customer, 5.0, system_type='hybrid', subsidy=True),
        ]
        # Filter by subsidy
        subsidized = [l for l in leads if l.subsidy_required]
        self.assertEqual(len(subsidized), 2)

        # Filter by on-grid
        ongrid = [l for l in leads if l.solar_system_type == 'on_grid']
        self.assertEqual(len(ongrid), 2)


if __name__ == '__main__':
    unittest.main()
