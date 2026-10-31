# -*- coding: utf-8 -*-
{
    'name': 'Solar Installation ERP - End-to-End Solar EPC Management',
    'version': '17.0.1.0.0',
    'summary': 'Complete Solar EPC Lifecycle: Leads, Site Survey, Auto-BOM, Subsidy, Serial Tracking, Installation, Warranty & AMC',
    'sequence': 10,
    'description': """
Solar Installation ERP (End-to-End Solar EPC Solution)
======================================================
A comprehensive enterprise solution for Solar EPCs handling:
- Customer Lead Management & Electricity Bill Consumption Analysis
- Mobile-ready Site Survey Management (Roof Azimuth, Tilt, Shadow Analysis, Photos)
- Dynamic Solar Packages & Automated Bill of Materials (BOM) Generation
- Solar Sales Quotations with PM Surya Ghar / State Subsidy & Payback Calculation
- Milestone-Based Payment Invoicing (Booking, Design, Dispatch, Installation, Net Meter)
- Serialized Inventory Tracking for Solar Panels, Inverters & Batteries
- Field Technician & Installation Project Tracking (6-Phase Commissioning Checklist)
- Digital Warranty Certificates with Unique Serial Association
- After-Sales Service Management & Annual Maintenance Contracts (AMC)
- Real-Time Project Costing, Profitability & Margin Variance Analysis
- Executive Management Dashboard & Role-based Access Control (RBAC)
    """,
    'category': 'Operations/Solar EPC',
    'author': 'Solar ERP Team / Hackathon 2026',
    'website': 'https://github.com/solar-epc-erp',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'crm',
        'sale_management',
        'stock',
        'project',
        'account',
    ],
    'data': [
        'security/solar_security.xml',
        'security/ir.model.access.csv',
        'data/solar_sequence.xml',
        'data/solar_package_data.xml',
        'views/solar_menus.xml',
        'views/solar_lead_views.xml',
        'views/solar_survey_views.xml',
        'views/solar_package_views.xml',
        'views/solar_sales_views.xml',
        'views/solar_inventory_views.xml',
        'views/solar_installation_views.xml',
        'views/solar_warranty_views.xml',
        'views/solar_service_views.xml',
        'views/solar_costing_views.xml',
        'views/solar_dashboard_views.xml',
        'reports/solar_reports.xml',
        'reports/solar_survey_report.xml',
        'reports/solar_warranty_certificate.xml',
    ],
    'demo': [
        'data/solar_demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'solar_management/static/src/css/solar_style.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
