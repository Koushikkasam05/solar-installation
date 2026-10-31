# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SolarFlowController(http.Controller):

    @http.route('/solarflow/health', type='json', auth='public', methods=['GET'])
    def health_check(self):
        return {
            'status': 'healthy',
            'system': 'SolarFlow ERP – Solar Installation Management System',
            'version': '20.0.1.0.0',
        }
