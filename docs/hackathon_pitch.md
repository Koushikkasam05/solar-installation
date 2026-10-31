# SolarFlow ERP – 5-7 Minute Hackathon Demonstration Pitch Script

**Target Audience:** Hackathon Judges, Solar EPC Executives, Odoo Community Architects  
**Presenter Tone:** Authoritative, confident, technical, metrics-driven  
**Total Running Time:** 6 Minutes 30 Seconds  

---

## ⏱️ Minute 0:00 - 0:45 | 1. The Business Problem & The $40B Rooftop Solar EPC Chaos

> *"Good afternoon, judges. Rooftop solar is experiencing exponential 45% year-over-year global growth, driven by government initiatives like PM Surya Ghar. Yet, 85% of solar EPC contractors still manage their business using fragmented tools: WhatsApp for field photos, Excel for site surveys, paper cards for warranties, and disconnected tally sheets for job costing.*
> 
> *The consequences are devastating:*
> 1. *Rooftop surveys approved without checking structural or shadow viability, resulting in panels getting installed in shade.*
> 2. *Equipment dispatched to sites before customer advance payments are collected, creating fatal cash-flow freezes.*
> 3. *Subcontractor field crews cutting corners on grounding, leaving dangerous high-impedance earth pits ($>5\,\Omega$) that blow $2,000 inverters on the first lightning surge.*
> 4. *Untracked equipment serial numbers, forcing companies to honor expensive warranty repairs on hardware they never supplied!*
> 5. *Blind profit leakage: projects running 20% over budget with zero management visibility until the bank account is empty.*
> 
> *Today, we present **SolarFlow ERP** — the first end-to-end solar EPC management system built natively on Odoo."*

---

## ⏱️ Minute 0:45 - 1:30 | 2. The SolarFlow Solution & Executive Dashboard

> *(Screen share: SolarFlow Executive Dashboard)*
> 
> *"SolarFlow transforms this fragmented lifecycle into a single, tightly controlled pipeline. Here is our live **Executive Dashboard**, driven entirely by real database metrics — zero fake numbers.*
> 
> *In a single view, our Solar Administrator and Director see 12 real-time KPIs: Active Projects, Pending Leads, Unapproved Surveys, Confirmed Orders, Scheduled Installations, Active Warranties, Open Service Tickets, and actual Gross Project Profit.*
> 
> *Every card is interactive — clicking 'Pending Surveys' takes us immediately to the operational queue."*

---

## ⏱️ Minute 1:30 - 2:30 | 3. Customer Lead to Site Survey & Dynamic Auto-BOM

> *(Screen share: Site Survey Form & Solar Package)*
> 
> *"Let's trace our complete 3kW On-Grid demonstration scenario for Dr. Rajesh Sharma.*
> 
> *Our field surveyor uses the mobile-responsive Site Survey interface to record exact rooftop parameters: RCC flat roof, 12-degree tilt angle, south-facing azimuth, and 20 meters of cable distance. Notice our first strict server-side validation gate:*
> - *An incomplete survey **cannot** be approved by the system.*
> - *If a survey is rejected due to shading, our mandatory rejection wizard forces documentation of the engineering reason.*
> 
> *Once approved by the Chief Engineer, the system matches our 3kW On-Grid Solar Package. Watch our **Automatic BOM Generation**: it dynamically pulls current component prices from inventory — calculating 6 Mono PERC panels, a 3kW Smart Inverter, mounting rails, and safety BOS — achieving dynamic pricing with **zero hardcoding** in Python!"*

---

## ⏱️ Minute 2:30 - 3:30 | 4. 50% Advance Payment Gate & Serialized Warehouse Dispatch

> *(Screen share: Sales Order & Material Dispatch Picking)*
> 
> *"Here is our Turnkey Proposal with the PM Surya Ghar subsidy offset ($940) and a simple 2.7-year payback calculation.*
> 
> *Now watch our second critical business rule in action: **The 50% Advance Payment Gate**.*
> *When we open the warehouse delivery picking, the warehouse manager cannot click 'Validate'. The system blocks dispatch with an error explaining that customer advance payment has not reached 50%. Once accounting reconciles the payment, dispatch permission unlocks.*
> 
> *Next, our third validation gate: **Serial Number Tracking**.*
> *Our inverter (`INV-GROWATT-3KW-9901`) and modules are barcode-scanned. Our unique single-allocation constraint guarantees that an active serial number cannot be accidentally assigned to two different installation sites!"*

---

## ⏱️ Minute 3:30 - 4:45 | 5. Installation Readiness Score & Mandatory Electrical QC

> *(Screen share: Installation Project Form)*
> 
> *"Now we move to field commissioning. Here is our first unique innovation: **The Installation Readiness Score (out of 100)**.*
> 
> *Before dispatching a crew, SolarFlow automatically calculates readiness across 5 critical dimensions (20 points each):*
> 1. *Survey Approved: +20*
> 2. *Payment Policy Satisfied: +20*
> 3. *Required Stock Available: +20*
> 4. *Equipment Allocated: +20*
> 5. *Technician Assigned: +20*
> 
> *Notice: The score is 100/100 — fully ready!*
> 
> *The field technician logs execution through our 6-phase checklist: Structure, Modules, Inverter, Earthing, Megger Testing, and Net Meter Sync.*
> 
> *Now notice our strictest safety gate: **Electrical QC Testing**.*
> *Standard solar safety mandates an Earth Pit Resistance $\le 5.0\,\Omega$. If a technician tries to complete the project with an earth resistance of $6.5\,\Omega$, the system **blocks completion with a safety hazard error**! Only when safe earthing ($\le 5.0\,\Omega$) and mandatory Customer Sign-Off are recorded can the project be marked completed."*

---

## ⏱️ Minute 4:45 - 5:45 | 6. Digital Warranties, After-Sales Tickets & Serial-to-Warranty Lifecycle

> *(Screen share: Digital Warranty & Service Ticket Form)*
> 
> *"Upon completion, SolarFlow automatically triggers two critical actions:*
> 1. *It issues **Digital Warranty Certificates** connected directly to the equipment serial numbers — 2 years for the Inverter, 20 years for the Solar Panels — sealed with an immutable SHA-256 cryptographic verification token.*
> 2. *It unlocks our second unique innovation: **The Serial-to-Warranty Lifecycle Timeline**.*
> *Looking at any hardware serial number, you see a complete audit trail: Purchase $\rightarrow$ Warehouse Receipt $\rightarrow$ Reservation $\rightarrow$ Dispatch $\rightarrow$ Installation $\rightarrow$ Warranty $\rightarrow$ Service History.*
> 
> *Now, when customer Dr. Sharma reports an issue, our service technician simply enters the serial number. SolarFlow automatically identifies the customer, site, and active warranty.*
> 
> *Watch our billing logic:*
> - *For an internal MPPT inverter fault (OEM defect), the system recognizes active warranty coverage and bills the customer **$0.00**.*
> - *For external lightning surge damage, the system recognizes a non-covered fault and automatically calculates parts and labor charges ($85.00).*
> - *And the ticket cannot be closed without customer sign-off confirmation!"*

---

## ⏱️ Minute 5:45 - 6:30 | 7. Real-Time Job Costing & Profit Leakage Alerting

> *(Screen share: Project Costing Form)*
> 
> *"Finally, the financial truth: **Project Cost and Profitability Management**.*
> 
> *SolarFlow tracks Material, Technician Labor, Transportation, Additional Material, and Other Expenses.*
> - *Total Cost $= \text{Material} + \text{Labour} + \text{Transport} + \text{Other Expenses} = \$1,500$.*
> - *Gross Profit $= \text{Revenue } (\$2,040) - \text{Total Cost } (\$1,500) = \$540$.*
> - *Gross Margin $= 26.47\%$ (with robust zero-revenue division protection).*
> 
> *And our final feature: **Configurable Profit Leakage Alerts**.*
> *If actual project expenses exceed the estimated budget by more than our configured 10% threshold, SolarFlow automatically fires high-priority alert activities to the Director and Solar Manager.*
> 
> *Furthermore, this financial sheet is protected by our RBAC rules — only the Director and Solar Administrator can view project costing; field technicians and sales executives have zero access."*

---

## ⏱️ Minute 6:30 - 7:00 | 8. Conclusion, Testing Evidence & Deployment Readiness

> *"To summarize:*
> - *26 automated tests passing in under 0.04 seconds.*
> - *15 XML view and data files verified with zero syntax errors.*
> - *Role-Based Access Control verified across 6 distinct user groups.*
> - *Complete 3kW On-Grid showcase scenario seeded with 10 demo customers and 10 leads.*
> - *Docker and Linux VPS deployment configurations verified.*
> 
> *SolarFlow ERP turns rooftop solar EPC from uncoordinated chaos into a predictable, safe, and highly profitable enterprise operation.*
> 
> *Thank you, judges! We welcome your questions."*
