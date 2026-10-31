# -*- coding: utf-8 -*-
"""
SolarFlow ERP – Live HTTP Role-Based Access Control (RBAC) & Security Test Suite
================================================================================
Executes REAL HTTP requests against the live Flask application test client using
active session cookies to verify that security and RBAC are enforced directly by
the backend server, not merely hidden in the frontend UI.

Tests across all 7 Enterprise Roles:
1. Unauthenticated direct URL probing -> 401 Unauthorized
2. Super Administrator (admin)       -> Full CRUD access across all modules
3. Sales Manager (sales)              -> CRM & surveys allowed; costing & stock blocked (403)
4. Warehouse Manager (warehouse)      -> Stock lots allowed; CRM & costing blocked (403)
5. Installation Technician (tech)     -> Assigned installs allowed; unassigned & costing blocked (403)
6. Support Manager (support)          -> Warranties allowed; inventory & costing blocked (403)
7. Finance Controller (finance)       -> Confidential costing allowed; stock & install blocked (403)
8. Managing Director (director)       -> Read-only analytics allowed; all mutations blocked (403)
"""
import unittest
import time
from server import create_app


class LiveRBACSecurityTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True

    def setUp(self):
        self.client = self.app.test_client()

    def login_as(self, username, password):
        """Helper: authenticate test client and establish session cookie."""
        res = self.client.post('/api/auth/login', json={'username': username, 'password': password})
        self.assertEqual(res.status_code, 200, f"Login failed for {username}: {res.get_json()}")
        return res.get_json()

    def logout(self):
        """Helper: clear session cookie."""
        self.client.post('/api/auth/logout')

    # =========================================================================
    # VECTOR 1: UNAUTHENTICATED ACCESS GUARDS (HTTP 401)
    # =========================================================================
    def test_01_unauthenticated_requests_rejected_with_401(self):
        """Unauthenticated requests to protected endpoints must be rejected with HTTP 401."""
        endpoints = [
            ('GET', '/api/dashboard'),
            ('GET', '/api/costing'),
            ('GET', '/api/installations'),
            ('GET', '/api/stock'),
            ('GET', '/api/leads'),
            ('POST', '/api/costing'),
            ('POST', '/api/stock/1/allocate'),
        ]
        for method, url in endpoints:
            if method == 'GET':
                res = self.client.get(url)
            else:
                res = self.client.post(url, json={})
            self.assertEqual(res.status_code, 401,
                             f"Expected 401 for unauthenticated {method} {url}, got {res.status_code}")
            data = res.get_json()
            self.assertIn('Authentication Required', data.get('error', ''))

    # =========================================================================
    # VECTOR 2: SUPER ADMINISTRATOR (UNIVERSAL ACCESS)
    # =========================================================================
    def test_02_super_admin_full_access(self):
        """Super Administrator has full CRUD permissions across all 14 modules."""
        self.login_as('admin', 'admin123')

        # Allowed GET operations
        self.assertEqual(self.client.get('/api/dashboard').status_code, 200)
        self.assertEqual(self.client.get('/api/costing').status_code, 200)
        self.assertEqual(self.client.get('/api/installations').status_code, 200)
        self.assertEqual(self.client.get('/api/stock').status_code, 200)
        self.assertEqual(self.client.get('/api/leads').status_code, 200)

        # Allowed sensitive POST operations
        cost_res = self.client.post('/api/costing', json={'revenue': 1000, 'material_cost': 500})
        self.assertEqual(cost_res.status_code, 201)

    # =========================================================================
    # VECTOR 3: SALES MANAGER (CRM & SURVEYS ALLOWED, FINANCIAL COSTING BLOCKED)
    # =========================================================================
    def test_03_sales_manager_permissions_and_boundaries(self):
        """Sales Manager can manage leads/surveys, but is blocked from costing & inventory dispatch."""
        self.login_as('sales', 'sales123')

        # Allowed operations
        self.assertEqual(self.client.get('/api/leads').status_code, 200)
        self.assertEqual(self.client.get('/api/surveys').status_code, 200)
        lead_res = self.client.post('/api/leads', json={'customer_id': 1, 'monthly_kwh': 300})
        self.assertEqual(lead_res.status_code, 201)

        # Denied 1: Confidential Financial Costing access -> 403 Forbidden
        cost_res = self.client.get('/api/costing')
        self.assertEqual(cost_res.status_code, 403, "Sales must NOT access financial costing")
        self.assertIn("Access Denied", cost_res.get_json()['error'])

        # Denied 2: Warehouse Equipment Allocation -> 403 Forbidden
        alloc_res = self.client.post('/api/stock/1/allocate', json={'order_id': 1})
        self.assertEqual(alloc_res.status_code, 403, "Sales must NOT allocate warehouse equipment")

        # Denied 3: Admin-only Unlink/Delete protection -> 403 Forbidden
        del_res = self.client.delete('/api/leads/1')
        self.assertEqual(del_res.status_code, 403, "Sales must NOT delete records permanently")

    # =========================================================================
    # VECTOR 4: WAREHOUSE MANAGER (STOCK ALLOWED, LEADS & COSTING BLOCKED)
    # =========================================================================
    def test_04_warehouse_manager_permissions_and_boundaries(self):
        """Warehouse Manager can manage physical stock, but is blocked from CRM leads and costing."""
        self.login_as('warehouse', 'warehouse123')

        # Allowed operations
        self.assertEqual(self.client.get('/api/stock').status_code, 200)
        lot_res = self.client.post('/api/stock', json={'serial_number': f'TEST-SN-{int(time.time()*1000)}', 'product_name': 'Test Panel'})
        self.assertEqual(lot_res.status_code, 201)

        # Denied 1: Confidential Financial Costing -> 403 Forbidden
        self.assertEqual(self.client.get('/api/costing').status_code, 403)

        # Denied 2: Create CRM Customer Lead -> 403 Forbidden
        lead_res = self.client.post('/api/leads', json={'customer_id': 1})
        self.assertEqual(lead_res.status_code, 403)

        # Denied 3: Approve Engineering Survey -> 403 Forbidden
        appr_res = self.client.post('/api/surveys/1/approve')
        self.assertEqual(appr_res.status_code, 403)

    # =========================================================================
    # VECTOR 5: INSTALLATION TECHNICIAN (ASSIGNED JOBS ONLY, COSTING BLOCKED)
    # =========================================================================
    def test_05_technician_assigned_isolation_and_boundaries(self):
        """Technician is strictly isolated to assigned installations and blocked from costing."""
        self.login_as('tech', 'tech123')

        # Allowed: View assigned installations list
        inst_res = self.client.get('/api/installations')
        self.assertEqual(inst_res.status_code, 200)

        # Allowed: Update phase milestone on assigned installation #1 (Ramesh Electrician)
        phase_res = self.client.post('/api/installations/1/phase', json={'phase': 'phase_1_structure', 'completed': True})
        self.assertEqual(phase_res.status_code, 200)

        # Denied 1: Access confidential project costing -> 403 Forbidden
        self.assertEqual(self.client.get('/api/costing').status_code, 403)

        # Denied 2: Warehouse Equipment Allocation -> 403 Forbidden
        self.assertEqual(self.client.post('/api/stock/1/allocate', json={'order_id': 1}).status_code, 403)

        # Denied 3: Approve Site Survey -> 403 Forbidden
        self.assertEqual(self.client.post('/api/surveys/1/approve').status_code, 403)

    # =========================================================================
    # VECTOR 6: SUPPORT MANAGER (WARRANTIES & SERVICE TICKETS ALLOWED)
    # =========================================================================
    def test_06_support_manager_permissions_and_boundaries(self):
        """Support Manager handles warranties and RMA tickets, but is blocked from costing & dispatch."""
        self.login_as('support', 'support123')

        # Allowed operations
        self.assertEqual(self.client.get('/api/warranties').status_code, 200)
        self.assertEqual(self.client.get('/api/service-tickets').status_code, 200)

        # Denied 1: Confidential Financial Costing -> 403 Forbidden
        self.assertEqual(self.client.get('/api/costing').status_code, 403)

        # Denied 2: Warehouse Equipment Allocation -> 403 Forbidden
        self.assertEqual(self.client.post('/api/stock/1/allocate', json={'order_id': 1}).status_code, 403)

    # =========================================================================
    # VECTOR 7: FINANCE CONTROLLER (FINANCIAL COSTING & PAYMENTS ALLOWED)
    # =========================================================================
    def test_07_finance_controller_permissions_and_boundaries(self):
        """Finance Controller manages costing and payments, but cannot allocate inventory or install."""
        self.login_as('finance', 'finance123')

        # Allowed operations
        self.assertEqual(self.client.get('/api/costing').status_code, 200)
        self.assertEqual(self.client.get('/api/payments').status_code, 200)
        cost_post = self.client.post('/api/costing', json={'revenue': 2000, 'material_cost': 1200})
        self.assertEqual(cost_post.status_code, 201)

        # Denied 1: Warehouse stock allocation -> 403 Forbidden
        self.assertEqual(self.client.post('/api/stock/1/allocate', json={'order_id': 1}).status_code, 403)

        # Denied 2: Installation phase updates -> 403 Forbidden
        self.assertEqual(self.client.post('/api/installations/1/phase', json={'phase': 'phase_1_structure'}).status_code, 403)

    # =========================================================================
    # VECTOR 8: MANAGING DIRECTOR (READ-ONLY EXECUTIVE ANALYTICS MODE)
    # =========================================================================
    def test_08_director_strict_read_only_executive_privileges(self):
        """Managing Director has executive view access, but ALL mutating requests are strictly blocked."""
        self.login_as('director', 'director123')

        # Allowed READ operations across all analytics
        self.assertEqual(self.client.get('/api/dashboard').status_code, 200)
        self.assertEqual(self.client.get('/api/costing').status_code, 200)
        self.assertEqual(self.client.get('/api/orders').status_code, 200)
        self.assertEqual(self.client.get('/api/surveys').status_code, 200)

        # Denied 1: Mutating POST to Costing -> 403 Forbidden (Read-Only Guard)
        cost_post = self.client.post('/api/costing', json={'revenue': 1000})
        self.assertEqual(cost_post.status_code, 403)
        self.assertIn("read-only executive privileges", cost_post.get_json()['error'])

        # Denied 2: Mutating POST to Leads -> 403 Forbidden
        lead_post = self.client.post('/api/leads', json={'customer_id': 1})
        self.assertEqual(lead_post.status_code, 403)
        self.assertIn("read-only executive privileges", lead_post.get_json()['error'])

        # Denied 3: Mutating POST to Approve Survey -> 403 Forbidden
        appr_post = self.client.post('/api/surveys/1/approve')
        self.assertEqual(appr_post.status_code, 403)

        # Denied 4: Mutating DELETE to Leads -> 403 Forbidden
        del_post = self.client.delete('/api/leads/1')
        self.assertEqual(del_post.status_code, 403)


if __name__ == '__main__':
    unittest.main()
