# SolarFlow ERP – Database Relationship & ER Diagram

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    RES_PARTNER ||--o{ CRM_LEAD : "has inquiries"
    RES_PARTNER ||--o{ SALE_ORDER : "purchases"
    RES_PARTNER ||--o{ SOLARFLOW_SURVEY : "surveyed at"
    RES_PARTNER ||--o{ SOLARFLOW_INSTALLATION : "site owner"
    RES_PARTNER ||--o{ SOLARFLOW_WARRANTY : "beneficiary"
    RES_PARTNER ||--o{ SOLARFLOW_SERVICE_TICKET : "submits tickets"

    CRM_LEAD ||--o| SOLARFLOW_SURVEY : "converts to"
    CRM_LEAD {
        string solarflow_reference "Unique Lead Sequence"
        float solar_capacity_kw "Required System Capacity"
        selection solar_system_type "On-Grid, Hybrid, Off-Grid"
        boolean subsidy_required "Subsidy Flag"
        date expected_install_date "Target Installation"
        selection survey_status "Not Scheduled, Scheduled, Completed, Approved"
        float monthly_kwh "Monthly Electricity Units"
        float roof_area_sqft "Estimated Roof Size"
    }

    SOLARFLOW_SURVEY ||--o| SOLARFLOW_PACKAGE : "selects pre-engineered"
    SOLARFLOW_SURVEY ||--o{ SOLARFLOW_BOM_LINE : "auto-generates"
    SOLARFLOW_SURVEY ||--o| SALE_ORDER : "creates quotation"
    SOLARFLOW_SURVEY {
        string name "SURV/YYYY/XXXX"
        many2one partner_id "Customer"
        many2one lead_id "CRM Lead"
        selection roof_type "RCC, Metal, Tile, Ground"
        float usable_area_sqft "Shadow Free Area"
        float roof_tilt_deg "Tilt Angle"
        float azimuth_deg "Azimuth Orientation"
        selection shadow_profile "Clear, Partial, Heavy"
        float db_distance_meters "Distance to Main Panel"
        selection state "Draft, In Progress, Completed, Approved, Rejected"
    }

    SOLARFLOW_PACKAGE ||--|{ SOLARFLOW_PACKAGE_LINE : "contains default items"
    SOLARFLOW_PACKAGE {
        string name "Package Title"
        string code "Unique Code"
        float system_capacity_kw "kW Rating"
        selection system_type "On-Grid, Hybrid, Off-Grid"
        selection phase "Single-Phase, Three-Phase"
        monetary base_price "Turnkey Price"
        monetary max_subsidy_amount "Subsidy Cap"
    }

    SALE_ORDER ||--|| SOLARFLOW_INSTALLATION : "spawns on confirm"
    SALE_ORDER ||--|{ SOLARFLOW_PAYMENT_MILESTONE : "split schedule"
    SALE_ORDER {
        boolean is_solar_order "Solar Contract Flag"
        float solar_capacity_kw "Contracted kW"
        monetary subsidy_amount "Govt Subsidy"
        monetary net_customer_payable "Net Payable"
        float payback_years "Simple Payback Period"
    }

    SOLARFLOW_INSTALLATION ||--|{ STOCK_PICKING : "dispatches BOM"
    SOLARFLOW_INSTALLATION ||--|{ STOCK_LOT : "assigns serials"
    SOLARFLOW_INSTALLATION ||--|{ SOLARFLOW_WARRANTY : "generates upon handover"
    SOLARFLOW_INSTALLATION ||--|| SOLARFLOW_PROJECT_COST : "tracks margin"
    SOLARFLOW_INSTALLATION {
        string name "INST/YYYY/XXXX"
        many2one customer_id "Site Owner"
        many2one supervisor_id "Lead Engineer"
        many2many technician_ids "Field Crew"
        boolean phase_1_structure "Civil Done"
        boolean phase_2_modules "Panels Mounted"
        boolean phase_3_inverter "Inverter Wired"
        boolean phase_4_earthing "Earthing Done"
        boolean phase_5_testing "QC Tested"
        boolean phase_6_discom_sync "Net Meter Active"
        float test_earth_resistance "Measured Ohms"
        selection state "Draft, Scheduled, Structure, Cabling, Testing, Commissioned"
    }

    SOLARFLOW_WARRANTY {
        string name "WRNT/YYYY/XXXX"
        many2one installation_id "Commissioned Project"
        selection warranty_type "Module, Inverter, Workmanship"
        integer duration_years "Duration (Years)"
        date start_date "Start Date"
        date expiry_date "Calculated Expiry"
        string verification_hash "SHA256 Token"
    }

    SOLARFLOW_PROJECT_COST {
        string name "COST/YYYY/XXXX"
        many2one installation_id "Project"
        monetary contract_revenue "Contract Total"
        monetary bom_hardware_cost "Hardware Cost"
        monetary structure_cost "Mounting Rails Cost"
        monetary electrical_bos_cost "Cables & DB Cost"
        monetary labor_cost "Technician Fees"
        monetary discom_liaisoning_cost "DISCOM Fees"
        monetary gross_profit "Revenue - Cost"
        float profit_margin_pct "EBITDA Margin %"
    }
```

---

## 2. Model Relationship Matrix

| Source Model | Field Name | Target Model | Relation Type | On Delete | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `crm.lead` | `survey_ids` | `solarflow.survey` | `One2many` | Set Null | Track site surveys generated from lead |
| `solarflow.survey` | `lead_id` | `crm.lead` | `Many2one` | Set Null | Originating lead record |
| `solarflow.survey` | `partner_id` | `res.partner` | `Many2one` | Restrict | Customer receiving the survey |
| `solarflow.survey` | `package_id` | `solarflow.package` | `Many2one` | Restrict | Selected pre-engineered package |
| `solarflow.survey` | `bom_line_ids` | `solarflow.bom.line` | `One2many` | Cascade | Calculated Bill of Materials items |
| `sale.order` | `survey_id` | `solarflow.survey` | `Many2one` | Set Null | Survey baseline for quotation |
| `sale.order` | `milestone_ids`| `solarflow.payment.milestone` | `One2many` | Cascade | 5-stage milestone payment lines |
| `solarflow.installation` | `sale_order_id`| `sale.order` | `Many2one` | Restrict | Financial sales order reference |
| `solarflow.installation` | `technician_ids`| `res.users` | `Many2many` | Null | Field crew assigned to project |
| `solarflow.installation` | `warranty_ids` | `solarflow.warranty` | `One2many` | Cascade | Warranty certificates issued |
| `solarflow.installation` | `ticket_ids` | `solarflow.service.ticket`| `One2many` | Set Null | After-sales repair tickets |
| `solarflow.installation` | `cost_id` | `solarflow.project.cost` | `Many2one` | Cascade | Financial costing sheet |
| `solarflow.warranty` | `customer_id` | `res.partner` | `Many2one` | Restrict | Warranty beneficiary |
