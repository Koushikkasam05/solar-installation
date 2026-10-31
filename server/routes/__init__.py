# -*- coding: utf-8 -*-
"""SolarFlow ERP - Route Blueprints Exporter."""
from server.routes.frontend import frontend_bp
from server.routes.auth_routes import auth_bp
from server.routes.dashboard_routes import dashboard_bp
from server.routes.lead_routes import lead_bp
from server.routes.survey_routes import survey_bp
from server.routes.order_routes import order_bp
from server.routes.stock_routes import stock_bp
from server.routes.install_routes import install_bp
from server.routes.warranty_routes import warranty_bp
from server.routes.cost_routes import cost_bp

__all__ = [
    'frontend_bp',
    'auth_bp',
    'dashboard_bp',
    'lead_bp',
    'survey_bp',
    'order_bp',
    'stock_bp',
    'install_bp',
    'warranty_bp',
    'cost_bp',
]
