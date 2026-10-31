# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestSolarFlowLeadManagement(TransactionCase):

    def setUp(self):
        super(TestSolarFlowLeadManagement, self).setUp()
        self.LeadModel = self.env['crm.lead']
        self.SurveyModel = self.env['solarflow.survey']
        self.PartnerModel = self.env['res.partner']

        self.customer = self.PartnerModel.create({
            'name': 'Prof. Ananya Sen',
            'email': 'ananya.sen@example.com',
            'phone': '+91 98888 77777',
            'street': '77 Green Park Layout',
            'city': 'Bengaluru',
        })

    def test_01_create_solarflow_lead_with_sequence(self):
        """Test creating a solar lead and verifying auto-generated unique reference."""
        lead = self.LeadModel.create({
            'name': 'Residential Solar 6kW Inquiry',
            'partner_id': self.customer.id,
            'is_solar_lead': True,
            'solar_capacity_kw': 6.0,
            'solar_system_type': 'on_grid',
            'subsidy_required': True,
            'expected_install_date': '2026-11-20',
            'solar_lead_source': 'web_inbound',
            'monthly_consumption_kwh': 720.0,
            'current_electricity_tariff': 8.5,
            'estimated_roof_area_sqft': 900.0,
        })
        self.assertTrue(lead.solarflow_reference, "Lead should have an auto-generated solar reference.")
        self.assertTrue(lead.solarflow_reference.startswith('SF/LEAD/'), f"Reference {lead.solarflow_reference} must start with SF/LEAD/")
        self.assertEqual(lead.survey_status, 'not_scheduled')
        self.assertEqual(lead.solar_feasibility_score, 100)

    def test_02_validation_error_on_zero_capacity(self):
        """Test that non-positive capacity raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.LeadModel.create({
                'name': 'Invalid Capacity Lead',
                'partner_id': self.customer.id,
                'is_solar_lead': True,
                'solar_capacity_kw': 0.0, # Invalid <= 0
            })

    def test_03_validation_error_missing_contact_info(self):
        """Test that missing phone and email raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.LeadModel.create({
                'name': 'Nameless Lead',
                'is_solar_lead': True,
                'solar_capacity_kw': 5.0,
                'partner_name': False,
                'contact_name': False,
                'partner_id': False,
                'phone': False,
                'email_from': False,
            })

    def test_04_convert_lead_to_survey(self):
        """Test converting a qualified lead into the site survey stage."""
        lead = self.LeadModel.create({
            'name': 'Villa 5kW Rooftop Solar',
            'partner_id': self.customer.id,
            'is_solar_lead': True,
            'solar_capacity_kw': 5.0,
            'solar_system_type': 'hybrid',
            'subsidy_required': True,
            'monthly_consumption_kwh': 600.0,
            'current_electricity_tariff': 8.5,
            'estimated_roof_area_sqft': 800.0,
        })

        action = lead.action_schedule_site_survey()
        self.assertEqual(action.get('res_model'), 'solarflow.survey')
        survey_id = action.get('res_id')
        survey = self.SurveyModel.browse(survey_id)

        self.assertTrue(survey.exists(), "Survey record should be created.")
        self.assertEqual(survey.partner_id, self.customer)
        self.assertEqual(survey.recommended_capacity_kw, 5.0)
        self.assertEqual(survey.system_type, 'hybrid')
        self.assertEqual(lead.survey_status, 'scheduled')
