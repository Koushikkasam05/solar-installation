# SunPower Nexus Audit Report

## Test Results

- **Passed:** 43 application tests in the root Python test suite.
- **Excluded from the application suite:** `addons/solarflow_management/tests/test_lead_management.py`
  requires an Odoo runtime and `odoo` Python package.
- **Running application verified:**
  - unauthenticated dashboard API returned `401`.
  - demo admin login returned the authenticated admin role and CSRF token.
  - authenticated admin dashboard returned data from the Flask database.
- **Mocks:** Existing unit tests use mocked database/module boundaries where stated
  by their source.

## Security Controls Added

- Server-side Flask sessions and password hashing.
- Approved-user authentication and role-aware authorization.
- CSRF validation for authenticated state-changing requests.
- Server-authenticated order transition roles.
- Protected staff dashboards, B2B administration, and management analysis APIs.

## Demo Accounts

All demo accounts use password `Solar@123` unless
`SUNPOWER_DEMO_PASSWORD` is configured.

| Account | Role |
| --- | --- |
| customer@sunpower.local | Customer |
| sales@sunpower.local | Sales |
| warehouse@sunpower.local | Warehouse |
| technician@sunpower.local | Technician |
| support@sunpower.local | Support |
| admin@sunpower.local | Administrator |

## Startup

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Database Reset

Stop the application, then remove the generated SQLite database:

```powershell
Remove-Item .\data\solarflow.db -ErrorAction SilentlyContinue
python app.py
```

The application recreates the schema and demo accounts.

## Known Limitations and External Credentials

- The rule-based management agent is active; external LLM responses require an
  integration and API credentials.
- RAG retrieval requires a configured document/vector service.
- GSTIN verification requires an approved GST verification provider.
- Google Solar imagery and live satellite measurement require provider credentials.
- SMS and email verification providers are not configured.
- Odoo-addon tests require an Odoo runtime and are separate from the Flask application suite.
