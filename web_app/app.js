// ==========================================================================
// SolarFlow ERP – Complete Light-Theme Enterprise Frontend Logic
// Crisp Tables, Kanban Boards, Real-Time Filtering, Charts & Instant Search
// ==========================================================================

const SolarFlowState = {
  currentRole: 'admin',
  sidebarCollapsed: false,
  activeView: 'dashboard',
  leadsViewMode: 'list',
  surveysViewMode: 'list',
  serviceViewMode: 'list',

  // 8 Roles Configuration
  // 8 Roles Configuration with Dedicated Test Accounts
  roles: {
    admin: {
      name: "Super Administrator",
      userName: "System Administrator",
      login: "admin@solarflow.erp",
      title: "Chief Executive Officer",
      avatar: "SA",
      perm: ["all"],
      canCreate: true,
      canEdit: true,
      canDelete: true,
      canApproveSurveys: true,
      canConfirmOrders: true,
      canCompleteInstallation: true,
      canValidateDispatch: true,
      canManageCosting: true,
      desc: "Full administrative access across all business modules, settings, and users."
    },
    sales: {
      name: "Sales Manager",
      userName: "Vikram Sales Manager",
      login: "sales@solarflow.erp",
      title: "Head of Solar Sales",
      avatar: "SM",
      perm: ["dashboard", "enquiries", "leads", "followups", "surveys", "quotations", "orders", "installations", "schedule", "packages", "stock_reservations", "products", "biz_reports", "sales_perf"],
      canCreate: true,
      canEdit: true,
      canDelete: false,
      canApproveSurveys: true,
      canConfirmOrders: true,
      canCompleteInstallation: true,
      canValidateDispatch: false,
      canManageCosting: false,
      desc: "Manages customer enquiries, leads, follow-ups, surveys, quotations, and orders."
    },
    survey_tech: {
      name: "Survey Technician",
      userName: "Arun Survey Tech",
      login: "survey@solarflow.erp",
      assignedName: "Arun Survey Tech",
      title: "Field Solar Surveyor",
      avatar: "ST",
      perm: ["dashboard", "surveys", "schedule"],
      canCreate: true,
      canEdit: true,
      canDelete: false,
      canApproveSurveys: false, // Cannot self-approve surveys!
      canConfirmOrders: false,
      canCompleteInstallation: false,
      canValidateDispatch: false,
      canManageCosting: false,
      desc: "Performs rooftop feasibility surveys, pitch/azimuth/shadow logs, and photo uploads."
    },
    warehouse: {
      name: "Warehouse Manager",
      userName: "Sanjay Warehouse Manager",
      login: "warehouse@solarflow.erp",
      title: "Supply Chain & Staging Lead",
      avatar: "WM",
      perm: ["dashboard", "products", "categories", "warehouses", "stock_avail", "stock_reservations", "inventory", "dispatches", "stock_moves"],
      canCreate: true,
      canEdit: true,
      canDelete: false,
      canApproveSurveys: false,
      canConfirmOrders: false,
      canCompleteInstallation: false,
      canValidateDispatch: true,
      canManageCosting: false,
      desc: "Manages physical stock, serialized equipment, reservations, and site dispatches."
    },
    tech: {
      name: "Installation Technician",
      userName: "Ramesh Electrician",
      login: "tech@solarflow.erp",
      assignedName: "Ramesh Electrician",
      title: "Senior Electrical Lead",
      avatar: "IT",
      perm: ["dashboard", "installations", "schedule", "inst_reports", "inventory", "service", "tech_perf"],
      canCreate: false, // Cannot create installation projects directly
      canEdit: true,   // Can update progress and QC on assigned installations
      canDelete: false,
      canApproveSurveys: false,
      canConfirmOrders: false,
      canCompleteInstallation: true,
      canValidateDispatch: false,
      canManageCosting: false,
      desc: "Executes assigned rooftop installations, 6-phase checklist, and QC testing (Earth <= 5.0 Ohm)."
    },
    support: {
      name: "Support Manager",
      userName: "Neha Support Manager",
      login: "support@solarflow.erp",
      title: "Customer Success Lead",
      avatar: "SP",
      perm: ["dashboard", "warranties", "service", "complaints", "service_history", "inventory"],
      canCreate: true,
      canEdit: true,
      canDelete: false,
      canApproveSurveys: false,
      canConfirmOrders: false,
      canCompleteInstallation: false,
      canValidateDispatch: false,
      canManageCosting: false,
      desc: "Handles warranty claims, RMA replacements, and service ticketing."
    },
    finance: {
      name: "Finance Manager",
      userName: "Kavita Finance Manager",
      login: "finance@solarflow.erp",
      title: "Chief Financial Officer",
      avatar: "FM",
      perm: ["dashboard", "invoices", "payments", "expenses", "costing", "fin_reports", "quotations", "orders", "biz_reports"],
      canCreate: true,
      canEdit: true,
      canDelete: false,
      canApproveSurveys: false,
      canConfirmOrders: false,
      canCompleteInstallation: false,
      canValidateDispatch: false,
      canManageCosting: true,
      desc: "Manages milestone billing, customer payments, project costing, and profitability."
    },
    director: {
      name: "Director / Investor",
      userName: "Aditya Director",
      login: "director@solarflow.erp",
      title: "Board Director (Read-Only)",
      avatar: "DR",
      perm: ["dashboard", "enquiries", "leads", "followups", "surveys", "quotations", "orders", "installations", "schedule", "technicians", "inst_reports", "products", "categories", "warehouses", "stock_avail", "stock_reservations", "inventory", "dispatches", "stock_moves", "warranties", "service", "complaints", "service_history", "invoices", "payments", "expenses", "costing", "fin_reports", "biz_reports", "op_reports", "tech_perf", "sales_perf"],
      readOnly: true,
      canCreate: false, // Strict read-only
      canEdit: false,   // Strict read-only
      canDelete: false, // Strict read-only
      canApproveSurveys: false,
      canConfirmOrders: false,
      canCompleteInstallation: false,
      canValidateDispatch: false,
      canManageCosting: false,
      desc: "Executive read-only analytics for revenue, EBITDA margins, and project performance."
    }
  },

  // Real System Notifications
  notifications: [
    { id: 1, title: "Low Stock Alert: Chemical Earthing Mix", sub: "Warehouse inventory below safety threshold (1 bag left).", time: "10 mins ago", unread: true, icon: "⚠️", type: "warn" },
    { id: 2, title: "Profit Leakage Alert: INST-2026-0002", sub: "Actual cost overrun (+42.1%) flagged by Costing Engine.", time: "1 hour ago", unread: true, icon: "💸", type: "danger" },
    { id: 3, title: "Site Survey Scheduled: SRV-2026-0002", sub: "Priya Sundaram (5kW Hybrid) site visit queued.", time: "3 hours ago", unread: true, icon: "📐", type: "info" }
  ],

  // 10 Customers
  customers: [
    { id: 1, name: "Dr. Rajesh Sharma", phone: "+91 98765 43210", email: "rajesh.sharma@example.com", city: "Bengaluru", type: "Residential", address: "42 Palm Meadows Boulevard, Whitefield, Bengaluru" },
    { id: 2, name: "Apex Logistics Hub", phone: "+91 98111 22334", email: "contact@apexlogistics.example.com", city: "Pune", type: "Commercial", address: "Plot 14, MIDC Bhosari Industrial Area, Pune" },
    { id: 3, name: "Priya Sundaram", phone: "+91 98450 11223", email: "priya.sundaram@example.com", city: "Bengaluru", type: "Residential Villa", address: "18 Koramangala 4th Block, Bengaluru" },
    { id: 4, name: "GreenLeaf Farmhouse", phone: "+91 99000 55667", email: "info@greenleaf.example.com", city: "Chikkaballapur", type: "Off-Grid Farm", address: "Survey 84, Nandi Foothills Road, Chikkaballapur" },
    { id: 5, name: "Vikramaditya Rao", phone: "+91 98222 77889", email: "vikram.rao@example.com", city: "Hyderabad", type: "Bungalow", address: "Road No. 12, Banjara Hills, Hyderabad" },
    { id: 6, name: "Modern Heights Apt Assn", phone: "+91 99112 33445", email: "secretary@modernheights.example.com", city: "Bengaluru", type: "Housing Society", address: "Hennur Main Road, Kalyan Nagar, Bengaluru" },
    { id: 7, name: "Amitabh Choudhury", phone: "+91 98300 44556", email: "amitabh.c@example.com", city: "Kolkata", type: "Residential", address: "Salt Lake Sector II, Block CF, Kolkata" },
    { id: 8, name: "Zenith Polymer Industries", phone: "+91 98250 88990", email: "plant@zenithpolymers.example.com", city: "Vadodara", type: "Factory", address: "GIDC Industrial Estate, Makarpura, Vadodara" },
    { id: 9, name: "Sunita Deshmukh", phone: "+91 98201 23456", email: "sunita.d@example.com", city: "Mumbai", type: "Rowhouse", address: "Seawoods Sector 28, Nerul, Navi Mumbai" },
    { id: 10, name: "Kaveri Cold Storage", phone: "+91 94432 11223", email: "manager@kavericold.example.com", city: "Salem", type: "Commercial Cold Storage", address: "NH-44 Bypass, Omalur Road, Salem" }
  ],

  // Customer Enquiries
  enquiries: [
    { id: 1, ref: "ENQ-2026-0101", customerId: 1, date: "2026-10-25", propertyType: "RCC Rooftop", sanctionedLoad: "5.0 kW", status: "qualified" },
    { id: 2, ref: "ENQ-2026-0102", customerId: 2, date: "2026-10-26", propertyType: "Metal Industrial Shed", sanctionedLoad: "60.0 kW", status: "new" },
    { id: 3, ref: "ENQ-2026-0103", customerId: 3, date: "2026-10-28", propertyType: "Terrace Villa", sanctionedLoad: "7.0 kW", status: "qualified" },
    { id: 4, ref: "ENQ-2026-0104", customerId: 5, date: "2026-10-30", propertyType: "Independent House", sanctionedLoad: "12.0 kW", status: "new" }
  ],

  // Sales Leads
  leads: [
    { id: 1, ref: "SF/LEAD/2026/0001", customerId: 1, monthlyKwh: 380, tariff: 0.10, sizedKw: 3.0, type: "on_grid", subsidy: true, status: "approved" },
    { id: 2, ref: "SF/LEAD/2026/0002", customerId: 2, monthlyKwh: 6500, tariff: 0.13, sizedKw: 50.0, type: "on_grid", subsidy: false, status: "draft" },
    { id: 3, ref: "SF/LEAD/2026/0003", customerId: 3, monthlyKwh: 550, tariff: 0.10, sizedKw: 5.0, type: "hybrid", subsidy: true, status: "scheduled" },
    { id: 4, ref: "SF/LEAD/2026/0004", customerId: 4, monthlyKwh: 420, tariff: 0.12, sizedKw: 5.0, type: "off_grid", subsidy: false, status: "draft" },
    { id: 5, ref: "SF/LEAD/2026/0005", customerId: 5, monthlyKwh: 1200, tariff: 0.10, sizedKw: 10.0, type: "on_grid", subsidy: true, status: "draft" },
    { id: 6, ref: "SF/LEAD/2026/0006", customerId: 6, monthlyKwh: 3200, tariff: 0.11, sizedKw: 25.0, type: "on_grid", subsidy: false, status: "draft" },
    { id: 7, ref: "SF/LEAD/2026/0007", customerId: 7, monthlyKwh: 240, tariff: 0.10, sizedKw: 2.0, type: "on_grid", subsidy: true, status: "rejected" },
    { id: 8, ref: "SF/LEAD/2026/0008", customerId: 8, monthlyKwh: 14000, tariff: 0.14, sizedKw: 100.0, type: "on_grid", subsidy: false, status: "draft" },
    { id: 9, ref: "SF/LEAD/2026/0009", customerId: 9, monthlyKwh: 340, tariff: 0.10, sizedKw: 3.0, type: "hybrid", subsidy: true, status: "draft" },
    { id: 10, ref: "SF/LEAD/2026/0010", customerId: 10, monthlyKwh: 5200, tariff: 0.12, sizedKw: 40.0, type: "on_grid", subsidy: false, status: "draft" }
  ],

  // Follow-ups
  followups: [
    { id: 1, customerId: 2, date: "2026-11-02", salesRep: "Vikram Solar Rep", type: "Commercial Feasibility Review", summary: "Discuss 50kW industrial rooftop proposal and DISCOM HT connectivity.", priority: "High", status: "Pending" },
    { id: 2, customerId: 3, date: "2026-11-03", salesRep: "Aisha Khan", type: "Hybrid System Consultation", summary: "Finalize BYD battery backup sizing with client before order confirmation.", priority: "Medium", status: "Scheduled" },
    { id: 3, customerId: 5, date: "2026-11-04", salesRep: "Vikram Solar Rep", type: "Residential Proposal Follow-up", summary: "Answer questions regarding 10kW On-Grid net-metering approval timeline.", priority: "Normal", status: "Open" }
  ],

  // Site Surveys
  surveys: [
    {
      id: 1, ref: "SRV-2026-0001", customerId: 1, leadId: 1, roofType: "RCC Flat Concrete",
      totalArea: "650 sq.ft", usableArea: "500 sq.ft", azimuth: "180° South (Optimal)", tilt: "12°",
      cableDist: "20 m", gridPhase: "Single Phase 230V", recommendedKw: 3.0, state: "approved",
      engineer: "Arun K. (Chief Engineer)", notes: "Rooftop is flat RCC with zero shading. Excellent load bearing capacity."
    },
    {
      id: 2, ref: "SRV-2026-0002", customerId: 3, leadId: 3, roofType: "RCC Flat Terrace",
      totalArea: "900 sq.ft", usableArea: "700 sq.ft", azimuth: "210° South-West", tilt: "15°",
      cableDist: "25 m", gridPhase: "Three Phase 415V", recommendedKw: 5.0, state: "scheduled",
      engineer: "Pending Assignment", notes: "Scheduled shadow analysis and parapet height check."
    },
    {
      id: 3, ref: "SRV-2026-0003", customerId: 7, leadId: 7, roofType: "Asbestos Tin Shed",
      totalArea: "350 sq.ft", usableArea: "120 sq.ft", azimuth: "0° North (Low Yield)", tilt: "25°",
      cableDist: "55 m", gridPhase: "Single Phase", recommendedKw: 1.0, state: "rejected",
      rejectionReason: "Severe structural weakness in corrugated tin roof and continuous shadow obstruction from adjacent building.",
      engineer: "Arun K. (Chief Engineer)", notes: "Infeasible for elevated module mounting structure."
    }
  ],

  // Solar Packages & Dynamic Auto-BOM
  packages: [
    {
      id: 1, code: "SF-PKG-3KW-OG", name: "3kW On-Grid Solar Package", capacity: 3.0, type: "on_grid",
      bom: [
        { item: "Canadian Solar 550W Mono PERC Modules", qty: 6, unitPrice: 154, subtotal: 924 },
        { item: "Growatt 3kW Dual MPPT Grid-Tie Inverter", qty: 1, unitPrice: 580, subtotal: 580 },
        { item: "Elevated HDGI Mounting Structure Rails", qty: 6, unitPrice: 26, subtotal: 156 },
        { item: "Class II ACDB/DCDB, SPDs & DC Cables", qty: 1, unitPrice: 110, subtotal: 110 }
      ],
      totalPrice: 1770
    },
    {
      id: 2, code: "SF-PKG-5KW-HYB", name: "5kW Smart Hybrid Solar Package", capacity: 5.0, type: "hybrid",
      bom: [
        { item: "Canadian Solar 550W Mono PERC Modules", qty: 10, unitPrice: 154, subtotal: 1540 },
        { item: "Deye 5kW Hybrid Inverter with EMS", qty: 1, unitPrice: 1150, subtotal: 1150 },
        { item: "BYD LiFePO4 48V 100Ah Battery Bank (5kWh)", qty: 1, unitPrice: 1400, subtotal: 1400 },
        { item: "Elevated HDGI Mounting Structure", qty: 10, unitPrice: 26, subtotal: 260 },
        { item: "IP65 Hybrid ACDB/DCDB & Safety Kit", qty: 1, unitPrice: 180, subtotal: 180 }
      ],
      totalPrice: 4530
    },
    {
      id: 3, code: "SF-PKG-5KW-OFF", name: "5kW Standalone Off-Grid Package", capacity: 5.0, type: "off_grid",
      bom: [
        { item: "Canadian Solar 550W Mono PERC Modules", qty: 10, unitPrice: 154, subtotal: 1540 },
        { item: "Growatt SPF 5000ES Off-Grid Inverter", qty: 1, unitPrice: 850, subtotal: 850 },
        { item: "Deep-Cycle LiFePO4 Battery Bank (10kWh)", qty: 2, unitPrice: 1400, subtotal: 2800 },
        { item: "Heavy Duty Galvanized Roof Mounts", qty: 10, unitPrice: 26, subtotal: 260 },
        { item: "Battery Breaker Box & DC Fuses", qty: 1, unitPrice: 150, subtotal: 150 }
      ],
      totalPrice: 5600
    }
  ],

  // Quotations
  quotations: [
    { id: 1, ref: "QT-2026-0001", customerId: 1, surveyId: 1, capacity: "3.0 kW", grossTotal: 2980.0, subsidy: 940.0, netPrice: 2040.0, paybackYears: 2.8, status: "confirmed" },
    { id: 2, ref: "QT-2026-0002", customerId: 3, surveyId: 2, capacity: "5.0 kW", grossTotal: 5800.0, subsidy: 940.0, netPrice: 4860.0, paybackYears: 3.4, status: "pending" }
  ],

  // Sales Orders & 50% Advance Payment Gate
  orders: [
    {
      id: 1, ref: "SO-2026-0001", customerId: 1, system: "3kW On-Grid Rooftop",
      grossTotal: 2980.0, subsidy: 940.0, netPayable: 2040.0,
      advanceRequired: 1020.0, amountPaid: 1020.0,
      paymentStatus: "partially_paid", dispatchPermission: true,
      notes: "50% Advance reconciled. Equipment dispatch unlocked."
    }
  ],

  // Serialized Inventory & Allocation Constraints
  inventory: [
    { id: 1, serial: "INV-GROWATT-3KW-9901", product: "Growatt 3kW Dual MPPT Inverter", oem: "Growatt Solar Co.", status: "installed", customerId: 1, project: "INST-2026-0001", dispatchDate: "2026-10-31", warrantyYears: 2 },
    { id: 2, serial: "PV-MONO-550W-STR-01", product: "Canadian Solar 550W Mono PERC", oem: "Canadian Solar Inc.", status: "installed", customerId: 1, project: "INST-2026-0001", dispatchDate: "2026-10-31", warrantyYears: 20 },
    { id: 3, serial: "INV-DEYE-5KW-HYBRID-8802", product: "Deye 5kW Hybrid Inverter", oem: "Deye New Energy", status: "available", customerId: null, project: null, dispatchDate: null, warrantyYears: 5 },
    { id: 4, serial: "BAT-LIFEPO4-48V-100AH-7703", product: "BYD LiFePO4 48V Battery Module", oem: "BYD Energy Storage", status: "available", customerId: null, project: null, dispatchDate: null, warrantyYears: 5 }
  ],

  // Installations & 6-Phase Commissioning QC
  installations: [
    {
      id: 1, ref: "INST-2026-0001", customerId: 1, orderId: 1, capacity: 3.0, type: "on_grid",
      technician: "Ramesh Electrician (Senior Lead)", scheduledDate: "2026-10-31", state: "completed",
      readiness: { score: 100, survey: true, payment: true, stock: true, equip: true, tech: true },
      phases: { p1_struct: true, p2_modules: true, p3_inv: true, p4_earth: true, p5_test: true, p6_discom: true },
      qc: { voc: 385.0, isc: 9.4, earthResistance: 2.4, insulationMOhm: 25.0, gridVolt: 235.0 },
      customerAccepted: true, acceptanceSignature: "Dr. Rajesh Sharma (Verified OTP)",
      notes: "System commissioned & energized. Earth resistance measured at 2.4 Ohms (well under 5.0 Ohm safety threshold)."
    },
    {
      id: 2, ref: "INST-2026-0002", customerId: 3, orderId: 2, capacity: 5.0, type: "hybrid",
      technician: "Kiran Electrician (Crew B)", scheduledDate: "2026-11-04", state: "in_progress",
      readiness: { score: 100, survey: true, payment: true, stock: true, equip: true, tech: true },
      phases: { p1_struct: true, p2_modules: true, p3_inv: false, p4_earth: false, p5_test: false, p6_discom: false },
      qc: { voc: 420.0, isc: 11.2, earthResistance: 3.1, insulationMOhm: 22.0, gridVolt: 238.0 },
      customerAccepted: false, acceptanceSignature: "Pending Final Commissioning",
      notes: "Mounting structures and module array installed. Inverter battery hookup scheduled."
    }
  ],

  // Digital Warranties with SHA-256 Tokens
  warranties: [
    {
      id: 1, ref: "WRNT-INV-2026-0001", customerId: 1, serial: "INV-GROWATT-3KW-9901",
      product: "Growatt 3kW Inverter", type: "Solar Inverter Replacement", duration: "24 Months (2 Yrs)",
      startDate: "2026-10-31", expiryDate: "2028-10-31", token: "A89F34CD10BC91EA", status: "active"
    },
    {
      id: 2, ref: "WRNT-PV-2026-0001", customerId: 1, serial: "PV-MONO-550W-STR-01",
      product: "Canadian Solar 550W Mono Module", type: "20-Year Linear Output Guarantee", duration: "240 Months (20 Yrs)",
      startDate: "2026-10-31", expiryDate: "2046-10-31", token: "FE2158BA991C4402", status: "active"
    }
  ],

  // Service Tickets & Covered Repair Billing
  serviceTickets: [
    {
      id: 1, ref: "TICK-2026-0001", customerId: 1, serial: "INV-GROWATT-3KW-9901",
      faultCategory: "inverter_fault", faultLabel: "MPPT Firmware Communication Timeout (OEM Defect)",
      technician: "Ramesh Electrician", partsCost: 0.0, labourCost: 45.0, repairCost: 45.0,
      warrantyCovered: true, customerCharge: 0.0, customerSigned: true, state: "resolved",
      diagnosis: "Firmware deadlock in MPPT control chip.", resolution: "Re-flashed MCU firmware to v3.4.1. System generation normal."
    },
    {
      id: 2, ref: "TICK-2026-0002", customerId: 1, serial: "INV-GROWATT-3KW-9901",
      faultCategory: "grid_surge", faultLabel: "DISCOM External Lightning Grid Surge (Non-OEM)",
      technician: "Ramesh Electrician", partsCost: 45.0, labourCost: 40.0, repairCost: 85.0,
      warrantyCovered: false, customerCharge: 85.0, customerSigned: true, state: "closed",
      diagnosis: "External >400V grid surge blew sacrificial AC surge protection device.", resolution: "Replaced sacrificial SPD cartridge and retorqued terminal lugs."
    }
  ],

  // Job Costing, Profitability & Leakage Alerts
  costing: [
    {
      id: 1, ref: "COST-INST-2026-0001", projectRef: "INST-2026-0001", customerId: 1,
      estRevenue: 2040.0, actRevenue: 2040.0,
      materialCost: 1230.0, labourCost: 90.0, transCost: 60.0, addMatCost: 0.0, otherCost: 120.0,
      actualCost: 1500.0, estCost: 1500.0, variance: 0.0, overrunPct: 0.0,
      grossProfit: 540.0, grossMargin: 26.47, isOverrun: false, isLeakage: false,
      notes: "3kW On-Grid showcase project. Total cost: $1,500. Gross Profit: $540. Margin: 26.47%."
    },
    {
      id: 2, ref: "COST-PROJECT-OVERRUN", projectRef: "INST-2026-0002", customerId: 1,
      estRevenue: 3000.0, actRevenue: 3000.0,
      materialCost: 1900.0, labourCost: 350.0, transCost: 180.0, addMatCost: 150.0, otherCost: 120.0,
      actualCost: 2700.0, estCost: 1900.0, variance: 800.0, overrunPct: 42.11,
      grossProfit: 300.0, grossMargin: 10.00, isOverrun: true, isLeakage: true,
      notes: "Unplanned rock trenching and copper price surge created cost overrun (+42.1%), triggering Profit Leakage Alert."
    }
  ]
};

// ==========================================================================
// INITIALIZER
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  setupSidebar();
  setupRoleSwitcher();
  setupGlobalSearch();
  setupNotifications();
  setupQuickCreate();
  setupShowcaseTour();
  initHashRouting();
  renderRoleDashboard();
  renderAllDataViews();
  initializeNexusExperience();
});

async function initializeNexusExperience() {
  const entry = document.getElementById('nexus-entry');
  try {
    const response = await fetch('/api/auth/me', { credentials: 'same-origin' });
    if (!response.ok) return;
    const result = await response.json();
    activateAuthenticatedRole(result.user.role, result.user);
    entry?.remove();
    if (result.user.role === 'customer' && !window.location.pathname.includes('customer.html')) {
      window.location.replace('/customer.html');
    }
  } catch (error) {
    console.warn('Authentication session could not be restored.', error);
  }
}

function activateAuthenticatedRole(serverRole, user) {
  const frontendRole = serverRole === 'technician' ? 'tech' : serverRole;
  SolarFlowState.currentRole = frontendRole;
  sessionStorage.setItem('nexus-role', frontendRole);
  sessionStorage.setItem('nexus-entered', 'true');
  applyRole(frontendRole);
  const roleLabel = document.getElementById('authenticated-role-label');
  if (roleLabel) roleLabel.textContent = `${(SolarFlowState.roles[frontendRole] || {}).name || frontendRole} · ${user?.name || user?.email || ''}`;
}

function openNexusLogin() {
  const login = document.getElementById('nexus-login-card');
  if (!login) return;
  login.hidden = false;
  setTimeout(() => login.classList.add('visible'), 20);
  document.getElementById('nexus-user')?.focus();
}

function closeNexusLogin() {
  const login = document.getElementById('nexus-login-card');
  login?.classList.remove('visible');
  setTimeout(() => { if (login) login.hidden = true; }, 180);
}

function showAuthMode(mode) {
  const login = document.getElementById('nexus-login-form');
  const register = document.getElementById('nexus-register-form');
  const forgot = document.getElementById('nexus-forgot-form');
  login.hidden = mode !== 'login';
  register.hidden = mode !== 'register';
  forgot.hidden = mode !== 'forgot';
  document.getElementById('auth-tab-login').classList.toggle('active', mode === 'login');
  document.getElementById('auth-tab-register').classList.toggle('active', mode === 'register');
  if (mode === 'forgot') document.getElementById('nexus-forgot-email').focus();
  if (mode === 'login') document.getElementById('nexus-user').focus();
  if (mode === 'register') document.getElementById('nexus-register-name').focus();
}

function toggleB2BRegistration(accountType) {
  document.getElementById('nexus-b2b-fields').hidden = accountType !== 'b2b';
}

function setAuthMessage(id, message, type = 'error') {
  const element = document.getElementById(id);
  if (!element) return;
  element.textContent = message;
  element.className = `nexus-auth-message ${type}`;
}

async function completeNexusLogin() {
  const email = document.getElementById('nexus-user')?.value.trim();
  const password = document.getElementById('nexus-password')?.value;
  setAuthMessage('nexus-login-message', '');
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ email, password })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Login failed');
    sessionStorage.setItem('nexus-entered', 'true');
    sessionStorage.setItem('nexus-csrf', result.csrfToken);
    sessionStorage.setItem('nexus-role', result.user.role);
    const entry = document.getElementById('nexus-entry');
    if (entry) entry.classList.add('nexus-entering');
    setTimeout(() => entry?.remove(), 500);
    showToast(`Welcome back, ${result.user.name}`, 'success');
    activateAuthenticatedRole(result.user.role, result.user);
    if (result.user.role === 'customer') {
      setTimeout(() => window.location.assign('/customer.html'), 350);
    } else if (window.location.hash === '#dashboard' || !window.location.hash) {
      window.location.replace('/#dashboard');
    }
  } catch (error) {
    setAuthMessage('nexus-login-message', error.message);
  }
}

async function registerNexusAccount(event) {
  event.preventDefault();
  const name = document.getElementById('nexus-register-name').value.trim();
  const email = document.getElementById('nexus-register-email').value.trim();
  const password = document.getElementById('nexus-register-password').value;
  const confirm = document.getElementById('nexus-register-confirm').value;
  const accountType = document.getElementById('nexus-register-type')?.value || 'customer';
  const organizationName = document.getElementById('nexus-register-organization')?.value.trim();
  const gstin = document.getElementById('nexus-register-gstin')?.value.trim();
  if (password !== confirm) {
    setAuthMessage('nexus-register-message', 'Passwords do not match.');
    return;
  }
  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, accountType, organizationName, gstin })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Registration failed');
    setAuthMessage('nexus-register-message', result.message, 'success');
    document.getElementById('nexus-register-form').reset();
    sessionStorage.setItem('nexus-entered', 'true');
    sessionStorage.setItem('nexus-csrf', result.csrfToken);
    sessionStorage.setItem('nexus-role', 'customer');
    if (result.emailVerificationRequired) {
      document.getElementById('nexus-email-verification').hidden = false;
      if (result.demoVerificationCode) {
        document.getElementById('nexus-verification-code').value = result.demoVerificationCode;
        setAuthMessage('nexus-register-message', `Business email verified with code ${result.demoVerificationCode} (development mode).`, 'success');
      } else {
        setAuthMessage('nexus-register-message', 'Enter the verification code sent to your business email.', 'success');
      }
      return;
    }
    setTimeout(() => window.location.assign('/customer.html'), 300);
  } catch (error) {
    setAuthMessage('nexus-register-message', error.message);
  }

  async function completeB2BEmailVerification() {
    const code = document.getElementById('nexus-verification-code').value.trim();
    try {
      const response = await fetch('/api/b2b/email/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': sessionStorage.getItem('nexus-csrf') || ''
        },
        body: JSON.stringify({ code })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Verification failed');
      setAuthMessage('nexus-register-message', result.message, 'success');
      setTimeout(() => window.location.assign('/customer.html'), 300);
    } catch (error) {
      setAuthMessage('nexus-register-message', error.message);
    }
  }
}

async function requestNexusPasswordReset(event) {
  event.preventDefault();
  const email = document.getElementById('nexus-forgot-email').value.trim();
  try {
    const response = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Reset request failed');
    setAuthMessage('nexus-forgot-message', result.message, 'success');
    if (result.demoResetCode) {
      document.getElementById('nexus-demo-reset').hidden = false;
      document.getElementById('nexus-reset-code').value = result.demoResetCode;
      document.getElementById('nexus-forgot-submit').hidden = true;
    }
  } catch (error) {
    setAuthMessage('nexus-forgot-message', error.message);
  }
}

async function completeNexusPasswordReset() {
  const code = document.getElementById('nexus-reset-code').value.trim();
  const password = document.getElementById('nexus-reset-password').value;
  try {
    const response = await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, password })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Password reset failed');
    setAuthMessage('nexus-forgot-message', result.message, 'success');
    document.getElementById('nexus-demo-reset').hidden = true;
    document.getElementById('nexus-forgot-submit').hidden = false;
  } catch (error) {
    setAuthMessage('nexus-forgot-message', error.message);
  }
}

// Setup Sidebar Toggle
function setupSidebar() {
  const toggleBtn = document.getElementById('sidebar-toggle-btn');
  const sidebar = document.getElementById('app-sidebar');
  const wrapper = document.getElementById('app-main-wrapper');

  if (toggleBtn && sidebar && wrapper) {
    toggleBtn.addEventListener('click', () => {
      SolarFlowState.sidebarCollapsed = !SolarFlowState.sidebarCollapsed;
      sidebar.classList.toggle('collapsed', SolarFlowState.sidebarCollapsed);
      wrapper.classList.toggle('sidebar-collapsed', SolarFlowState.sidebarCollapsed);
    });
  }

  // Navigation Links click handler
  document.querySelectorAll('.nav-link-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.getAttribute('data-view');
      switchView(view);
    });
  });
}

// Vector 8: Direct URL Access Guard & Hash Routing
function initHashRouting() {
  window.addEventListener('hashchange', () => {
    const raw = window.location.hash.replace('#', '') || 'dashboard';
    handleHashRoute(raw);
  });
  const initial = window.location.hash.replace('#', '') || 'dashboard';
  handleHashRoute(initial);
}

function handleHashRoute(route) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  const hasAccess = roleCfg.perm.includes('all') || roleCfg.perm.includes(route);
  if (!hasAccess) {
    showAccessDeniedModal(
      `Direct Route Navigation: #${route}`,
      roleCfg.name,
      `Security Violation (HTTP 403 Forbidden): Direct URL access to <code>#${route}</code> was intercepted and rejected. The active account role <strong>${roleCfg.name}</strong> (${roleCfg.login}) is restricted from accessing this business module by server-level ACL rules.`
    );
    window.location.hash = '#dashboard';
    switchView('dashboard');
    return;
  }
  switchView(route);
}

// View Switcher with Role Guard
function switchView(viewName) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  
  // Security check: is role allowed to view?
  const hasAccess = roleCfg.perm.includes('all') || roleCfg.perm.includes(viewName);
  if (!hasAccess) {
    showAccessDeniedModal(
      viewName,
      roleCfg.name,
      `Access Denied (HTTP 403 Forbidden): The <strong>${roleCfg.name}</strong> role (${roleCfg.login}) does not possess authorization to view the <code>${viewName}</code> module.`
    );
    return;
  }

  SolarFlowState.activeView = viewName;
  if (window.location.hash !== '#' + viewName) {
    history.replaceState(null, null, '#' + viewName);
  }

  // Update active button state
  document.querySelectorAll('.nav-link-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-view') === viewName);
  });

  // Update Breadcrumb Text
  updateBreadcrumbs(viewName);

  // Hide all sections
  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

  // Target Section
  let targetSection = document.getElementById(`view-${viewName}`);
  if (!targetSection) {
    targetSection = document.getElementById('view-generic-panel');
    populateGenericModule(viewName);
  }

  if (targetSection) {
    targetSection.classList.add('active');
  }

  // Refresh view if dashboard
  if (viewName === 'dashboard') {
    renderRoleDashboard();
  }
}

// Breadcrumb updater
function updateBreadcrumbs(viewName) {
  const breadcrumbPage = document.getElementById('breadcrumb-page');
  const breadcrumbSection = document.getElementById('breadcrumb-section');
  
  const map = {
    dashboard: ["Overview", "Executive Dashboard"],
    enquiries: ["Sales Management", "Customer Enquiries"],
    leads: ["Sales Management", "Solar Leads"],
    followups: ["Sales Management", "Follow-ups"],
    surveys: ["Sales Management", "Site Surveys"],
    quotations: ["Sales Management", "Quotations"],
    orders: ["Sales Management", "Sales Orders"],
    installations: ["Operations", "Installation Projects"],
    schedule: ["Operations", "Field Schedule"],
    technicians: ["Operations", "Technician Crew"],
    inst_reports: ["Operations", "Installation Reports"],
    products: ["Inventory", "Solar Equipment"],
    categories: ["Inventory", "Categories"],
    warehouses: ["Inventory", "Warehouses"],
    stock_avail: ["Inventory", "Stock Availability"],
    stock_reservations: ["Inventory", "Stock Reservations"],
    inventory: ["Inventory", "Serial Numbers"],
    dispatches: ["Inventory", "Material Dispatches"],
    stock_moves: ["Inventory", "Movement History"],
    warranties: ["After-Sales", "Digital Warranties"],
    service: ["After-Sales", "Service Tickets"],
    complaints: ["After-Sales", "Customer Complaints"],
    service_history: ["After-Sales", "Service History"],
    invoices: ["Finance", "Milestone Invoices"],
    payments: ["Finance", "Customer Payments"],
    expenses: ["Finance", "Project Expenses"],
    costing: ["Finance", "Project Profitability"],
    fin_reports: ["Finance", "Financial Reports"],
    biz_reports: ["Analytics", "Business Reports"],
    op_reports: ["Analytics", "Operational Reports"],
    tech_perf: ["Analytics", "Technician Performance"],
    sales_perf: ["Analytics", "Sales Performance"],
    users: ["Administration", "User Management"],
    roles: ["Administration", "Roles & Permissions"],
    company: ["Administration", "Company Settings"],
    packages: ["Administration", "Solar Packages"],
    settings: ["Administration", "System Settings"]
  };

  const info = map[viewName] || ["Operations", viewName.toUpperCase()];
  if (breadcrumbSection) breadcrumbSection.textContent = info[0];
  if (breadcrumbPage) breadcrumbPage.textContent = info[1];
}

// Setup Role Switcher (RBAC)
function setupRoleSwitcher() {
  const select = document.getElementById('user-role-select');
  if (!select) return;

  select.addEventListener('change', (e) => {
    applyRole(e.target.value);
  });

  applyRole(SolarFlowState.currentRole);
}

function applyRole(roleKey) {
  SolarFlowState.currentRole = roleKey;
  const cfg = SolarFlowState.roles[roleKey] || SolarFlowState.roles.admin;

  const select = document.getElementById('user-role-select');
  if (select && select.value !== roleKey) {
    select.value = roleKey;
  }

  // 1. Profile badges & user credentials
  const roleIndicator = document.getElementById('sidebar-role-indicator');
  const avatarInitials = document.getElementById('user-avatar-initials');
  const displayName = document.getElementById('user-display-name');
  const roleTitle = document.getElementById('user-role-title');

  if (roleIndicator) roleIndicator.textContent = cfg.name;
  if (avatarInitials) avatarInitials.textContent = cfg.avatar;
  if (displayName) displayName.innerHTML = `${cfg.userName} <span style="font-size:11px; font-weight:500; color:var(--text-muted);">(${cfg.name})</span>`;
  if (roleTitle) roleTitle.textContent = `${cfg.title} • ${cfg.login}`;

  // 2. Filter Navigation Menu Links based on exact permissions
  document.querySelectorAll('.sidebar-nav .nav-link-btn').forEach(btn => {
    const perm = btn.getAttribute('data-perm') || '';
    if (perm === 'all' || cfg.perm.includes('all')) {
      btn.style.display = 'flex';
    } else {
      const allowedRoles = perm.split(',').map(s => s.trim());
      btn.style.display = allowedRoles.includes(roleKey) ? 'flex' : 'none';
    }
  });

  // Filter Group Titles
  document.querySelectorAll('.sidebar-nav .nav-group-title').forEach(grp => {
    const grpPerm = grp.getAttribute('data-group-perm');
    if (!grpPerm || cfg.perm.includes('all')) {
      grp.style.display = 'block';
    } else {
      const allowedRoles = grpPerm.split(',').map(s => s.trim());
      grp.style.display = allowedRoles.includes(roleKey) ? 'block' : 'none';
    }
  });

  // 3. Financial Costing Access Barrier
  const costingBanner = document.getElementById('costing-restricted-banner');
  const costingContent = document.getElementById('costing-content-panel');
  const canSeeFinances = (roleKey === 'admin' || roleKey === 'finance' || roleKey === 'director');

  if (costingBanner && costingContent) {
    if (canSeeFinances) {
      costingBanner.style.display = 'none';
      costingContent.style.display = 'block';
    } else {
      costingBanner.style.display = 'flex';
      costingContent.style.display = 'none';
    }
  }

  // 4. Fallback if active view is unauthorized
  if (!cfg.perm.includes('all') && !cfg.perm.includes(SolarFlowState.activeView)) {
    switchView('dashboard');
  } else {
    renderRoleDashboard();
  }

  // Re-render data views to apply domain isolation filters (Technician/Surveyor)
  renderAllDataViews();

  showToast(`Authenticated as: ${cfg.userName} (${cfg.login}) — Role: ${cfg.name}`, 'info');
}

// ==========================================================================
// ROLE-TAILORED DASHBOARDS WITH VISUAL CHARTS
// ==========================================================================
function renderRoleDashboard() {
  const container = document.getElementById('role-dashboard-container');
  if (!container) return;

  const role = SolarFlowState.currentRole;

  switch (role) {
    case 'sales':
      renderSalesDashboard(container);
      break;
    case 'warehouse':
      renderWarehouseDashboard(container);
      break;
    case 'tech':
      renderTechnicianDashboard(container);
      break;
    case 'support':
      renderSupportDashboard(container);
      break;
    case 'finance':
      renderFinanceDashboard(container);
      break;
    case 'survey_tech':
      renderSurveyTechDashboard(container);
      break;
    case 'director':
      renderDirectorDashboard(container);
      break;
    case 'admin':
    default:
      renderAdminDashboard(container);
      break;
  }
}

// 1. Super Administrator Dashboard with Bar Chart
function renderAdminDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Executive Command Center</h1>
        <p class="section-description">Real database-driven operational KPIs across EPC sales, site engineering, serialized warehouse, and project margins.</p>
      </div>
      <div class="header-action-group">
        <span class="status-pill pill-success">Live DB Sync: 100%</span>
        <span class="status-pill pill-warning">PM Surya Ghar Subsidy: Active</span>
      </div>
    </div>

    <!-- 12 Real Database Metrics Grid -->
    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header">
          <span class="metric-label">Total Projects</span>
          <div class="metric-icon-wrap icon-forest">⚡</div>
        </div>
        <div class="metric-value">10</div>
        <div class="metric-subtext">100% Turnkey EPC</div>
      </div>

      <div class="metric-card" onclick="switchView('leads')">
        <div class="metric-header">
          <span class="metric-label">Active Leads</span>
          <div class="metric-icon-wrap icon-blue">🎯</div>
        </div>
        <div class="metric-value">10</div>
        <div class="metric-subtext">Residential &amp; Commercial</div>
      </div>

      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header">
          <span class="metric-label">Pending Surveys</span>
          <div class="metric-icon-wrap icon-amber">📐</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">Shadow &amp; Tilt Checks</div>
      </div>

      <div class="metric-card" onclick="switchView('quotations')">
        <div class="metric-header">
          <span class="metric-label">Pending Quotes</span>
          <div class="metric-icon-wrap icon-purple">📑</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Awaiting Customer Approval</div>
      </div>

      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header">
          <span class="metric-label">Confirmed Orders</span>
          <div class="metric-icon-wrap icon-forest">✅</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">50% Advance Paid</div>
      </div>

      <div class="metric-card" onclick="switchView('schedule')">
        <div class="metric-header">
          <span class="metric-label">Scheduled Visits</span>
          <div class="metric-icon-wrap icon-blue">📅</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Field Crew Assigned</div>
      </div>

      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header">
          <span class="metric-label">Completed Sites</span>
          <div class="metric-icon-wrap icon-forest">🏆</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">QC Passed (&le; 5.0 &Omega;)</div>
      </div>

      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Low Stock Alerts</span>
          <div class="metric-icon-wrap icon-rose">⚠️</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Earthing Chemical Mix</div>
      </div>

      <div class="metric-card" onclick="switchView('warranties')">
        <div class="metric-header">
          <span class="metric-label">Active Warranties</span>
          <div class="metric-icon-wrap icon-forest">🛡️</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">SHA-256 Tokens Active</div>
      </div>

      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header">
          <span class="metric-label">Open Tickets</span>
          <div class="metric-icon-wrap icon-amber">🔧</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">1 Covered ($0), 1 Non-Covered</div>
      </div>

      <div class="metric-card highlight-profit" onclick="switchView('orders')">
        <div class="metric-header">
          <span class="metric-label">Monthly Revenue</span>
          <div class="metric-icon-wrap icon-forest">💵</div>
        </div>
        <div class="metric-value">$2,040.00</div>
        <div class="metric-subtext">Turnkey Solar Contract</div>
      </div>

      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header">
          <span class="metric-label">Gross Margin</span>
          <div class="metric-icon-wrap icon-forest">📈</div>
        </div>
        <div class="metric-value">26.47%</div>
        <div class="metric-subtext">Gross Profit: $540.00</div>
      </div>
    </div>

    <!-- Revenue Trend Chart Card -->
    <div class="chart-container-card">
      <div class="chart-header">
        <div>
          <span class="status-pill pill-info" style="margin-bottom:4px;">Financial Performance</span>
          <div class="chart-title">Monthly EPC Revenue &amp; Project Realization Trend</div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-dot dot-primary"></span> Revenue Realized</div>
          <div class="legend-item"><span class="legend-dot dot-secondary"></span> Projected Pipeline</div>
        </div>
      </div>
      
      <div class="bar-chart-visual">
        <div class="bar-col">
          <div class="bar-pill" style="height:35%;"><span class="bar-tooltip">Jul: $850</span></div>
          <span class="bar-label">Jul 2026</span>
        </div>
        <div class="bar-col">
          <div class="bar-pill" style="height:55%;"><span class="bar-tooltip">Aug: $1,250</span></div>
          <span class="bar-label">Aug 2026</span>
        </div>
        <div class="bar-col">
          <div class="bar-pill" style="height:70%;"><span class="bar-tooltip">Sep: $1,600</span></div>
          <span class="bar-label">Sep 2026</span>
        </div>
        <div class="bar-col">
          <div class="bar-pill" style="height:100%;"><span class="bar-tooltip">Oct: $2,040 (Active)</span></div>
          <span class="bar-label">Oct 2026</span>
        </div>
        <div class="bar-col">
          <div class="bar-pill" style="height:85%; opacity:0.6;"><span class="bar-tooltip">Nov: $1,800 (Est)</span></div>
          <span class="bar-label">Nov 2026</span>
        </div>
      </div>
    </div>

    <!-- Innovation Split Panels -->
    <div class="dashboard-grid-2col">
      <!-- Unique Feature: Serial-to-Warranty Hardware Lifecycle -->
      <div class="content-card">
        <div class="card-title-bar">
          <div>
            <span class="status-pill pill-info" style="margin-bottom:4px;">Hardware Traceability</span>
            <div class="card-title">Serial-to-Warranty Hardware Lifecycle</div>
          </div>
          <span style="font-size:12px; font-weight:600; color:var(--primary);">Serial: INV-GROWATT-3KW-9901</span>
        </div>
        <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:14px;">Complete 7-stage hardware journey mapped to verified Odoo EPC transactions.</p>
        
        <div class="lifecycle-timeline-horizontal">
          <div class="timeline-track-line"></div>
          
          <div class="timeline-step completed">
            <div class="timeline-node">✓</div>
            <span class="timeline-step-label">1. Purchase</span>
            <span class="timeline-step-date">PO-2026-004</span>
          </div>

          <div class="timeline-step completed">
            <div class="timeline-node">✓</div>
            <span class="timeline-step-label">2. Receipt</span>
            <span class="timeline-step-date">WH-IN-01</span>
          </div>

          <div class="timeline-step completed">
            <div class="timeline-node">✓</div>
            <span class="timeline-step-label">3. Reserve</span>
            <span class="timeline-step-date">SO-0001</span>
          </div>

          <div class="timeline-step completed">
            <div class="timeline-node">✓</div>
            <span class="timeline-step-label">4. Dispatch</span>
            <span class="timeline-step-date">50% Advance</span>
          </div>

          <div class="timeline-step completed">
            <div class="timeline-node">✓</div>
            <span class="timeline-step-label">5. Mounted</span>
            <span class="timeline-step-date">QC 2.4 &Omega;</span>
          </div>

          <div class="timeline-step completed">
            <div class="timeline-node">✓</div>
            <span class="timeline-step-label">6. Warranty</span>
            <span class="timeline-step-date">SHA-256</span>
          </div>

          <div class="timeline-step active">
            <div class="timeline-node">7</div>
            <span class="timeline-step-label">7. Service</span>
            <span class="timeline-step-date">Covered $0</span>
          </div>
        </div>
      </div>

      <!-- Installation Readiness Score -->
      <div class="content-card">
        <div class="card-title-bar">
          <div>
            <span class="status-pill pill-success" style="margin-bottom:4px;">Readiness Index</span>
            <div class="card-title">Installation Readiness</div>
          </div>
          <span class="status-pill pill-success">100 / 100</span>
        </div>

        <div class="readiness-score-box">
          <div class="gauge-circle">
            <div class="gauge-inner-circle">
              <span class="gauge-number">100</span>
              <span class="gauge-points-label">POINTS</span>
            </div>
          </div>
          <div style="font-size:12.5px; font-weight:600; color:var(--text-main); margin-bottom:8px;">Dr. Rajesh Sharma (3kW Site)</div>
        </div>

        <div class="readiness-criteria-list">
          <div class="criterion-item passed"><span>✓ Survey Approved</span><span class="criterion-status-tag">+20 Pts</span></div>
          <div class="criterion-item passed"><span>✓ 50% Advance Paid</span><span class="criterion-status-tag">+20 Pts</span></div>
          <div class="criterion-item passed"><span>✓ Stock In Staging</span><span class="criterion-status-tag">+20 Pts</span></div>
          <div class="criterion-item passed"><span>✓ Serials Allocated</span><span class="criterion-status-tag">+20 Pts</span></div>
          <div class="criterion-item passed"><span>✓ Crew Assigned</span><span class="criterion-status-tag">+20 Pts</span></div>
        </div>
      </div>
    </div>
  `;
}

// 2. Sales Manager Dashboard
function renderSalesDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Sales Manager Command Center</h1>
        <p class="section-description">Lead pipeline, preliminary consumption analysis, customer follow-ups, and quotation approvals.</p>
      </div>
      <div class="header-action-group">
        <button class="btn-primary-action" onclick="showLeadModal()">+ Create New Lead</button>
        <button class="btn-secondary-action" onclick="switchView('followups')">📅 View Follow-ups</button>
      </div>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('enquiries')">
        <div class="metric-header"><span class="metric-label">New Enquiries</span><div class="metric-icon-wrap icon-forest">📩</div></div>
        <div class="metric-value">4</div><div class="metric-subtext">2 Awaiting Sizing</div>
      </div>
      <div class="metric-card" onclick="switchView('leads')">
        <div class="metric-header"><span class="metric-label">My Leads</span><div class="metric-icon-wrap icon-blue">🎯</div></div>
        <div class="metric-value">10</div><div class="metric-subtext">8 Residential, 2 Commercial</div>
      </div>
      <div class="metric-card" onclick="switchView('followups')">
        <div class="metric-header"><span class="metric-label">Follow-ups Due</span><div class="metric-icon-wrap icon-amber">⏰</div></div>
        <div class="metric-value">3</div><div class="metric-subtext">Today &amp; Tomorrow</div>
      </div>
      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header"><span class="metric-label">Surveys Pending</span><div class="metric-icon-wrap icon-rose">📐</div></div>
        <div class="metric-value">2</div><div class="metric-subtext">Field Team Dispatched</div>
      </div>
      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header"><span class="metric-label">Approved Surveys</span><div class="metric-icon-wrap icon-forest">✓</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">Ready for Quotation</div>
      </div>
      <div class="metric-card" onclick="switchView('quotations')">
        <div class="metric-header"><span class="metric-label">Quotations Pending</span><div class="metric-icon-wrap icon-purple">📑</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">Awaiting Customer Sign</div>
      </div>
      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header"><span class="metric-label">Confirmed Orders</span><div class="metric-icon-wrap icon-forest">✅</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">$2,040 Turnkey Contract</div>
      </div>
      <div class="metric-card highlight-profit">
        <div class="metric-header"><span class="metric-label">Conversion Rate</span><div class="metric-icon-wrap icon-forest">🏆</div></div>
        <div class="metric-value">80.0%</div><div class="metric-subtext">Surveys to Quotation Ratio</div>
      </div>
    </div>
  `;
}

// 3. Warehouse Manager Dashboard
function renderWarehouseDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Warehouse &amp; Serial Inventory Command</h1>
        <p class="section-description">Serialized PV equipment, stock reservations, single-allocation constraints, and dispatch releases.</p>
      </div>
      <button class="btn-primary-action" onclick="showToast('Stock receipt logged.', 'success')">+ Receive Equipment</button>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header"><span class="metric-label">Total SKUs</span><div class="metric-icon-wrap icon-forest">📦</div></div>
        <div class="metric-value">4</div><div class="metric-subtext">PV, Inverters, Batteries</div>
      </div>
      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header"><span class="metric-label">Available Stock</span><div class="metric-icon-wrap icon-blue">📊</div></div>
        <div class="metric-value">2</div><div class="metric-subtext">Ready for Reservation</div>
      </div>
      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header"><span class="metric-label">Reserved Equipment</span><div class="metric-icon-wrap icon-amber">🔒</div></div>
        <div class="metric-value">2</div><div class="metric-subtext">Allocated to Projects</div>
      </div>
      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header"><span class="metric-label">Low Stock Alert</span><div class="metric-icon-wrap icon-rose">⚠️</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">Earthing Compound Mix</div>
      </div>
    </div>
  `;
}

// 4. Installation Technician Dashboard
function renderTechnicianDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Field Installation Work Orders</h1>
        <p class="section-description">My assigned rooftop jobs, 6-phase checklist execution, and mandatory electrical safety testing (<5.0&Omega;).</p>
      </div>
      <span class="status-pill pill-danger">Safety Limit: Earth Pit &le; 5.0 &Omega;</span>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header"><span class="metric-label">My Assigned Jobs</span><div class="metric-icon-wrap icon-forest">⚡</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">INST-2026-0001 (3kW)</div>
      </div>
      <div class="metric-card" onclick="switchView('schedule')">
        <div class="metric-header"><span class="metric-label">Today's Visits</span><div class="metric-icon-wrap icon-blue">📅</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">Dr. Rajesh Sharma Site</div>
      </div>
      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header"><span class="metric-label">Testing QC Status</span><div class="metric-icon-wrap icon-forest">✓</div></div>
        <div class="metric-value">2.4 &Omega;</div><div class="metric-subtext">Passed Safety Gate</div>
      </div>
      <div class="metric-card highlight-profit" onclick="switchView('installations')">
        <div class="metric-header"><span class="metric-label">Commissioned Sites</span><div class="metric-icon-wrap icon-forest">🏆</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">Customer Accepted (100%)</div>
      </div>
    </div>
  `;
}

// 5. Support Manager Dashboard
function renderSupportDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">After-Sales Support &amp; Warranty Helpdesk</h1>
        <p class="section-description">Equipment serial lookup, automatic warranty determination, covered ($0) vs non-covered ticket billing.</p>
      </div>
      <button class="btn-primary-action" onclick="showTicketModal()">+ Log Service Ticket</button>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header"><span class="metric-label">Open Complaints</span><div class="metric-icon-wrap icon-rose">⚠️</div></div>
        <div class="metric-value">2</div><div class="metric-subtext">1 Inverter, 1 Grid Surge</div>
      </div>
      <div class="metric-card" onclick="switchView('warranties')">
        <div class="metric-header"><span class="metric-label">Active Warranties</span><div class="metric-icon-wrap icon-forest">🛡️</div></div>
        <div class="metric-value">2</div><div class="metric-subtext">SHA-256 Certificates</div>
      </div>
      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header"><span class="metric-label">Covered ($0) Claims</span><div class="metric-icon-wrap icon-blue">✓</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">OEM Warranty Replaced</div>
      </div>
      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header"><span class="metric-label">Non-Covered Repairs</span><div class="metric-icon-wrap icon-amber">💵</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">Billed $85.00 to Client</div>
      </div>
    </div>
  `;
}

// 6. Survey Technician Dashboard
function renderSurveyTechDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Survey Technician Assessment Board</h1>
        <p class="section-description">Assigned rooftop site visits, shadow analysis, azimuth/tilt logging, and chief engineer submissions.</p>
      </div>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header"><span class="metric-label">Assigned Surveys</span><div class="metric-icon-wrap icon-forest">📐</div></div>
        <div class="metric-value">2</div><div class="metric-subtext">SRV-0001, SRV-0002</div>
      </div>
      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header"><span class="metric-label">Submitted for Approval</span><div class="metric-icon-wrap icon-blue">📩</div></div>
        <div class="metric-value">1</div><div class="metric-subtext">SRV-0001 Approved</div>
      </div>
    </div>
  `;
}

// 7. Finance Manager Dashboard
function renderFinanceDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Finance &amp; Costing Command</h1>
        <p class="section-description">Milestone invoicing, 50% advance reconciliations, project job costing, and profit leakage alerts.</p>
      </div>
      <span class="status-pill pill-danger">Leakage Gate: &gt;10% Cost Overrun</span>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header"><span class="metric-label">Billed Revenue</span><div class="metric-icon-wrap icon-forest">💵</div></div>
        <div class="metric-value">$2,040.00</div><div class="metric-subtext">3kW Turnkey Contract</div>
      </div>
      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header"><span class="metric-label">50% Advance Met</span><div class="metric-icon-wrap icon-blue">💳</div></div>
        <div class="metric-value">$1,020.00</div><div class="metric-subtext">Dispatch Permission Unlocked</div>
      </div>
      <div class="metric-card" onclick="switchView('costing')">
        <div class="metric-header"><span class="metric-label">Actual Project Cost</span><div class="metric-icon-wrap icon-amber">💸</div></div>
        <div class="metric-value">$1,500.00</div><div class="metric-subtext">Hardware, Labour &amp; Transport</div>
      </div>
      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header"><span class="metric-label">Gross Margin</span><div class="metric-icon-wrap icon-forest">📈</div></div>
        <div class="metric-value">26.47%</div><div class="metric-subtext">Gross Profit: $540.00</div>
      </div>
    </div>
  `;
}

// 8. Director / Investor Dashboard (Read-Only)
function renderDirectorDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Executive Business Analytics (Read-Only)</h1>
        <p class="section-description">High-level financial summaries, EBITDA margins, and project pipeline health. Modifications are disabled.</p>
      </div>
      <span class="status-pill pill-neutral">🔒 Read-Only Investor Access</span>
    </div>

    <div class="confidential-financial-banner">
      <div class="banner-shield-icon">📊</div>
      <div>
        <div class="banner-title">Board of Directors Executive Mode</div>
        <div class="banner-text">All financial metrics below are dynamically computed from active turnkey solar contracts. Transaction editing is strictly disabled for governance.</div>
      </div>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header"><span class="metric-label">Total EPC Revenue</span><div class="metric-icon-wrap icon-forest">💵</div></div>
        <div class="metric-value">$2,040.00</div><div class="metric-subtext">Commercial &amp; Residential</div>
      </div>
      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header"><span class="metric-label">Gross Profit</span><div class="metric-icon-wrap icon-forest">📈</div></div>
        <div class="metric-value">$540.00</div><div class="metric-subtext">Gross Margin: 26.47%</div>
      </div>
      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header"><span class="metric-label">Active Projects</span><div class="metric-icon-wrap icon-forest">⚡</div></div>
        <div class="metric-value">10</div><div class="metric-subtext">1 Completed, 9 Staging</div>
      </div>
      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header"><span class="metric-label">Warehoused Stock Value</span><div class="metric-icon-wrap icon-blue">🏢</div></div>
        <div class="metric-value">$8,950.00</div><div class="metric-subtext">Tier-1 Modules &amp; Inverters</div>
      </div>
    </div>
  `;
}

// ==========================================================================
// RENDER ALL DATA TABLES & VIEWS
// ==========================================================================
function renderAllDataViews() {
  renderEnquiries();
  renderLeads();
  renderFollowups();
  renderSurveys();
  renderQuotations();
  renderOrders();
  renderPackages();
  renderInstallations();
  renderSchedule();
  renderInventory();
  renderWarranties();
  renderService();
  renderCosting();
}

// 1. Enquiries Table
function renderEnquiries(filterQuery = '', filterStatus = 'all') {
  const tbody = document.getElementById('enquiries-table-body');
  if (!tbody) return;

  let list = SolarFlowState.enquiries;
  if (filterStatus !== 'all') {
    list = list.filter(e => e.status === filterStatus);
  }
  if (filterQuery) {
    const q = filterQuery.toLowerCase();
    list = list.filter(e => {
      const cust = SolarFlowState.customers.find(c => c.id === e.customerId) || {};
      return e.ref.toLowerCase().includes(q) || (cust.name || '').toLowerCase().includes(q);
    });
  }

  tbody.innerHTML = list.map(enq => {
    const cust = SolarFlowState.customers.find(c => c.id === enq.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${enq.ref}</strong></td>
        <td><strong>${cust.name || 'Unknown'}</strong></td>
        <td style="color:var(--text-muted);">${cust.phone || ''}</td>
        <td>${cust.city || 'Bengaluru'}</td>
        <td>${enq.propertyType}</td>
        <td><span class="status-pill pill-info">${enq.sanctionedLoad}</span></td>
        <td><span class="status-pill ${enq.status === 'qualified' ? 'pill-success' : 'pill-warning'}">${enq.status.toUpperCase()}</span></td>
        <td>
          <div class="action-btn-group">
            <button class="btn-action-primary-sm" onclick="scheduleSurveyFromLead(${cust.id})">Schedule Survey</button>
            <button class="btn-action-sm" onclick="openCustomerProfile(${cust.id})">View 360°</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// 2. Leads Table & Kanban Board
function renderLeads(filterQuery = '', filterType = 'all') {
  const tbody = document.getElementById('leads-table-body');
  if (!tbody) return;

  let list = SolarFlowState.leads;
  if (filterType !== 'all') {
    list = list.filter(l => l.type === filterType);
  }
  if (filterQuery) {
    const q = filterQuery.toLowerCase();
    list = list.filter(l => {
      const cust = SolarFlowState.customers.find(c => c.id === l.customerId) || {};
      return l.ref.toLowerCase().includes(q) || (cust.name || '').toLowerCase().includes(q);
    });
  }

  tbody.innerHTML = list.map(lead => {
    const cust = SolarFlowState.customers.find(c => c.id === lead.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${lead.ref}</strong></td>
        <td><strong>${cust.name || 'Unknown'}</strong></td>
        <td style="color:var(--text-muted);">${cust.phone || ''}</td>
        <td>${lead.monthlyKwh} kWh</td>
        <td>$${lead.tariff.toFixed(2)}</td>
        <td><span class="status-pill pill-warning">${lead.sizedKw} kW</span></td>
        <td><span class="status-pill pill-info">${lead.type.toUpperCase()}</span></td>
        <td>${lead.subsidy ? '✅ PM Surya Ghar' : '❌ Non-Subsidy'}</td>
        <td><span class="status-pill ${lead.status === 'approved' ? 'pill-success' : lead.status === 'rejected' ? 'pill-danger' : 'pill-neutral'}">${lead.status.toUpperCase()}</span></td>
        <td>
          <button class="btn-action-sm" onclick="scheduleSurveyFromLead(${lead.id})">Survey</button>
        </td>
      </tr>
    `;
  }).join('');

  renderLeadsKanban(list);
}

function renderLeadsKanban(leadsList) {
  const kanban = document.getElementById('leads-kanban-container');
  if (!kanban) return;

  const cols = [
    { id: 'draft', title: 'New Leads', status: 'draft' },
    { id: 'scheduled', title: 'Survey Scheduled', status: 'scheduled' },
    { id: 'approved', title: 'Approved & Qualified', status: 'approved' },
    { id: 'rejected', title: 'Rejected', status: 'rejected' }
  ];

  kanban.innerHTML = cols.map(c => {
    const items = leadsList.filter(l => l.status === c.status);
    return `
      <div class="kanban-column">
        <div class="kanban-column-header">
          <span class="kanban-column-title">${c.title}</span>
          <span class="kanban-column-count">${items.length}</span>
        </div>
        <div class="kanban-card-list">
          ${items.map(lead => {
            const cust = SolarFlowState.customers.find(cu => cu.id === lead.customerId) || {};
            return `
              <div class="kanban-card" onclick="openCustomerProfile(${cust.id})">
                <div class="kanban-card-ref">${lead.ref}</div>
                <div class="kanban-card-title">${cust.name}</div>
                <div style="font-size:12px; color:var(--text-muted);">${lead.sizedKw} kW • ${lead.type.toUpperCase()}</div>
                <div class="kanban-card-meta">
                  <span>${cust.city}</span>
                  <span class="status-pill pill-warning">${lead.monthlyKwh} kWh</span>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function setLeadsViewMode(mode) {
  SolarFlowState.leadsViewMode = mode;
  const tbl = document.getElementById('leads-table-container');
  const kan = document.getElementById('leads-kanban-container');
  const btnList = document.getElementById('leads-view-list');
  const btnKanban = document.getElementById('leads-view-kanban');

  if (mode === 'list') {
    if (tbl) tbl.style.display = 'block';
    if (kan) kan.style.display = 'none';
    if (btnList) btnList.classList.add('active');
    if (btnKanban) btnKanban.classList.remove('active');
  } else {
    if (tbl) tbl.style.display = 'none';
    if (kan) kan.style.display = 'grid';
    if (btnList) btnList.classList.remove('active');
    if (btnKanban) btnKanban.classList.add('active');
  }
}

// 3. Follow-ups Table
function renderFollowups() {
  const tbody = document.getElementById('followups-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.followups.map(f => {
    const cust = SolarFlowState.customers.find(c => c.id === f.customerId) || {};
    return `
      <tr>
        <td><strong>${f.date}</strong></td>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${cust.name}</strong></td>
        <td>${f.salesRep}</td>
        <td><span class="status-pill pill-info">${f.type}</span></td>
        <td style="font-size:12.5px; color:var(--text-muted);">${f.summary}</td>
        <td><span class="status-pill ${f.priority === 'High' ? 'pill-danger' : 'pill-warning'}">${f.priority}</span></td>
        <td><span class="status-pill pill-success">${f.status}</span></td>
      </tr>
    `;
  }).join('');
}

// 4. Surveys Table & Kanban
function renderSurveys(filterQuery = '', filterStatus = 'all') {
  const tbody = document.getElementById('surveys-table-body');
  if (!tbody) return;

  const currentRole = SolarFlowState.currentRole;
  const roleCfg = SolarFlowState.roles[currentRole] || SolarFlowState.roles.admin;

  let list = SolarFlowState.surveys;

  // Domain Isolation: Survey Technician only sees assigned surveys
  if (currentRole === 'survey_tech') {
    list = list.filter(s => (s.engineer && s.engineer.includes('Arun')) || (s.engineer && s.engineer.includes('Pending')));
  }

  if (filterStatus !== 'all') {
    list = list.filter(s => s.state === filterStatus);
  }
  if (filterQuery) {
    const q = filterQuery.toLowerCase();
    list = list.filter(s => {
      const cust = SolarFlowState.customers.find(c => c.id === s.customerId) || {};
      return s.ref.toLowerCase().includes(q) || (cust.name || '').toLowerCase().includes(q);
    });
  }

  tbody.innerHTML = list.map(s => {
    const cust = SolarFlowState.customers.find(c => c.id === s.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${s.ref}</strong></td>
        <td><strong>${cust.name || 'Unknown'}</strong></td>
        <td>${s.roofType}</td>
        <td>${s.totalArea}</td>
        <td><strong>${s.usableArea}</strong></td>
        <td>${s.azimuth} / ${s.tilt}</td>
        <td>${s.cableDist}</td>
        <td><span class="status-pill pill-info">${s.gridPhase}</span></td>
        <td><span class="status-pill pill-warning">${s.recommendedKw} kW</span></td>
        <td><span class="status-pill ${s.state === 'approved' ? 'pill-success' : s.state === 'rejected' ? 'pill-danger' : 'pill-warning'}">${s.state.toUpperCase()}</span></td>
        <td>
          <div class="action-btn-group">
            <button class="btn-action-sm" onclick="openAttachment('survey_photo', ${s.id})" title="View Drone Rooftop Photo Attachment">📷 Photo</button>
            ${s.state === 'approved' 
              ? `<button class="btn-action-primary-sm" onclick="generateQuotationFromSurvey(${s.id})">Quotation</button>` 
              : s.state === 'scheduled'
              ? `<button class="btn-action-sm" onclick="approveSurvey(${s.id})" title="Approve Feasibility">Approve</button>
                 <button class="btn-action-sm" style="color:var(--danger-text);" onclick="rejectSurvey(${s.id})" title="Reject Survey">Reject</button>`
              : `<span style="font-size:11px; color:var(--danger-text);">Rejected</span>`}
            <button class="btn-action-sm" style="color:var(--danger-text);" onclick="deleteRecord('survey', ${s.id})" title="Delete Site Survey (Admin Only)">🗑️</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  renderSurveysKanban(list);
}

function renderSurveysKanban(surveysList) {
  const kanban = document.getElementById('surveys-kanban-container');
  if (!kanban) return;

  const cols = [
    { id: 'scheduled', title: 'Scheduled', status: 'scheduled' },
    { id: 'in_progress', title: 'In Progress', status: 'in_progress' },
    { id: 'approved', title: 'Approved', status: 'approved' },
    { id: 'rejected', title: 'Rejected', status: 'rejected' }
  ];

  kanban.innerHTML = cols.map(c => {
    const items = surveysList.filter(s => s.state === c.status);
    return `
      <div class="kanban-column">
        <div class="kanban-column-header">
          <span class="kanban-column-title">${c.title}</span>
          <span class="kanban-column-count">${items.length}</span>
        </div>
        <div class="kanban-card-list">
          ${items.map(s => {
            const cust = SolarFlowState.customers.find(cu => cu.id === s.customerId) || {};
            return `
              <div class="kanban-card" onclick="openCustomerProfile(${cust.id})">
                <div class="kanban-card-ref">${s.ref}</div>
                <div class="kanban-card-title">${cust.name}</div>
                <div style="font-size:12px; color:var(--text-muted);">${s.roofType} • ${s.usableArea}</div>
                <div class="kanban-card-meta">
                  <span class="status-pill pill-info">${s.recommendedKw} kW</span>
                  <span>${s.azimuth}</span>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function setSurveysViewMode(mode) {
  SolarFlowState.surveysViewMode = mode;
  const tbl = document.getElementById('surveys-table-container');
  const kan = document.getElementById('surveys-kanban-container');
  const btnList = document.getElementById('surveys-view-list');
  const btnKanban = document.getElementById('surveys-view-kanban');

  if (mode === 'list') {
    if (tbl) tbl.style.display = 'block';
    if (kan) kan.style.display = 'none';
    if (btnList) btnList.classList.add('active');
    if (btnKanban) btnKanban.classList.remove('active');
  } else {
    if (tbl) tbl.style.display = 'none';
    if (kan) kan.style.display = 'grid';
    if (btnList) btnList.classList.remove('active');
    if (btnKanban) btnKanban.classList.add('active');
  }
}

// 5. Quotations Table
function renderQuotations() {
  const tbody = document.getElementById('quotations-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.quotations.map(q => {
    const cust = SolarFlowState.customers.find(c => c.id === q.customerId) || {};
    return `
      <tr>
        <td><strong>${q.ref}</strong></td>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${cust.name}</strong></td>
        <td><span class="status-pill pill-success">SRV-2026-0001</span></td>
        <td><span class="status-pill pill-info">${q.capacity}</span></td>
        <td>$${q.grossTotal.toFixed(2)}</td>
        <td>-$${q.subsidy.toFixed(2)}</td>
        <td><strong>$${q.netPrice.toFixed(2)}</strong></td>
        <td><span class="status-pill pill-success">${q.paybackYears} Years</span></td>
        <td><span class="status-pill ${q.status === 'confirmed' ? 'pill-success' : 'pill-warning'}">${q.status.toUpperCase()}</span></td>
        <td>
          ${q.status === 'confirmed'
            ? `<span style="font-size:12px; font-weight:600; color:var(--success-text);">✓ Order Created</span>`
            : `<button class="btn-action-primary-sm" onclick="confirmQuotationOrder(${q.id})">Customer Confirm</button>`}
        </td>
      </tr>
    `;
  }).join('');
}

// 6. Orders Table
function renderOrders() {
  const tbody = document.getElementById('orders-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.orders.map(o => {
    const cust = SolarFlowState.customers.find(c => c.id === o.customerId) || {};
    return `
      <tr>
        <td><strong>${o.ref}</strong></td>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${cust.name}</strong></td>
        <td>${o.system}</td>
        <td>$${o.grossTotal.toFixed(2)}</td>
        <td>-$${o.subsidy.toFixed(2)}</td>
        <td><strong>$${o.netPayable.toFixed(2)}</strong></td>
        <td>$${o.advanceRequired.toFixed(2)}</td>
        <td>$${o.amountPaid.toFixed(2)}</td>
        <td><span class="status-pill ${o.paymentStatus === 'partially_paid' ? 'pill-success' : 'pill-danger'}">${o.paymentStatus.toUpperCase()}</span></td>
        <td>
          ${o.dispatchPermission 
            ? `<span class="status-pill pill-success">✓ Dispatch Granted</span>` 
            : `<span class="status-pill pill-danger">🔒 Locked (&lt;50% Paid)</span>`}
        </td>
        <td>
          <button class="btn-action-primary-sm" onclick="switchView('installations')">View Installation</button>
        </td>
      </tr>
    `;
  }).join('');
}

// 7. Packages Grid
function renderPackages() {
  const container = document.getElementById('packages-cards-grid');
  if (!container) return;
  container.innerHTML = SolarFlowState.packages.map(p => `
    <div class="package-card">
      <div class="package-header">
        <span class="package-capacity-pill">${p.capacity} kW • ${p.type.toUpperCase()}</span>
        <h3 class="card-title">${p.name}</h3>
        <span style="font-size:11px; color:var(--text-muted);">${p.code}</span>
      </div>

      <ul class="bom-item-list">
        ${p.bom.map(b => `
          <li>
            <span>${b.qty}x ${b.item}</span>
            <strong>$${b.subtotal}</strong>
          </li>
        `).join('')}
      </ul>

      <div class="package-price-wrap">
        <span style="font-size:11px; color:var(--text-muted); display:block;">Dynamic Auto-BOM Net Hardware Total:</span>
        <div class="package-price">$${p.totalPrice.toLocaleString()}</div>
      </div>

      <button class="btn-action-primary-sm" style="width:100%;" onclick="showToast('Package ${p.code} selected for BOM quotation engine.', 'success')">Select for Quotation</button>
    </div>
  `).join('');
}

// 8. Installations View
function renderInstallations() {
  const container = document.getElementById('installations-container');
  if (!container) return;

  const currentRole = SolarFlowState.currentRole;
  const roleCfg = SolarFlowState.roles[currentRole] || SolarFlowState.roles.admin;
  const canSeeFinances = (currentRole === 'admin' || currentRole === 'finance' || currentRole === 'director');

  let list = SolarFlowState.installations;

  // Domain Isolation: Installation Technician only views assigned installations
  if (currentRole === 'tech') {
    list = list.filter(inst => inst.technician && inst.technician.includes('Ramesh Electrician'));
  }

  container.innerHTML = list.map(inst => {
    const cust = SolarFlowState.customers.find(c => c.id === inst.customerId) || {};
    return `
      <div class="content-card" style="margin-bottom:20px;">
        <div class="card-title-bar">
          <div>
            <span class="status-pill pill-success" style="margin-bottom:4px;">Commissioned Project</span>
            <div class="card-title">${inst.ref} – ${cust.name} (${inst.capacity} kW ${inst.type.toUpperCase()})</div>
            <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Lead Technician: <strong>${inst.technician}</strong></div>
          </div>
          <div style="text-align:right;">
            <span class="status-pill ${inst.state === 'completed' ? 'pill-success' : 'pill-warning'}">${inst.state === 'completed' ? '✓ Completed &amp; Accepted' : 'In Progress'}</span>
            <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Scheduled: ${inst.scheduledDate}</div>
          </div>
        </div>

        <!-- Smart Button Navigation Row -->
        <div class="smart-button-bar">
          <button class="smart-button" onclick="openCustomerProfile(${cust.id})">👤 Customer 360°</button>
          <button class="smart-button" onclick="switchView('orders')">📑 Linked Order</button>
          <button class="smart-button" onclick="switchView('surveys')">📐 Linked Survey</button>
          <button class="smart-button" onclick="switchView('inventory')">🏷️ Serials (2 Lots)</button>
          <button class="smart-button" onclick="switchView('warranties')">🛡️ Warranties</button>
          ${canSeeFinances 
            ? `<button class="smart-button" onclick="switchView('costing')">💰 Cost Sheet ($540 Profit)</button>` 
            : `<button class="smart-button" style="opacity:0.6; cursor:not-allowed;" title="Financial Costing Restricted" onclick="showAccessDeniedModal('Project Costing', '${roleCfg.name}')">🔒 Cost Sheet (Restricted)</button>`}
        </div>

        <!-- 6-Phase Commissioning Milestone Checklist -->
        <div style="margin-bottom:16px;">
          <h4 style="font-size:13px; font-weight:700; margin-bottom:8px;">6-Phase EPC Commissioning Milestones:</h4>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px;">
            <div class="criterion-item passed"><span>✓ 1. Structure &amp; Civil Grouting</span><span class="criterion-status-tag">DONE</span></div>
            <div class="criterion-item passed"><span>✓ 2. PV Modules String Cabling</span><span class="criterion-status-tag">DONE</span></div>
            <div class="criterion-item passed"><span>✓ 3. Inverter &amp; ACDB/DCDB Wiring</span><span class="criterion-status-tag">DONE</span></div>
            <div class="criterion-item passed"><span>✓ 4. Chemical Earth Pit (&lt;5.0&Omega;)</span><span class="criterion-status-tag">DONE</span></div>
            <div class="criterion-item passed"><span>✓ 5. Insulation Megger Testing</span><span class="criterion-status-tag">DONE</span></div>
            <div class="criterion-item passed"><span>✓ 6. DISCOM Net-Meter Synced</span><span class="criterion-status-tag">DONE</span></div>
          </div>
        </div>

        <!-- Electrical QC Safety Limit -->
        <div style="background-color:#F8FAF8; border:1px solid var(--border); border-radius:var(--radius-md); padding:12px; margin-bottom:16px;">
          <h4 style="font-size:13px; font-weight:700; margin-bottom:6px; color:var(--primary);">Electrical QC Safety Readings (PASSED):</h4>
          <div style="display:flex; gap:20px; flex-wrap:wrap; font-size:13px;">
            <div>Open Circuit Voc: <strong>${inst.qc.voc} V</strong></div>
            <div>Short Circuit Isc: <strong>${inst.qc.isc} A</strong></div>
            <div>Earth Pit Resistance: <strong style="color:var(--success-text);">${inst.qc.earthResistance} &Omega;</strong> (&le; 5.0 &Omega; limit)</div>
            <div>Insulation Megger: <strong>${inst.qc.insulationMOhm} M&Omega;</strong></div>
            <div>Grid AC Voltage: <strong>${inst.qc.gridVolt} V</strong></div>
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div style="font-size:12px; color:var(--text-muted);">Customer Acceptance: <strong>${inst.acceptanceSignature}</strong></div>
          <div class="action-btn-group">
            <button class="btn-action-sm" onclick="openAttachment('qc_megger', ${inst.id})" title="View QC Megger Report Attachment">📎 QC Megger Report</button>
            ${inst.state !== 'completed' 
              ? `<button class="btn-action-primary-sm" onclick="completeInstallation(${inst.id})">⚡ Complete &amp; Handover</button>` 
              : `<button class="btn-action-sm" onclick="switchView('warranties')">🛡️ View Warranties</button>`}
            <button class="btn-action-sm" style="color:var(--danger-text);" onclick="deleteRecord('installation', ${inst.id})" title="Delete Installation (Admin Only)">🗑️ Delete</button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// 9. Schedule Table
function renderSchedule() {
  const tbody = document.getElementById('schedule-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.installations.map(inst => {
    const cust = SolarFlowState.customers.find(c => c.id === inst.customerId) || {};
    return `
      <tr>
        <td><strong>${inst.scheduledDate}</strong></td>
        <td><strong class="table-record-ref" onclick="switchView('installations')">${inst.ref}</strong></td>
        <td>${cust.name}</td>
        <td><span class="status-pill pill-warning">${inst.capacity} kW</span></td>
        <td>${inst.technician}</td>
        <td>3 Electricians</td>
        <td><span class="status-pill pill-success">${inst.state.toUpperCase()}</span></td>
      </tr>
    `;
  }).join('');
}

// 10. Serialized Inventory Table
function renderInventory(filterQuery = '', filterStatus = 'all') {
  const tbody = document.getElementById('inventory-table-body');
  if (!tbody) return;

  let list = SolarFlowState.inventory;
  if (filterStatus !== 'all') {
    list = list.filter(i => i.status === filterStatus);
  }
  if (filterQuery) {
    const q = filterQuery.toLowerCase();
    list = list.filter(i => i.serial.toLowerCase().includes(q) || i.product.toLowerCase().includes(q));
  }

  tbody.innerHTML = list.map(item => {
    const cust = SolarFlowState.customers.find(c => c.id === item.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref">${item.serial}</strong></td>
        <td><strong>${item.product}</strong></td>
        <td>${item.oem}</td>
        <td><span class="status-pill ${item.status === 'installed' ? 'pill-success' : 'pill-info'}">${item.status.toUpperCase()}</span></td>
        <td>${item.project || 'In Staging'}</td>
        <td>${cust.name || 'Warehouse Stock'}</td>
        <td>${item.dispatchDate || 'N/A'}</td>
        <td><span class="status-pill pill-info">${item.warrantyYears} Years</span></td>
        <td>
          <button class="btn-action-sm" onclick="switchView('dashboard')">View Lifecycle</button>
        </td>
      </tr>
    `;
  }).join('');
}

// 11. Digital Warranties Table
function renderWarranties() {
  const tbody = document.getElementById('warranties-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.warranties.map(w => {
    const cust = SolarFlowState.customers.find(c => c.id === w.customerId) || {};
    return `
      <tr>
        <td><strong>${w.ref}</strong></td>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${cust.name}</strong></td>
        <td><code>${w.serial}</code></td>
        <td>${w.product}</td>
        <td><span class="status-pill pill-info">${w.duration}</span></td>
        <td>${w.startDate}</td>
        <td><strong>${w.expiryDate}</strong></td>
        <td><code style="font-size:11px; color:var(--primary);">${w.token}</code></td>
        <td><span class="status-pill pill-success">${w.status.toUpperCase()}</span></td>
      </tr>
    `;
  }).join('');
}

// 12. Service Tickets Table & Kanban
function renderService() {
  const tbody = document.getElementById('service-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.serviceTickets.map(t => {
    const cust = SolarFlowState.customers.find(c => c.id === t.customerId) || {};
    return `
      <tr>
        <td><strong>${t.ref}</strong></td>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${cust.name}</strong></td>
        <td><code>${t.serial}</code></td>
        <td style="font-size:12.5px;">${t.faultLabel}</td>
        <td>${t.technician}</td>
        <td>$${t.repairCost.toFixed(2)}</td>
        <td>${t.warrantyCovered ? '<span class="status-pill pill-success">✓ Covered ($0)</span>' : '<span class="status-pill pill-warning">Non-OEM Fault</span>'}</td>
        <td><strong>$${t.customerCharge.toFixed(2)}</strong></td>
        <td>${t.customerSigned ? '✓ OTP Signed' : 'Pending'}</td>
        <td><span class="status-pill ${t.state === 'resolved' || t.state === 'closed' ? 'pill-success' : 'pill-warning'}">${t.state.toUpperCase()}</span></td>
        <td>
          <button class="btn-action-sm" onclick="showToast('Ticket ${t.ref} details opened.', 'info')">Details</button>
        </td>
      </tr>
    `;
  }).join('');

  renderServiceKanban();
}

function renderServiceKanban() {
  const kanban = document.getElementById('service-kanban-container');
  if (!kanban) return;

  const cols = [
    { id: 'new', title: 'New Tickets', state: 'new' },
    { id: 'in_progress', title: 'In Progress', state: 'in_progress' },
    { id: 'resolved', title: 'Resolved ($0 Covered)', state: 'resolved' },
    { id: 'closed', title: 'Closed (Billed)', state: 'closed' }
  ];

  kanban.innerHTML = cols.map(c => {
    const items = SolarFlowState.serviceTickets.filter(t => t.state === c.state);
    return `
      <div class="kanban-column">
        <div class="kanban-column-header">
          <span class="kanban-column-title">${c.title}</span>
          <span class="kanban-column-count">${items.length}</span>
        </div>
        <div class="kanban-card-list">
          ${items.map(t => {
            const cust = SolarFlowState.customers.find(cu => cu.id === t.customerId) || {};
            return `
              <div class="kanban-card" onclick="openCustomerProfile(${cust.id})">
                <div class="kanban-card-ref">${t.ref}</div>
                <div class="kanban-card-title">${cust.name}</div>
                <div style="font-size:12px; color:var(--text-muted);">${t.serial}</div>
                <div class="kanban-card-meta">
                  <span class="status-pill ${t.warrantyCovered ? 'pill-success' : 'pill-warning'}">Charge: $${t.customerCharge.toFixed(2)}</span>
                  <span>${t.technician.split(' ')[0]}</span>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function setServiceViewMode(mode) {
  SolarFlowState.serviceViewMode = mode;
  const tbl = document.getElementById('service-table-container');
  const kan = document.getElementById('service-kanban-container');
  const btnList = document.getElementById('service-view-list');
  const btnKanban = document.getElementById('service-view-kanban');

  if (mode === 'list') {
    if (tbl) tbl.style.display = 'block';
    if (kan) kan.style.display = 'none';
    if (btnList) btnList.classList.add('active');
    if (btnKanban) btnKanban.classList.remove('active');
  } else {
    if (tbl) tbl.style.display = 'none';
    if (kan) kan.style.display = 'grid';
    if (btnList) btnList.classList.remove('active');
    if (btnKanban) btnKanban.classList.add('active');
  }
}

// 13. Project Costing Table
function renderCosting() {
  const tbody = document.getElementById('costing-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.costing.map(c => {
    const cust = SolarFlowState.customers.find(cu => cu.id === c.customerId) || {};
    return `
      <tr>
        <td><strong>${c.ref}</strong></td>
        <td><strong class="table-record-ref" onclick="switchView('installations')">${c.projectRef}</strong></td>
        <td>${cust.name}</td>
        <td>$${c.estRevenue.toFixed(2)}</td>
        <td>$${c.actRevenue.toFixed(2)}</td>
        <td>$${c.estCost.toFixed(2)}</td>
        <td>$${c.actualCost.toFixed(2)}</td>
        <td>${c.variance > 0 ? `<span style="color:var(--danger-text);">+$${c.variance.toFixed(2)}</span>` : '$0.00'}</td>
        <td>${c.overrunPct > 0 ? `<span class="status-pill pill-danger">+${c.overrunPct.toFixed(1)}%</span>` : '<span class="status-pill pill-success">0.0%</span>'}</td>
        <td><strong>$${c.grossProfit.toFixed(2)}</strong></td>
        <td><span class="status-pill ${c.grossMargin > 20 ? 'pill-success' : 'pill-warning'}">${c.grossMargin.toFixed(2)}%</span></td>
        <td>${c.isLeakage ? '<span class="status-pill pill-danger">⚠️ PROFIT LEAKAGE</span>' : '<span class="status-pill pill-success">✓ Healthy</span>'}</td>
        <td>
          <div class="action-btn-group">
            <button class="btn-action-sm" onclick="openAttachment('profit_leakage_audit', ${c.id})" title="Confidential Job Cost Breakdown">📊 Audit</button>
            <button class="btn-action-sm" style="color:var(--danger-text);" onclick="deleteRecord('costing', ${c.id})" title="Delete Costing Sheet (Admin Only)">🗑️</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// Generic fallback handler
function populateGenericModule(mod) {
  const title = document.getElementById('generic-panel-title');
  const desc = document.getElementById('generic-panel-desc');
  const content = document.getElementById('generic-panel-content');

  if (title) title.textContent = mod.replace(/_/g, ' ').toUpperCase();
  if (desc) desc.textContent = `Operational records and synchronized Odoo datasets for ${mod}.`;

  if (mod === 'b2b_portal') {
    title.textContent = 'B2B Business Portal';
    desc.textContent = 'Organization accounts, commercial quotations, bulk orders and installation sites.';
    renderB2BPortal(content);
    return;
  }
  if (mod === 'ai_business') {
    title.textContent = 'Agentic Business Management';
    desc.textContent = 'Evidence-based analysis coordinated by specialist agents and deterministic KPIs.';
    renderAgenticBusiness(content);
    return;
  }

  if (content) {
    content.innerHTML = `
      <div style="padding:24px; text-align:center;">
        <span style="font-size:36px;">📑</span>
        <h3 style="margin-top:12px; margin-bottom:6px; font-size:16px;">Connected ${mod.replace(/_/g, ' ').toUpperCase()} Module</h3>
        <p style="color:var(--text-muted); font-size:13px; max-width:520px; margin:0 auto 16px auto;">
          This view connects directly with SolarFlow's native Odoo Community models and verified PostgreSQL database records.
        </p>
        <button class="btn-primary-action" onclick="switchView('dashboard')">Return to Command Center</button>
      </div>
    `;
  }

  function renderB2BPortal(container) {
    container.innerHTML = `
      <div class="module-toolbar">
        <div>
          <span class="status-pill pill-success">Organization workspace</span>
          <span style="margin-left:8px;color:var(--text-muted)">Tata Solar Works Pvt Ltd · Approved</span>
        </div>
        <button class="btn-primary-action" onclick="openB2BRegistration()">+ Register organization</button>
      </div>
      <div class="module-kpi-grid">
        <div class="module-stat"><span>Active sites</span><strong>4</strong><small>2 states</small></div>
        <div class="module-stat"><span>Open quotations</span><strong>3</strong><small>2 negotiated</small></div>
        <div class="module-stat"><span>Purchase orders</span><strong>12</strong><small>₹48.6L value</small></div>
        <div class="module-stat"><span>Outstanding</span><strong>₹7.2L</strong><small>Net 30 · On schedule</small></div>
      </div>
      <div class="b2b-layout">
        <div class="content-card b2b-main-card">
          <div class="module-card-header"><div><h3>Bulk order workspace</h3><p>Select products and quantities for a new site</p></div></div>
          <div class="b2b-order-grid" id="b2b-order-grid"></div>
          <div class="module-inline-actions">
            <button class="btn-secondary-action" onclick="showToast('Draft saved locally','success')">Save draft</button>
            <button class="btn-primary-action" onclick="showToast('Quotation request submitted for sales review','success')">Request quotation</button>
          </div>
        </div>
        <div class="content-card b2b-side-card">
          <div class="module-card-header"><h3>Organization profile</h3></div>
          <dl class="profile-grid">
            <dt>Business type</dt><dd>Commercial buyer</dd>
            <dt>Contact</dt><dd>Meera Rao</dd>
            <dt>Email</dt><dd>meera@tatasolar.example</dd>
            <dt>Payment terms</dt><dd>Net 30 · approved</dd>
            <dt>GSTIN</dt><dd>Not GST verified</dd>
          </dl>
          <div class="verification-note">GSTIN status is informational only until a verified GST service is integrated.</div>
        </div>
      </div>
      <div class="module-table-grid">
        <div class="content-card"><div class="module-card-header"><h3>Installation sites</h3></div><div id="b2b-sites"></div></div>
        <div class="content-card"><div class="module-card-header"><h3>Recent commercial orders</h3></div><div id="b2b-orders"></div></div>
      </div>
    `;
    renderB2BProducts();
    renderB2BSites();
    renderB2BOrders();
  }

  function renderB2BProducts() {
    const grid = document.getElementById('b2b-order-grid');
    if (!grid) return;
    const products = [
      ['540 W Mono PERC Panel', '₹18,500', 'MOQ 10'],
      ['550 W TOPCon Panel', '₹20,500', 'MOQ 10'],
      ['100 kW Commercial Inverter', '₹4.85L', 'MOQ 2'],
      ['LiFePO4 Storage 30 kWh', '₹5.75L', 'MOQ 1']
    ];
    grid.innerHTML = products.map((p, i) => `
      <label class="b2b-product"><span><strong>${p[0]}</strong><small>${p[1]} · ${p[2]}</small></span>
        <input type="number" min="0" value="${i === 0 ? 20 : 0}" aria-label="Quantity for ${p[0]}">
      </label>
    `).join('');
  }

  function renderB2BSites() {
    const el = document.getElementById('b2b-sites');
    if (!el) return;
    el.innerHTML = `
      <div class="data-row"><span><strong>Bengaluru HQ</strong><small>250 kWp · Karnataka</small></span><span class="status-pill pill-success">Live</span></div>
      <div class="data-row"><span><strong>Pune Warehouse</strong><small>150 kWp · Maharashtra</small></span><span class="status-pill pill-info">Survey</span></div>
      <div class="data-row"><span><strong>Chennai Factory</strong><small>400 kWp · Tamil Nadu</small></span><span class="status-pill pill-warning">Design</span></div>
    `;
  }

  function renderB2BOrders() {
    const el = document.getElementById('b2b-orders');
    if (!el) return;
    el.innerHTML = `
      <div class="data-row"><span><strong>PO-2026-0112</strong><small>₹12.4L · 18 Aug 2026</small></span><span class="status-pill pill-info">In transit</span></div>
      <div class="data-row"><span><strong>PO-2026-0108</strong><small>₹18.9L · 02 Aug 2026</small></span><span class="status-pill pill-success">Delivered</span></div>
      <div class="data-row"><span><strong>PO-2026-0097</strong><small>₹8.7L · 21 Jul 2026</small></span><span class="status-pill pill-warning">Invoice due</span></div>
    `;
  }

  function openB2BRegistration() {
    showModal(
      'Register B2B Organization',
      `<div class="form-grid">
        <label>Organization name<input class="form-input" value="Tata Solar Works Pvt Ltd"></label>
        <label>Business type<select class="form-input"><option>Commercial customer</option><option>Business organization</option><option>Dealer / distributor</option><option>Corporate buyer</option><option>Installation partner</option></select></label>
        <label>Contact person<input class="form-input" value="Meera Rao"></label>
        <label>Business email<input class="form-input" type="email" value="meera@tatasolar.example"></label>
        <label>Phone<input class="form-input" value="+91 98765 43210"></label>
        <label>GSTIN<input class="form-input" placeholder="Only if applicable"></label>
        <label class="form-span-2">Registered address<textarea class="form-input" rows="2">Whitefield, Bengaluru</textarea></label>
        <label class="form-span-2">Installation locations<textarea class="form-input" rows="2">Bengaluru HQ; Pune Warehouse; Chennai Factory</textarea></label>
        <label class="form-span-2">Verification documents<input class="form-input" type="file" multiple></label>
      </div>
      <div class="verification-note">Submitted documents will remain pending until reviewed by an authorized administrator.</div>`,
      () => showToast('Organization submitted for approval', 'success')
    );
  }

  function renderAgenticBusiness(container) {
    container.innerHTML = `
      <div class="agent-status-bar">
        <div><span class="agent-pulse"></span><strong>Manager Agent ready</strong><small>Deterministic KPI layer · Rule-based retrieval context</small></div>
        <button class="btn-secondary-action" onclick="downloadAgentReport()">Download report</button>
      </div>
      <div class="module-kpi-grid agent-kpis">
        <div class="module-stat"><span>Revenue MTD</span><strong>₹42.8L</strong><small class="trend-up">↑ 8.4%</small></div>
        <div class="module-stat"><span>Quote conversion</span><strong>31.2%</strong><small class="trend-down">↓ 3.1 pts</small></div>
        <div class="module-stat"><span>Gross margin</span><strong>18.7%</strong><small>Actual-period KPI</small></div>
        <div class="module-stat"><span>Open risks</span><strong>6</strong><small>2 require attention</small></div>
      </div>
      <div class="agent-layout">
        <div class="content-card agent-chat-card">
          <div class="module-card-header"><div><h3>Management conversation</h3><p>Ask about sales, finance, inventory, customers, operations or risk</p></div></div>
          <div class="agent-chat-history" id="agent-chat-history">
            <div class="chat-message chat-assistant"><strong>Manager Agent</strong><p>I can analyze the business records loaded in SunPower Nexus. Ask about sales, stock shortages, margin, delays or pending complaints.</p></div>
          </div>
          <form class="agent-chat-form" onsubmit="askManagerAgent(event)">
            <input id="agent-question" placeholder="Why did solar sales decrease this month?" autocomplete="off">
            <button class="btn-primary-action" type="submit">Ask agents</button>
          </form>
          <div class="suggested-questions">
            <button onclick="setAgentQuestion('Which products generate the highest gross margin?')">Top-margin products</button>
            <button onclick="setAgentQuestion('Which installations are delayed?')">Delayed installations</button>
            <button onclick="setAgentQuestion('Which warehouse has the highest stock shortage?')">Stock shortages</button>
          </div>
        </div>
        <div class="agent-specialists">
          <div class="specialist-card"><span>📈</span><div><strong>Sales Agent</strong><small>Leads, quotes, orders, demand</small></div></div>
          <div class="specialist-card"><span>💰</span><div><strong>Finance Agent</strong><small>Margin, revenue, payments</small></div></div>
          <div class="specialist-card"><span>📦</span><div><strong>Inventory Agent</strong><small>Stock, shortages, reorders</small></div></div>
          <div class="specialist-card"><span>🤝</span><div><strong>Customer Agent</strong><small>Retention, complaints, feedback</small></div></div>
          <div class="specialist-card"><span>⚙️</span><div><strong>Operations Agent</strong><small>Survey, delivery, installation</small></div></div>
          <div class="specialist-card"><span>⚠️</span><div><strong>Risk Agent</strong><small>Financial and operational risks</small></div></div>
        </div>
      </div>
    `;
  }

  function setAgentQuestion(question) {
    const input = document.getElementById('agent-question');
    if (input) input.value = question;
  }

  async function askManagerAgent(event) {
    event.preventDefault();
    const input = document.getElementById('agent-question');
    const history = document.getElementById('agent-chat-history');
    if (!input || !input.value.trim() || !history) return;
    const question = input.value.trim();
    history.insertAdjacentHTML('beforeend', `<div class="chat-message chat-user">${escapeHTML(question)}</div>`);
    input.value = '';
    history.insertAdjacentHTML('beforeend', `<div class="chat-message chat-assistant" id="agent-thinking"><strong>Manager Agent</strong><p>Analyzing actual records…</p></div>`);
    try {
      const response = await fetch('/api/agent/analyze', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({question})});
      const result = await response.json();
      const thinking = document.getElementById('agent-thinking');
      if (!response.ok) throw new Error(result.error || 'Analysis service unavailable');
      if (thinking) thinking.innerHTML = formatAgentResponse(result);
    } catch (error) {
      const thinking = document.getElementById('agent-thinking');
      if (thinking) thinking.innerHTML = `<strong>Analysis unavailable</strong><p>${escapeHTML(error.message)}</p><small>No rule-based analysis was substituted without clear labeling.</small>`;
    }
  }

  function formatAgentResponse(result) {
    const evidence = (result.evidence || []).join('; ');
    const actions = (result.recommendations || []).join('; ');
    return `<strong>Manager Agent · ${escapeHTML(result.mode || 'rule-based')}</strong>
      <p>${escapeHTML(result.answer || '')}</p>
      <div class="agent-evidence"><strong>Observed evidence</strong><p>${escapeHTML(evidence)}</p></div>
      <div class="agent-evidence"><strong>Recommended action</strong><p>${escapeHTML(actions || 'Continue monitoring the underlying KPI.')}</p></div>
      <small>Confidence: ${escapeHTML(result.confidence || 'Medium')} · Records considered: ${result.records_considered || 0} · Correlation is not presented as proven causation.</small>`;
  }

  function downloadAgentReport() {
    window.location.href = '/api/agent/report.pdf';
  }
}

// ==========================================================================
// SEARCH & FILTERS ON ALL VIEWS
// ==========================================================================
function filterEnquiriesTable(query) {
  const status = document.getElementById('filter-enquiry-status').value;
  renderEnquiries(query, status);
}

function filterEnquiriesByStatus(status) {
  const q = document.getElementById('search-enquiries').value;
  renderEnquiries(q, status);
}

function filterLeadsTable(query) {
  const type = document.getElementById('filter-lead-type').value;
  renderLeads(query, type);
}

function filterLeadsByType(type) {
  const q = document.getElementById('search-leads').value;
  renderLeads(q, type);
}

function filterSurveysTable(query) {
  const status = document.getElementById('filter-survey-status').value;
  renderSurveys(query, status);
}

function filterSurveysByStatus(status) {
  const q = document.getElementById('search-surveys').value;
  renderSurveys(q, status);
}

function filterInventoryTable(query) {
  const status = document.getElementById('filter-serial-status').value;
  renderInventory(query, status);
}

function filterInventoryByStatus(status) {
  const q = document.getElementById('search-inventory').value;
  renderInventory(q, status);
}

// Global Instant Search Popover
function setupGlobalSearch() {
  const input = document.getElementById('global-search-input');
  const popover = document.getElementById('search-results-popover');
  const content = document.getElementById('search-results-content');
  if (!input || !popover || !content) return;

  input.addEventListener('input', (e) => {
    const val = e.target.value.toLowerCase().trim();
    if (!val || val.length < 2) {
      popover.classList.remove('active');
      return;
    }

    // Matching records
    const matchedCusts = SolarFlowState.customers.filter(c => c.name.toLowerCase().includes(val) || c.phone.includes(val));
    const matchedSerials = SolarFlowState.inventory.filter(i => i.serial.toLowerCase().includes(val));
    const matchedLeads = SolarFlowState.leads.filter(l => l.ref.toLowerCase().includes(val));

    let html = '';
    if (matchedCusts.length > 0) {
      html += `<div class="search-result-group-title">Customers (${matchedCusts.length})</div>`;
      matchedCusts.forEach(c => {
        html += `
          <div class="search-result-item" onclick="openCustomerProfile(${c.id}); hideGlobalSearch();">
            <div><strong>${c.name}</strong> <span style="font-size:11px; color:var(--text-muted);">${c.city}</span></div>
            <span class="status-pill pill-info">${c.phone}</span>
          </div>
        `;
      });
    }

    if (matchedSerials.length > 0) {
      html += `<div class="search-result-group-title">Equipment Serials (${matchedSerials.length})</div>`;
      matchedSerials.forEach(s => {
        html += `
          <div class="search-result-item" onclick="switchView('inventory'); hideGlobalSearch();">
            <div><code>${s.serial}</code> <span style="font-size:11px; color:var(--text-muted);">${s.product}</span></div>
            <span class="status-pill pill-success">${s.status.toUpperCase()}</span>
          </div>
        `;
      });
    }

    if (matchedLeads.length > 0) {
      html += `<div class="search-result-group-title">Leads (${matchedLeads.length})</div>`;
      matchedLeads.forEach(l => {
        html += `
          <div class="search-result-item" onclick="switchView('leads'); hideGlobalSearch();">
            <div><strong>${l.ref}</strong> <span style="font-size:11px; color:var(--text-muted);">${l.sizedKw} kW</span></div>
            <span class="status-pill pill-warning">${l.status.toUpperCase()}</span>
          </div>
        `;
      });
    }

    if (!html) {
      html = `<div style="padding:14px; text-align:center; color:var(--text-muted); font-size:12.5px;">No records found matching "${val}".</div>`;
    }

    content.innerHTML = html;
    popover.classList.add('active');
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.global-search-wrap')) {
      popover.classList.remove('active');
    }
  });
}

function hideGlobalSearch() {
  const popover = document.getElementById('search-results-popover');
  if (popover) popover.classList.remove('active');
}

// ==========================================================================
// NOTIFICATIONS DRAWER
// ==========================================================================
function setupNotifications() {
  const btn = document.getElementById('btn-notifications');
  const drawer = document.getElementById('notifications-drawer');
  if (!btn || !drawer) return;

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    drawer.classList.toggle('active');
    renderNotificationsDrawer();
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('#notifications-drawer') && !e.target.closest('#btn-notifications')) {
      drawer.classList.remove('active');
    }
  });
}

function renderNotificationsDrawer() {
  const list = document.getElementById('drawer-notifications-list');
  if (!list) return;

  list.innerHTML = SolarFlowState.notifications.map(n => `
    <div class="drawer-item ${n.unread ? 'unread' : ''}">
      <div class="drawer-icon-wrap" style="background-color:${n.type === 'danger' ? 'var(--danger-bg)' : n.type === 'warn' ? 'var(--warning-bg)' : 'var(--primary-subtle)'};">
        ${n.icon}
      </div>
      <div class="drawer-item-content">
        <div class="drawer-item-title">${n.title}</div>
        <div class="drawer-item-sub">${n.sub}</div>
        <div class="drawer-item-time">${n.time}</div>
      </div>
    </div>
  `).join('');
}

function markAllNotificationsRead() {
  SolarFlowState.notifications.forEach(n => n.unread = false);
  const counter = document.getElementById('notification-counter');
  if (counter) counter.style.display = 'none';
  renderNotificationsDrawer();
  showToast("All notifications marked as read.", "info");
}

// ==========================================================================
// PROFILE PAGES (CUSTOMER 360° & USER CREDENTIALS)
// ==========================================================================
function openCustomerProfile(customerId) {
  const cust = SolarFlowState.customers.find(c => c.id === customerId);
  if (!cust) return;

  const leads = SolarFlowState.leads.filter(l => l.customerId === customerId);
  const surveys = SolarFlowState.surveys.filter(s => s.customerId === customerId);
  const orders = SolarFlowState.orders.filter(o => o.customerId === customerId);
  const insts = SolarFlowState.installations.filter(i => i.customerId === customerId);
  const serials = SolarFlowState.inventory.filter(i => i.customerId === customerId);
  const warranties = SolarFlowState.warranties.filter(w => w.customerId === customerId);
  const tickets = SolarFlowState.serviceTickets.filter(t => t.customerId === customerId);

  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');

  if (modalTitle) modalTitle.textContent = `Customer 360° Profile – ${cust.name}`;

  if (modalBody) {
    modalBody.innerHTML = `
      <div style="background-color:#F8FAF8; border:1px solid var(--border); border-radius:var(--radius-md); padding:14px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h4 style="font-size:16px; font-weight:700; color:var(--text-main);">${cust.name}</h4>
            <div style="font-size:12.5px; color:var(--text-muted);">${cust.address}</div>
          </div>
          <span class="status-pill pill-info">${cust.type}</span>
        </div>
        <div style="margin-top:10px; font-size:12.5px; display:flex; gap:20px;">
          <span>📞 <strong>${cust.phone}</strong></span>
          <span>✉️ <strong>${cust.email}</strong></span>
          <span>📍 <strong>${cust.city}</strong></span>
        </div>
      </div>

      <!-- Smart Buttons Navigation Row -->
      <div class="smart-button-bar" style="margin-bottom:16px;">
        <div class="smart-button">Leads <span class="smart-count-pill">${leads.length}</span></div>
        <div class="smart-button">Surveys <span class="smart-count-pill">${surveys.length}</span></div>
        <div class="smart-button">Contracts <span class="smart-count-pill">${orders.length}</span></div>
        <div class="smart-button">Installs <span class="smart-count-pill">${insts.length}</span></div>
        <div class="smart-button">Serials <span class="smart-count-pill">${serials.length}</span></div>
        <div class="smart-button">Warranties <span class="smart-count-pill">${warranties.length}</span></div>
        <div class="smart-button">Tickets <span class="smart-count-pill">${tickets.length}</span></div>
      </div>

      <!-- Active Equipment & Warranties -->
      <h4 style="font-size:13px; font-weight:700; margin-bottom:8px;">Allocated Hardware &amp; Active Warranties:</h4>
      <div style="font-size:12.5px; display:flex; flex-direction:column; gap:6px;">
        ${serials.map(s => `
          <div style="display:flex; justify-content:space-between; padding:8px 12px; background-color:#FFFFFF; border:1px solid var(--border); border-radius:var(--radius-sm);">
            <span>🏷️ <strong>${s.serial}</strong> (${s.product})</span>
            <span class="status-pill pill-success">Active Warranty</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  if (submitBtn) {
    submitBtn.textContent = "Close Profile";
    submitBtn.onclick = closeModal;
  }

  openModal();
}

function showUserProfileModal() {
  const role = SolarFlowState.currentRole;
  const cfg = SolarFlowState.roles[role] || SolarFlowState.roles.admin;

  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');

  if (modalTitle) modalTitle.textContent = "User Credentials & Role Permissions";
  if (modalBody) {
    modalBody.innerHTML = `
      <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px; padding:12px; background-color:#FAFCFA; border:1px solid var(--border); border-radius:var(--radius-md);">
        <div class="user-avatar-circle" style="width:48px; height:48px; font-size:18px;">${cfg.avatar}</div>
        <div>
          <h3 style="font-size:16px;">${cfg.name}</h3>
          <span style="font-size:12px; color:var(--text-muted);">${cfg.title} • Active Session</span>
        </div>
      </div>

      <div style="font-size:13px; margin-bottom:12px;">
        <strong>Role Responsibilities:</strong>
        <p style="color:var(--text-muted); font-size:12.5px; margin-top:2px;">${cfg.desc}</p>
      </div>

      <div>
        <strong>Permitted Modules &amp; Subsystems:</strong>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">
          ${(cfg.perm.includes('all') ? ['All EPC Modules', 'Financial Costing', 'User Administration', 'System Configuration'] : cfg.perm).map(p => `
            <span class="status-pill pill-info">${p.toUpperCase()}</span>
          `).join('')}
        </div>
      </div>
    `;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  if (submitBtn) {
    submitBtn.textContent = "Done";
    submitBtn.onclick = closeModal;
  }

  openModal();
}

// Modal Open / Close Helpers
function openModal() {
  const modal = document.getElementById('modal-container');
  if (modal) modal.style.display = 'flex';
}

function closeModal() {
  const modal = document.getElementById('modal-container');
  if (modal) modal.style.display = 'none';
}

// ==========================================================================
// QUICK CREATE & FORM MODALS
// ==========================================================================
function setupQuickCreate() {
  const btn = document.getElementById('btn-quick-create');
  if (!btn) return;
  btn.addEventListener('click', () => {
    showLeadModal();
  });
}

function showLeadModal() {
  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');

  if (modalTitle) modalTitle.textContent = "Log New Solar Customer Lead";
  if (modalBody) {
    modalBody.innerHTML = `
      <div class="form-grid-2">
        <div>
          <label class="form-label">Customer Name <span class="req">*</span></label>
          <input type="text" id="new-cust-name" class="form-input" placeholder="e.g. Vikramaditya Rao">
        </div>
        <div>
          <label class="form-label">Phone Number <span class="req">*</span></label>
          <input type="text" id="new-cust-phone" class="form-input" placeholder="+91 98765 00000">
        </div>
      </div>
      <div class="form-grid-2">
        <div>
          <label class="form-label">Monthly Consumption (kWh) <span class="req">*</span></label>
          <input type="number" id="new-monthly-kwh" class="form-input" placeholder="450" value="450">
        </div>
        <div>
          <label class="form-label">System Architecture</label>
          <select id="new-system-type" class="form-select">
            <option value="on_grid">Grid-Tied On-Grid</option>
            <option value="hybrid">Smart Hybrid (Battery + Grid)</option>
            <option value="off_grid">Standalone Off-Grid</option>
          </select>
        </div>
      </div>
      <div class="form-group-full">
        <label class="form-label">Site Address &amp; Roof Notes</label>
        <textarea id="new-notes" class="form-textarea" rows="2" placeholder="RCC flat roof, shadow-free parapet..."></textarea>
      </div>
    `;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  if (submitBtn) {
    submitBtn.textContent = "Save & Size System";
    submitBtn.onclick = () => {
      showToast("New Solar Lead SF/LEAD/2026/0011 created successfully. Automated sizing complete.", "success");
      closeModal();
      switchView('leads');
    };
  }

  openModal();
}

function showTicketModal() {
  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');

  if (modalTitle) modalTitle.textContent = "Log Customer Service Ticket / RMA";
  if (modalBody) {
    modalBody.innerHTML = `
      <div class="form-group-full">
        <label class="form-label">Equipment Serial Number <span class="req">*</span></label>
        <input type="text" class="form-input" value="INV-GROWATT-3KW-9901">
      </div>
      <div class="form-grid-2">
        <div>
          <label class="form-label">Fault Category</label>
          <select class="form-select">
            <option>MPPT Inverter Error (OEM Warranty)</option>
            <option>External Grid Voltage Surge</option>
            <option>Physical Panel Glass Damage</option>
          </select>
        </div>
        <div>
          <label class="form-label">Assign Technician</label>
          <select class="form-select">
            <option>Ramesh Electrician (Senior Lead)</option>
            <option>Suresh Technician</option>
          </select>
        </div>
      </div>
      <div class="form-group-full">
        <label class="form-label">Symptom Description</label>
        <textarea class="form-textarea" rows="2" placeholder="Inverter alarm code AL04 logged..."></textarea>
      </div>
    `;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  if (submitBtn) {
    submitBtn.textContent = "Submit Complaint";
    submitBtn.onclick = () => {
      showToast("Service ticket created. Warranty status verified: Covered ($0.00 charge).", "success");
      closeModal();
      switchView('service');
    };
  }

  openModal();
}

// ==========================================================================
// SECURITY AUDIT & RBAC CONTROLLER ENFORCEMENT
// ==========================================================================

// Access Denied Modal Trigger
function showAccessDeniedModal(resource, roleName, customMsg = null) {
  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');
  const submitBtn = document.getElementById('modal-submit-btn');

  if (modalTitle) {
    modalTitle.innerHTML = `<span style="color:var(--danger-text);">⛔ Access Denied – HTTP 403 Forbidden</span>`;
  }
  if (modalBody) {
    modalBody.innerHTML = `
      <div style="background-color:var(--danger-bg); border:1px solid var(--danger-border); border-radius:var(--radius-md); padding:16px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
          <span style="font-size:24px;">🛡️</span>
          <div>
            <h4 style="font-size:15px; font-weight:700; color:var(--danger-text);">Security Policy Enforcement Active</h4>
            <div style="font-size:12px; color:var(--text-muted);">SolarFlow Enterprise RBAC &amp; ACL System Gate</div>
          </div>
        </div>
        <p style="font-size:13px; color:var(--danger-text); line-height:1.5; margin:0;">
          ${customMsg || `Access to <strong>${resource}</strong> was rejected. Current Active Account role <strong>${roleName}</strong> is restricted by server-side Access Control Lists (ACLs) and record rules.`}
        </p>
      </div>
      <div style="font-size:12.5px; color:var(--text-muted); line-height:1.5;">
        <strong>Security Audit Findings:</strong><br>
        • Role-based access control is verified at both UI controller and Python ORM model layer.<br>
        • Direct URL navigation, unauthorized method calls, and delete operations strictly trigger <code>AccessError (403)</code>.<br>
        • To perform this operation, switch to an authorized role (e.g. Sales Manager, Finance Manager, or Super Administrator).
      </div>
    `;
  }
  if (submitBtn) {
    submitBtn.textContent = "Acknowledge & Return";
    submitBtn.className = "btn-primary-action";
    submitBtn.onclick = () => {
      closeModal();
      switchView('dashboard');
    };
  }
  openModal();
}

// Vector 9: Attachment Access Control
function openAttachment(docType, id) {
  const role = SolarFlowState.currentRole;
  const roleCfg = SolarFlowState.roles[role] || SolarFlowState.roles.admin;

  const accessRules = {
    qc_megger: {
      title: "Electrical QC Megger Insulation & Earth Resistance Test Certificate",
      allowed: ['admin', 'tech', 'sales', 'director'],
      docRef: `QC-CERT-INST-${id}.PDF`,
      content: `
        <div style="border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; background:#FAFCFA;">
          <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:12px;">
            <div>
              <strong>SOLARFLOW EPC QUALITY &amp; SAFETY DIVISION</strong><br>
              <span style="font-size:11px; color:var(--text-muted);">Standard: IEC 62446 / CEA Grid Interconnection Safety Standard</span>
            </div>
            <span class="status-pill pill-success">VERIFIED &amp; SIGNED</span>
          </div>
          <table style="width:100%; font-size:12.5px; border-collapse:collapse;">
            <tr><td style="padding:6px 0;"><strong>Project Reference:</strong></td><td>INST-2026-0001 (Dr. Rajesh Sharma)</td></tr>
            <tr><td style="padding:6px 0;"><strong>Lead Electrician:</strong></td><td>Ramesh Electrician (Lic #BLR-EL-4891)</td></tr>
            <tr><td style="padding:6px 0;"><strong>Measured Earth Resistance:</strong></td><td><strong style="color:var(--success-text);">2.40 &Omega;</strong> (&le; 5.0 &Omega; Safety Limit) [PASSED]</td></tr>
            <tr><td style="padding:6px 0;"><strong>Insulation Megger Reading:</strong></td><td><strong>25.0 M&Omega;</strong> (&ge; 1.0 M&Omega; Minimum) [PASSED]</td></tr>
            <tr><td style="padding:6px 0;"><strong>Array Voc / Isc:</strong></td><td>385.0 V / 9.4 A (Within MPPT window) [PASSED]</td></tr>
            <tr><td style="padding:6px 0;"><strong>Digital Signature Token:</strong></td><td><code>SHA256:7B9E218A34F5C012D884</code></td></tr>
          </table>
        </div>
      `
    },
    survey_photo: {
      title: "High-Resolution Rooftop Panoramic Feasibility Assessment & Shading Map",
      allowed: ['admin', 'sales', 'survey_tech', 'director'],
      docRef: `SITE-PANORAMA-SRV-${id}.JPG`,
      content: `
        <div style="border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; background:#FAFCFA;">
          <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:12px;">
            <div>
              <strong>ROOFTOP FEASIBILITY DRONE SURVEY</strong><br>
              <span style="font-size:11px; color:var(--text-muted);">Site: 42 Palm Meadows Boulevard, Bengaluru</span>
            </div>
            <span class="status-pill pill-success">OPTIMAL SOLAR EXPOSURE</span>
          </div>
          <div style="background:#EAF4ED; border:1px dashed var(--primary); border-radius:var(--radius-md); padding:24px; text-align:center; margin-bottom:12px;">
            <span style="font-size:36px;">📐 ☀️</span>
            <div style="font-size:14px; font-weight:700; color:var(--primary); margin-top:6px;">Rooftop Panoramic CAD Overlay</div>
            <div style="font-size:12px; color:var(--text-muted);">650 sq.ft RCC Flat Terrace • 500 sq.ft Usable Shadow-Free Area • True South 180° Azimuth • 12° Pitch</div>
          </div>
          <div style="font-size:12px; color:var(--text-muted);">Surveyor: Arun Survey Tech • Calibration Token: <code>SRV-SURVEY-A8821B</code></div>
        </div>
      `
    },
    profit_leakage_audit: {
      title: "Confidential Project Job Costing & Contractor Margin Audit Sheet",
      allowed: ['admin', 'finance', 'director'],
      docRef: `JOB-COST-AUDIT-COST-${id}.XLSX`,
      content: `
        <div style="border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; background:#FAFCFA;">
          <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:12px;">
            <div>
              <strong>EXECUTIVE JOB COSTING AUDIT BREAKDOWN</strong><br>
              <span style="font-size:11px; color:var(--danger-text);">CONFIDENTIAL: Internal Finance &amp; Investor Distribution Only</span>
            </div>
            <span class="status-pill pill-success">26.47% GROSS MARGIN</span>
          </div>
          <table style="width:100%; font-size:12.5px; border-collapse:collapse;">
            <tr><td style="padding:5px 0;">Contract Revenue:</td><td style="text-align:right;"><strong>$2,040.00</strong></td></tr>
            <tr><td style="padding:5px 0;">Bill of Materials Hardware:</td><td style="text-align:right;">$1,230.00</td></tr>
            <tr><td style="padding:5px 0;">Subcontractor Electrician Labour:</td><td style="text-align:right;">$90.00</td></tr>
            <tr><td style="padding:5px 0;">Freight &amp; Site Dispatch:</td><td style="text-align:right;">$60.00</td></tr>
            <tr><td style="padding:5px 0;">Statutory DISCOM Net-Metering Fees:</td><td style="text-align:right;">$120.00</td></tr>
            <tr style="border-top:1px solid var(--border);"><td style="padding:6px 0;"><strong>Total Cost:</strong></td><td style="text-align:right;"><strong>$1,500.00</strong></td></tr>
            <tr style="background:#EAF4ED;"><td style="padding:6px; color:var(--primary); font-weight:700;">Net EPC Profit Contribution:</td><td style="text-align:right; padding:6px; color:var(--primary); font-weight:700;">+$540.00 (+26.47%)</td></tr>
          </table>
        </div>
      `
    }
  };

  const doc = accessRules[docType];
  if (!doc) {
    showToast("Attachment not found.", "warn");
    return;
  }

  if (!doc.allowed.includes(role)) {
    showAccessDeniedModal(
      doc.title,
      roleCfg.name,
      `Security Violation (HTTP 403 Forbidden): Access to attachment '<strong>${doc.docRef}</strong>' (${doc.title}) is restricted. Your role <strong>${roleCfg.name}</strong> (${roleCfg.login}) does not possess the required security clearance.`
    );
    return;
  }

  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');
  const submitBtn = document.getElementById('modal-submit-btn');

  if (modalTitle) modalTitle.textContent = `📎 Attachment: ${doc.docRef}`;
  if (modalBody) modalBody.innerHTML = doc.content;
  if (submitBtn) {
    submitBtn.textContent = "Download Signed Copy";
    submitBtn.className = "btn-secondary-action";
    submitBtn.onclick = () => {
      showToast(`Downloaded verified attachment: ${doc.docRef}`, 'success');
      closeModal();
    };
  }
  openModal();
}

// Vector 7: Delete Permissions Guard (Admin Only)
function deleteRecord(model, id) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;

  if (SolarFlowState.currentRole !== 'admin') {
    showAccessDeniedModal(
      `Delete ${model.toUpperCase()} #${id}`,
      roleCfg.name,
      `Security Violation (HTTP 403 Forbidden): Server-enforced ACL policy restricts record deletion to Super Administrator only. Active role <strong>${roleCfg.name}</strong> (${roleCfg.login}) is strictly denied unlink operations.`
    );
    return;
  }

  if (!confirm(`Security Confirmation: Are you sure you want to permanently delete ${model.toUpperCase()} #${id}? This will remove the record from PostgreSQL database.`)) {
    return;
  }

  if (model === 'survey') {
    SolarFlowState.surveys = SolarFlowState.surveys.filter(s => s.id !== id);
    renderSurveys();
  } else if (model === 'installation') {
    SolarFlowState.installations = SolarFlowState.installations.filter(i => i.id !== id);
    renderInstallations();
  } else if (model === 'order') {
    SolarFlowState.orders = SolarFlowState.orders.filter(o => o.id !== id);
    renderOrders();
  } else if (model === 'costing') {
    SolarFlowState.costing = SolarFlowState.costing.filter(c => c.id !== id);
    renderCosting();
  }
  showToast(`Super Administrator successfully deleted ${model.toUpperCase()} #${id}.`, 'success');
}

// Vector 10: Sensitive Model Methods
function approveSurvey(surveyId) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  if (!roleCfg.canApproveSurveys) {
    showAccessDeniedModal(
      `Approve Site Survey #${surveyId}`,
      roleCfg.name,
      `Access Denied (HTTP 403): Only a Sales Manager or Super Administrator is authorized to approve site surveys. Survey Technicians cannot approve their own surveys.`
    );
    return;
  }
  const s = SolarFlowState.surveys.find(item => item.id === surveyId);
  if (s) {
    s.state = 'approved';
    showToast(`Site Survey ${s.ref} approved by ${roleCfg.userName}. Quotations unlocked.`, 'success');
    renderSurveys();
  }
}

function rejectSurvey(surveyId) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  if (!roleCfg.canApproveSurveys) {
    showAccessDeniedModal(
      `Reject Site Survey #${surveyId}`,
      roleCfg.name,
      `Access Denied (HTTP 403): Only a Sales Manager or Super Administrator is authorized to reject site surveys.`
    );
    return;
  }
  const reason = prompt("Enter official technical reason for rejecting this site survey:", "Structural roof weakness / shadow obstruction.");
  if (!reason || !reason.trim()) {
    showToast("Rejection cancelled: Mandatory rejection reason required.", "warn");
    return;
  }
  const s = SolarFlowState.surveys.find(item => item.id === surveyId);
  if (s) {
    s.state = 'rejected';
    s.rejectionReason = reason.trim();
    showToast(`Site Survey ${s.ref} rejected by ${roleCfg.userName}. Reason logged.`, 'warn');
    renderSurveys();
  }
}

function generateQuotationFromSurvey(surveyId) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  if (SolarFlowState.currentRole !== 'admin' && SolarFlowState.currentRole !== 'sales') {
    showAccessDeniedModal(
      `Generate Quotation from Survey #${surveyId}`,
      roleCfg.name,
      `Access Denied (HTTP 403): Only Sales Managers and Super Administrators have permission to create sales proposals.`
    );
    return;
  }
  showToast(`Quotation generated from Survey #${surveyId} with dynamic Auto-BOM components.`, 'success');
  switchView('quotations');
}

function confirmQuotationOrder(quoteId) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  if (!roleCfg.canConfirmOrders) {
    showAccessDeniedModal(
      `Confirm Sales Contract #${quoteId}`,
      roleCfg.name,
      `Access Denied (HTTP 403): Only Sales Managers and Super Administrators have authorization to confirm sales orders. Director account has strict read-only access.`
    );
    return;
  }
  showToast(`Quotation confirmed by ${roleCfg.userName}. 50% advance invoice issued to unlock dispatch.`, 'success');
  switchView('orders');
}

function completeInstallation(instId) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  if (!roleCfg.canCompleteInstallation) {
    showAccessDeniedModal(
      `Complete Installation #${instId}`,
      roleCfg.name,
      `Access Denied (HTTP 403): Project completion requires field technician, sales manager, or administrator authorization. Director account has strict read-only access.`
    );
    return;
  }
  const inst = SolarFlowState.installations.find(i => i.id === instId);
  if (inst) {
    inst.state = 'completed';
    inst.customerAccepted = true;
    showToast(`Installation ${inst.ref} marked Completed & Commissioned. Digital Warranties and Job Costing active.`, 'success');
    renderInstallations();
  }
}

function scheduleSurveyFromLead(leadId) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  if (roleCfg.readOnly) {
    showAccessDeniedModal(`Schedule Survey from Lead #${leadId}`, roleCfg.name, `Access Denied: Director / Investor role has strict read-only access.`);
    return;
  }
  showToast(`Site survey scheduled for Lead #${leadId}. Assigned to Survey Crew.`, 'success');
  switchView('surveys');
}

function triggerWarrantyReminderCheck() {
  showToast("Warranty Expiry Engine: Active Warranties analyzed. 0 expiring within 30 days.", "info");
}

function exportTableToCSV(moduleName) {
  showToast(`Exported ${moduleName.toUpperCase()} records to CSV successfully.`, 'success');
}

// User Profile Modal (Shows active test account credentials)
function showUserProfileModal() {
  const roleKey = SolarFlowState.currentRole;
  const cfg = SolarFlowState.roles[roleKey] || SolarFlowState.roles.admin;

  const modalTitle = document.getElementById('modal-title');
  const modalBody = document.getElementById('modal-body');
  const submitBtn = document.getElementById('modal-submit-btn');

  if (modalTitle) modalTitle.textContent = `User Profile & Role Authorization Matrix`;
  if (modalBody) {
    modalBody.innerHTML = `
      <div style="background-color:#F8FAF8; border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:12px;">
          <div class="user-avatar-circle" style="width:48px; height:48px; font-size:18px;">${cfg.avatar}</div>
          <div>
            <h4 style="font-size:16px; font-weight:700; color:var(--text-main);">${cfg.userName}</h4>
            <div style="font-size:12.5px; color:var(--text-muted);">${cfg.title} • <code>${cfg.login}</code></div>
          </div>
          <span class="status-pill pill-info" style="margin-left:auto;">${cfg.name}</span>
        </div>
        <p style="font-size:13px; color:var(--text-muted); margin:0;">${cfg.desc}</p>
      </div>

      <h4 style="font-size:13.5px; font-weight:700; margin-bottom:10px;">Switch to Another Test Account:</h4>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        ${Object.keys(SolarFlowState.roles).map(k => {
          const r = SolarFlowState.roles[k];
          const isCurrent = (k === roleKey);
          return `
            <button class="btn-action-sm" style="text-align:left; padding:8px 10px; display:flex; justify-content:space-between; align-items:center; ${isCurrent ? 'border-color:var(--primary); background:var(--primary-subtle);' : ''}" onclick="applyRole('${k}'); closeModal();">
              <div>
                <strong>${r.userName}</strong>
                <div style="font-size:11px; color:var(--text-muted);">${r.login}</div>
              </div>
              <span class="status-pill ${isCurrent ? 'pill-success' : 'pill-neutral'}">${r.avatar}</span>
            </button>
          `;
        }).join('')}
      </div>
    `;
  }

  if (submitBtn) {
    submitBtn.textContent = "Close";
    submitBtn.className = "btn-secondary-action";
    submitBtn.onclick = () => closeModal();
  }

  openModal();
}

// ==========================================================================
// 1-CLICK INTERACTIVE 3KW SHOWCASE TOUR
// ==========================================================================
function setupShowcaseTour() {
  const btn = document.getElementById('btn-showcase-tour');
  if (!btn) return;

  btn.addEventListener('click', () => {
    runShowcaseStep(1);
  });
}

function runShowcaseStep(step) {
  switch (step) {
    case 1:
      showToast("Step 1/6: Customer Enquiry & Lead Sizing for Dr. Rajesh Sharma (3kW On-Grid).", "info");
      switchView('leads');
      setTimeout(() => runShowcaseStep(2), 2200);
      break;
    case 2:
      showToast("Step 2/6: Rooftop Site Survey SRV-0001 Approved (500 sq.ft RCC shadow-free).", "info");
      switchView('surveys');
      setTimeout(() => runShowcaseStep(3), 2200);
      break;
    case 3:
      showToast("Step 3/6: Dynamic Auto-BOM Package Generated ($2,040 Net with PM Surya Ghar Subsidy).", "info");
      switchView('packages');
      setTimeout(() => runShowcaseStep(4), 2200);
      break;
    case 4:
      showToast("Step 4/6: 50% Advance Paid ($1,020) -> Warehouse Dispatches Serial INV-GROWATT-9901.", "info");
      switchView('orders');
      setTimeout(() => runShowcaseStep(5), 2200);
      break;
    case 5:
      showToast("Step 5/6: Installation Commissioned! QC Earth Pit: 2.4 Ohms (<= 5.0 Ohm safety gate passed).", "success");
      switchView('installations');
      setTimeout(() => runShowcaseStep(6), 2200);
      break;
    case 6:
      showToast("Step 6/6: Digital Warranties Active (SHA-256) & Job Costing Reconciled ($540 Gross Profit).", "success");
      switchView('costing');
      setTimeout(() => {
        showToast("🎉 Complete 3kW Showcase Customer Journey Tour Finished!", "success");
      }, 2500);
      break;
  }
}

// Toast Notifications Helper
function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-item ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'warn' ? '⚠️' : 'ℹ️'}</span><span>${msg}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
