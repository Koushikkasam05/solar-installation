# SolarFlow ERP – Comprehensive Installation & Setup Guide

This guide provides instructions to run and deploy **SolarFlow ERP** on both local development machines (Windows 11 / macOS / Linux) and production Linux VPS servers.

---

## 1. System Requirements

| Component | Minimum Requirement | Recommended Production |
| :--- | :--- | :--- |
| **OS** | Windows 10/11, Ubuntu 22.04/24.04 LTS, macOS | Ubuntu 24.04 LTS x86_64 |
| **Python** | Python 3.10 to 3.12 | Python 3.12 |
| **Database** | PostgreSQL 15 or 16 | PostgreSQL 16 (Dedicated container) |
| **RAM** | 4 GB | 8 GB+ |
| **CPU** | 2 Cores | 4 Cores |
| **Disk Space** | 10 GB SSD | 50 GB NVMe SSD |
| **Docker** | Docker Engine 24+ & Docker Compose v2+ | Docker Engine 27+ & Compose plugin |

---

## 2. Quick Local Verification (Without Docker)

You can verify all business logic, validation rules, constraints, formulas, and XML syntax immediately using the built-in Python test runners:

```bash
# 1. Run Core Module Automated Unit Tests (20 Tests)
python test_solarflow_modules.py

# 2. Run Customer Lead Automated Tests (6 Tests)
python test_solarflow_lead.py

# 3. Verify All 15 XML Views, Sequences, and Data Files
python -c "import os, xml.etree.ElementTree as ET; [ET.parse(os.path.join(r, f)) for r, d, fs in os.walk('addons/solarflow_management') for f in fs if f.endswith('.xml')]; print('All XML files parsed successfully with zero syntax errors!')"

# 4. Run Interactive 15-Stage Solar EPC Simulator
python demo_solar_cli.py
```

---

## 3. Local Development with Docker Compose

When Docker Desktop is installed and running on your host:

### Step 1: Environment Configuration
Copy the safe `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Ensure ports `8069` (web), `8072` (longpolling), and `5432` (database) are available.

### Step 2: Start the Containers
```bash
docker compose up -d
```
Docker Compose starts:
- **`solarflow-db`**: PostgreSQL 15-alpine database with persistent volume `solarflow_db_data`.
- **`solarflow-web`**: Odoo Community with persistent filestore volume `solarflow_web_data` and custom module mounted from `./addons`.

### Step 3: Access Odoo & Install the Module
1. Open your browser and navigate to: `http://localhost:8069`
2. Create or select a database (e.g. `solarflow_db`).
3. Log in with your configured admin credentials.
4. Navigate to **Apps** menu.
5. Click **Update Apps List** in the top navigation bar.
6. Search for `SolarFlow ERP` or `solarflow_management`.
7. Click **Activate / Install**.
8. The top navigation bar will now display the **SolarFlow ERP** icon and full menu suite!

---

## 4. Production Linux VPS Deployment

For full production deployment instructions with Nginx, SSL certificates, automated database backups, and systemd restart policies, refer to the [Deployment Guide](file:///c:/Solar_installation/docs/deployment_guide.md).
