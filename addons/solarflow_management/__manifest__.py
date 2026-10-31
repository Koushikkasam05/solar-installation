# -*- coding: utf-8 -*-
{
    'name': 'SolarFlow ERP – Solar Installation Management System',
    'version': '20.0.1.0.0',
    'summary': 'End-to-End Rooftop Solar EPC: Leads, Site Survey, Auto-BOM, Milestones, Serial Dispatch, Commissioning, Warranty & Costing',
    'sequence': 1,
    'description': """
SolarFlow ERP – Solar Installation Management System
====================================================
A state-of-the-art enterprise solution for Solar EPC companies covering:
- **Lead Management**: Extended CRM inquiries with solar capacity, system type, subsidy needs, and automated reference generation.
- **Site Survey**: Mobile-ready rooftop surveys with pitch, azimuth, shadow profiling, and checklist flags.
- **Dynamic Auto-BOM**: Capacity-driven BOM generation (panel count, inverter sizing, mounting rails, and DC/AC cables).
- **Sales & Subsidies**: Turnkey proposals with PM Surya Ghar subsidy offsets, 2.7-year payback calculation, and 5-stage milestone invoicing.
- **Serialized Inventory**: Barcode & serial number tracking for PV modules, inverters, and battery banks across staging and dispatch.
- **Installation & Testing**: Field crew work orders with 6-phase commissioning checklist and electrical QC logs (Voc, Isc, earth resistance < 5 Ohm).
- **Digital Warranty**: Cryptographic SHA-256 verified warranty certificates for 25-yr panel and 10-yr inverter coverage.
- **After-Sales & AMC**: Helpdesk ticketing for inverter fault alerts and scheduled solar cleaning agreements.
- **Job Costing & Profitability**: Real-time project costing with EBITDA margin health classification.
    """,
    'category': 'Operations/Solar EPC',
    'author': 'SolarFlow ERP Development Team',
    'website': 'https://github.com/solarflow-erp',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'crm',
        'sale_management',
        'stock',
        'account',
    ],
    'data': [
        'security/solarflow_security.xml',
        'security/ir.model.access.csv',
        'data/solarflow_sequence.xml',
        'data/solarflow_package_data.xml',
        'views/solarflow_dashboard_views.xml',
        'views/solarflow_menus.xml',
        'views/crm_lead_views.xml',
        'views/solarflow_survey_views.xml',
        'views/solarflow_package_views.xml',
        'views/solarflow_installation_views.xml',
        'views/solarflow_warranty_views.xml',
        'views/solarflow_service_views.xml',
        'views/solarflow_cost_views.xml',
        'reports/solarflow_reports.xml',
        'reports/solarflow_survey_report.xml',
    ],
    'demo': [
        'demo/solarflow_demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'solarflow_management/static/src/css/solarflow.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
