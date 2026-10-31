# SolarFlow ERP – User Roles & Security Access Matrix (RBAC)

SolarFlow ERP enforces a strict **Role-Based Access Control (RBAC)** architecture configured through native Odoo security groups, access control lists (`ir.model.access.csv`), and multi-tenant record rules (`ir.rule`).

---

## 1. The 6 User Roles

| # | Role Name | Group XML ID | Primary Responsibilities & Functional Scope |
| :-: | :--- | :--- | :--- |
| **1** | **Solar Administrator** | `group_solarflow_admin` | Full system access across all models, configuration settings, user management, and automated sequences. |
| **2** | **Sales Manager** | `group_solarflow_sales_manager` | Customer leads, site surveys, solar packages, quotation generation, and sales order contracts. |
| **3** | **Warehouse Manager** | `group_solarflow_warehouse_manager` | Hardware inventory, stock quants, serial number tracking (`stock.lot`), and dispatch gatepasses (`stock.picking`). |
| **4** | **Installation Technician** | `group_solarflow_technician` | Mobile-friendly field execution of assigned installations, 6-phase checklist milestones, electrical QC test logs, and customer sign-off. |
| **5** | **Support Manager** | `group_solarflow_support_manager` | Digital warranty certificates, RMA replacement claims, after-sales service tickets, replacement parts consumption, and AMC agreements. |
| **6** | **Director** | `group_solarflow_director` | Executive command center, read-only analytics across all projects, financial job costing, EBITDA gross margins, and profit leakage alerts. |

---

## 2. Group Hierarchy & Inheritance

```
group_solarflow_admin (Solar Administrator)
  ├── group_solarflow_director (Director)
  ├── group_solarflow_sales_manager (Sales Manager)
  │     └── group_solarflow_technician (Installation Technician)
  ├── group_solarflow_warehouse_manager (Warehouse Manager)
  └── group_solarflow_support_manager (Support Manager)
```

---

## 3. Detailed Model Access Matrix (`ir.model.access.csv`)

| Model Technical ID | Model Description | Tech | Sales Mgr | WH Mgr | Support Mgr | Director | Admin |
| :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `solarflow.survey` | Site Surveys | R/W | CRUD | - | - | R | CRUD |
| `solarflow.package` | Solar Packages & BOM | R | CRUD | - | - | R | CRUD |
| `solarflow.package.line` | Package BOM Lines | - | CRUD | - | - | R | CRUD |
| `sale.order` | Solar Sales Orders | - | CRUD | R | - | R | CRUD |
| `stock.lot` | Serialized Equipment | R | R | CRUD | R | R | CRUD |
| `stock.picking` | Material Dispatches | - | - | CRUD | - | R | CRUD |
| `solarflow.installation` | Field Installations | R/W* | CRUD | R/W | - | R | CRUD |
| `solarflow.warranty` | Digital Warranties | R | - | - | CRUD | R | CRUD |
| `solarflow.service.ticket` | Service Tickets | R/W | - | - | CRUD | R | CRUD |
| `solarflow.service.part.line`| Replacement Parts | CRUD | - | - | CRUD | R | CRUD |
| `solarflow.project.cost` | Job Costing & Margins | **NO** | **NO** | **NO** | **NO** | **R** | **CRUD** |
| `solarflow.dashboard` | Executive Dashboard | R/W | R/W | R/W | R/W | R/W | CRUD |

*Legend: CRUD = Create, Read, Update, Delete | R = Read Only | R/W = Read and Write | - = No Access*

---

## 4. Multi-Tenant Record Rules (`ir.rule`)

### Rule 1: Technician Assignment Isolation
- **Target Model:** `solarflow.installation`
- **Group:** `group_solarflow_technician`
- **Domain Filter:**
  ```python
  ['|', ('technician_id', '=', user.id), ('technician_ids', 'in', [user.id])]
  ```
- **Business Purpose:** Technicians only see and edit installation projects where they are assigned as the Lead Technician or Crew Member. They cannot browse or view projects assigned to other field crews.

### Rule 2: Management Full Installation Visibility
- **Target Model:** `solarflow.installation`
- **Groups:** `group_solarflow_admin`, `group_solarflow_director`, `group_solarflow_sales_manager`, `group_solarflow_warehouse_manager`, `group_solarflow_support_manager`
- **Domain Filter:** `[(1, '=', 1)]`
- **Business Purpose:** Management roles have company-wide visibility across all installation projects.

### Rule 3: Confidential Financial Information Gate
- **Target Model:** `solarflow.project.cost`
- **Groups:** `group_solarflow_director`, `group_solarflow_admin`
- **Domain Filter:** `[(1, '=', 1)]`
- **Business Purpose:** Strictly enforces requirement 7 of Project Costing: **"Restrict financial information to authorized roles."** Sales Executives, Field Technicians, Warehouse Staff, and Support Managers have zero access to contractor labor rates, procurement costs, gross profit figures, or profit leakage notifications.
