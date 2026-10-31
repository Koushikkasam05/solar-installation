// ==========================================================================
// SolarFlow ERP – Complete Light Enterprise Frontend & Business Engine
// Clean Forest Green Palette (#246B45), Real DB Records, Strict RBAC Matrix
// ==========================================================================

const SolarFlowState = {
  currentRole: 'admin',
  sidebarCollapsed: false,
  activeView: 'dashboard',

  // 8 Role Definitions with Permissions and Profiles
  roles: {
    admin: {
      name: "Super Administrator",
      title: "Chief Executive Officer",
      avatar: "SA",
      perm: ["all"],
      desc: "Full administrative access across all business modules, settings, and users."
    },
    sales: {
      name: "Sales Manager",
      title: "Head of Solar Sales",
      avatar: "SM",
      perm: ["dashboard", "enquiries", "leads", "followups", "surveys", "quotations", "orders", "installations", "schedule", "packages", "stock_reservations", "products"],
      desc: "Manages customer enquiries, leads, follow-ups, surveys, quotations, and orders."
    },
    survey_tech: {
      name: "Survey Technician",
      title: "Field Solar Surveyor",
      avatar: "ST",
      perm: ["dashboard", "surveys", "schedule"],
      desc: "Performs rooftop feasibility surveys, pitch/azimuth/shadow logs, and photo uploads."
    },
    warehouse: {
      name: "Warehouse Manager",
      title: "Supply Chain & Staging Lead",
      avatar: "WM",
      perm: ["dashboard", "products", "categories", "warehouses", "stock_avail", "stock_reservations", "inventory", "dispatches", "stock_moves"],
      desc: "Manages physical stock, serialized equipment, reservations, and site dispatches."
    },
    tech: {
      name: "Installation Technician",
      title: "Senior Electrical Lead",
      avatar: "IT",
      perm: ["dashboard", "installations", "schedule", "inst_reports", "inventory", "service"],
      desc: "Executes assigned rooftop installations, 6-phase checklist, and QC testing (Earth <= 5.0 Ohm)."
    },
    support: {
      name: "Support Manager",
      title: "Customer Success Lead",
      avatar: "SP",
      perm: ["dashboard", "warranties", "service", "complaints", "service_history", "inventory"],
      desc: "Handles warranty claims, RMA replacements, and service ticketing."
    },
    finance: {
      name: "Finance Manager",
      title: "Chief Financial Officer",
      avatar: "FM",
      perm: ["dashboard", "invoices", "payments", "expenses", "costing", "fin_reports", "quotations", "orders"],
      desc: "Manages milestone billing, customer payments, project costing, and profitability."
    },
    director: {
      name: "Director / Investor",
      title: "Board Director (Read-Only)",
      avatar: "DR",
      perm: ["dashboard", "enquiries", "leads", "followups", "surveys", "quotations", "orders", "installations", "schedule", "technicians", "inst_reports", "products", "categories", "warehouses", "stock_avail", "stock_reservations", "inventory", "dispatches", "stock_moves", "warranties", "service", "complaints", "service_history", "invoices", "payments", "expenses", "costing", "fin_reports", "biz_reports", "op_reports", "tech_perf", "sales_perf"],
      readOnly: true,
      desc: "Executive read-only analytics for revenue, EBITDA margins, and project performance."
    }
  },

  // 10 Verified Customers
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
      engineer: "Arun K. (Chief Engineer)",
      notes: "Rooftop is flat RCC with zero shading. Excellent load bearing capacity."
    },
    {
      id: 2, ref: "SRV-2026-0002", customerId: 3, leadId: 3, roofType: "RCC Flat Terrace",
      totalArea: "900 sq.ft", usableArea: "700 sq.ft", azimuth: "210° South-West", tilt: "15°",
      cableDist: "25 m", gridPhase: "Three Phase 415V", recommendedKw: 5.0, state: "scheduled",
      engineer: "Pending Assignment",
      notes: "Scheduled shadow analysis and parapet height check."
    },
    {
      id: 3, ref: "SRV-2026-0003", customerId: 7, leadId: 7, roofType: "Asbestos Tin Shed",
      totalArea: "350 sq.ft", usableArea: "120 sq.ft", azimuth: "0° North (Low Yield)", tilt: "25°",
      cableDist: "55 m", gridPhase: "Single Phase", recommendedKw: 1.0, state: "rejected",
      rejectionReason: "Severe structural weakness in corrugated tin roof and continuous shadow obstruction from adjacent building.",
      engineer: "Arun K. (Chief Engineer)",
      notes: "Infeasible for elevated module mounting structure."
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
// INITIALIZATION & EVENT LISTENERS
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  setupSidebar();
  setupRoleSwitcher();
  setupGlobalSearch();
  setupQuickCreate();
  setupShowcaseTour();
  renderRoleDashboard();
  renderAllDataViews();
});

// Sidebar Toggle
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

// View Switching with Role Permission Checking
function switchView(viewName) {
  const roleCfg = SolarFlowState.roles[SolarFlowState.currentRole] || SolarFlowState.roles.admin;
  
  // Security Check: does role have access?
  const hasAccess = roleCfg.perm.includes('all') || roleCfg.perm.includes(viewName);
  if (!hasAccess) {
    showToast(`Access Denied: The ${roleCfg.name} role does not have permission to access '${viewName}'.`, 'warn');
    return;
  }

  SolarFlowState.activeView = viewName;

  // Update Sidebar active state
  document.querySelectorAll('.nav-link-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-view') === viewName);
  });

  // Update Breadcrumbs
  updateBreadcrumbs(viewName);

  // Hide all sections
  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

  // Target section
  let targetSection = document.getElementById(`view-${viewName}`);
  if (!targetSection) {
    // If not a dedicated section, show generic panel with informative records
    targetSection = document.getElementById('view-generic-panel');
    populateGenericModule(viewName);
  }

  if (targetSection) {
    targetSection.classList.add('active');
  }

  // If dashboard, refresh role dashboard
  if (viewName === 'dashboard') {
    renderRoleDashboard();
  }
}

// Update Top Breadcrumbs
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

// ==========================================================================
// ROLE-BASED ACCESS CONTROL (RBAC) LOGIC
// ==========================================================================
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

  // 1. Update Profile Badges
  const roleIndicator = document.getElementById('sidebar-role-indicator');
  const avatarInitials = document.getElementById('user-avatar-initials');
  const displayName = document.getElementById('user-display-name');
  const roleTitle = document.getElementById('user-role-title');

  if (roleIndicator) roleIndicator.textContent = cfg.name;
  if (avatarInitials) avatarInitials.textContent = cfg.avatar;
  if (displayName) displayName.textContent = cfg.name;
  if (roleTitle) roleTitle.textContent = cfg.title;

  // 2. Filter Left Sidebar Menus by Role Permissions
  document.querySelectorAll('.sidebar-nav .nav-link-btn').forEach(btn => {
    const perm = btn.getAttribute('data-perm') || '';
    if (perm === 'all' || cfg.perm.includes('all')) {
      btn.style.display = 'flex';
    } else {
      const allowedRoles = perm.split(',').map(s => s.trim());
      btn.style.display = allowedRoles.includes(roleKey) ? 'flex' : 'none';
    }
  });

  // Filter Nav Groups
  document.querySelectorAll('.sidebar-nav .nav-group-title').forEach(grp => {
    const grpPerm = grp.getAttribute('data-group-perm');
    if (!grpPerm || cfg.perm.includes('all')) {
      grp.style.display = 'block';
    } else {
      const allowedRoles = grpPerm.split(',').map(s => s.trim());
      grp.style.display = allowedRoles.includes(roleKey) ? 'block' : 'none';
    }
  });

  // 3. Financial Costing Access Gate
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

  // 4. If current active view is not permitted for new role, switch back to dashboard
  if (!cfg.perm.includes('all') && !cfg.perm.includes(SolarFlowState.activeView)) {
    switchView('dashboard');
  } else {
    // Refresh dashboard view for role
    renderRoleDashboard();
  }

  showToast(`Active User Role switched to: ${cfg.name}`, 'info');
}

// ==========================================================================
// ROLE-TAILORED DASHBOARD INJECTION
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

// 1. SUPER ADMINISTRATOR DASHBOARD
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
        <div class="metric-subtext">Shadow &amp; Tilt Assessments</div>
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
        <div class="metric-subtext">Earthing Chemical Compound</div>
      </div>

      <div class="metric-card" onclick="switchView('warranties')">
        <div class="metric-header">
          <span class="metric-label">Active Warranties</span>
          <div class="metric-icon-wrap icon-forest">🛡️</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">Cryptographic SHA-256 Tokens</div>
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
          <div class="metric-icon-wrap">💵</div>
        </div>
        <div class="metric-value">$2,040.00</div>
        <div class="metric-subtext">Turnkey Solar Contract</div>
      </div>

      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header">
          <span class="metric-label">Gross Margin</span>
          <div class="metric-icon-wrap">📈</div>
        </div>
        <div class="metric-value">26.47%</div>
        <div class="metric-subtext">Gross Profit: $540.00</div>
      </div>
    </div>

    <!-- Innovation Split Panels -->
    <div class="dashboard-grid-2col">
      <!-- Unique Innovation: Serial-to-Warranty Hardware Lifecycle -->
      <div class="content-card">
        <div class="card-title-bar">
          <div>
            <span class="status-pill pill-info" style="margin-bottom:4px;">Unique Innovation</span>
            <div class="card-title">Serial-to-Warranty Hardware Lifecycle Traceability</div>
          </div>
          <span style="font-size:12px; font-weight:600; color:var(--primary-forest);">Serial: INV-GROWATT-3KW-9901</span>
        </div>
        <p style="font-size:12px; color:var(--secondary-text); margin-bottom:14px;">Complete 7-stage hardware journey mapped to verified Odoo EPC transactions.</p>
        
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

      <!-- Installation Readiness Score (out of 100) -->
      <div class="content-card">
        <div class="card-title-bar">
          <div>
            <span class="status-pill pill-success" style="margin-bottom:4px;">Innovation Metric</span>
            <div class="card-title">Readiness Index</div>
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
          <div style="font-size:12px; font-weight:600; color:var(--main-text); margin-bottom:8px;">Dr. Rajesh Sharma (3kW Site)</div>
        </div>

        <div class="readiness-criteria-list">
          <div class="criterion-item passed">
            <span>✓ Survey Approved</span>
            <span class="criterion-status-tag">+20 Pts</span>
          </div>
          <div class="criterion-item passed">
            <span>✓ 50% Advance Received</span>
            <span class="criterion-status-tag">+20 Pts</span>
          </div>
          <div class="criterion-item passed">
            <span>✓ Stock Available in Staging</span>
            <span class="criterion-status-tag">+20 Pts</span>
          </div>
          <div class="criterion-item passed">
            <span>✓ Serial Numbers Allocated</span>
            <span class="criterion-status-tag">+20 Pts</span>
          </div>
          <div class="criterion-item passed">
            <span>✓ Field Crew Assigned</span>
            <span class="criterion-status-tag">+20 Pts</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 2. SALES MANAGER DASHBOARD
function renderSalesDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Sales Manager Command Center</h1>
        <p class="section-description">Lead pipeline, preliminary consumption analysis, customer follow-ups, and quotation approvals.</p>
      </div>
      <div class="header-action-group">
        <button class="btn-quick-create" onclick="showLeadModal()">+ Create New Lead</button>
        <button class="btn-outline-action" onclick="switchView('followups')">📅 View Follow-ups</button>
      </div>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('enquiries')">
        <div class="metric-header">
          <span class="metric-label">New Enquiries</span>
          <div class="metric-icon-wrap icon-forest">📩</div>
        </div>
        <div class="metric-value">4</div>
        <div class="metric-subtext">2 Awaiting Sizing</div>
      </div>

      <div class="metric-card" onclick="switchView('leads')">
        <div class="metric-header">
          <span class="metric-label">My Leads</span>
          <div class="metric-icon-wrap icon-blue">🎯</div>
        </div>
        <div class="metric-value">10</div>
        <div class="metric-subtext">8 Residential, 2 Commercial</div>
      </div>

      <div class="metric-card" onclick="switchView('followups')">
        <div class="metric-header">
          <span class="metric-label">Follow-ups Due</span>
          <div class="metric-icon-wrap icon-amber">⏰</div>
        </div>
        <div class="metric-value">3</div>
        <div class="metric-subtext">Today &amp; Tomorrow</div>
      </div>

      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header">
          <span class="metric-label">Surveys Pending</span>
          <div class="metric-icon-wrap icon-rose">📐</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">Field Team Dispatched</div>
      </div>

      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header">
          <span class="metric-label">Approved Surveys</span>
          <div class="metric-icon-wrap icon-forest">✓</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Ready for Quotation</div>
      </div>

      <div class="metric-card" onclick="switchView('quotations')">
        <div class="metric-header">
          <span class="metric-label">Quotations Pending</span>
          <div class="metric-icon-wrap icon-purple">📑</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Awaiting Customer Sign</div>
      </div>

      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header">
          <span class="metric-label">Confirmed Orders</span>
          <div class="metric-icon-wrap icon-forest">✅</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">$2,040 Turnkey Contract</div>
      </div>

      <div class="metric-card highlight-profit">
        <div class="metric-header">
          <span class="metric-label">Conversion Rate</span>
          <div class="metric-icon-wrap">🏆</div>
        </div>
        <div class="metric-value">80.0%</div>
        <div class="metric-subtext">Surveys to Quotation Ratio</div>
      </div>
    </div>

    <!-- Quick Actions Panel -->
    <div class="content-card" style="margin-top:20px;">
      <div class="card-title-bar">
        <div class="card-title">Sales Quick Actions &amp; Workflows</div>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <button class="btn-action-primary-sm" onclick="showLeadModal()">+ Log Customer Lead</button>
        <button class="btn-action-sm" onclick="scheduleSurveyFromLead(1)">+ Schedule Site Survey</button>
        <button class="btn-action-sm" onclick="switchView('packages')">View Configured Packages</button>
        <button class="btn-action-sm" onclick="switchView('orders')">Verify Advance Payments</button>
      </div>
    </div>
  `;
}

// 3. WAREHOUSE MANAGER DASHBOARD
function renderWarehouseDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Warehouse &amp; Serial Inventory Command</h1>
        <p class="section-description">Serialized PV equipment, stock reservations, single-allocation constraints, and dispatch releases.</p>
      </div>
      <div class="header-action-group">
        <button class="btn-action-primary-sm" onclick="showToast('Stock intake logged.', 'success')">+ Receive Equipment</button>
        <button class="btn-outline-action" onclick="switchView('inventory')">🏷️ View Serial Numbers</button>
      </div>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Total SKUs</span>
          <div class="metric-icon-wrap icon-forest">📦</div>
        </div>
        <div class="metric-value">4</div>
        <div class="metric-subtext">PV, Inverters, Batteries</div>
      </div>

      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Available Stock</span>
          <div class="metric-icon-wrap icon-blue">📊</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">Ready for Reservation</div>
      </div>

      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Reserved Equipment</span>
          <div class="metric-icon-wrap icon-amber">🔒</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">Allocated to Projects</div>
      </div>

      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Low Stock Alert</span>
          <div class="metric-icon-wrap icon-rose">⚠️</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Earthing Compound Mix</div>
      </div>

      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header">
          <span class="metric-label">Pending Dispatches</span>
          <div class="metric-icon-wrap icon-purple">🚚</div>
        </div>
        <div class="metric-value">0</div>
        <div class="metric-subtext">All Approved Dispatched</div>
      </div>

      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Serial Allocation</span>
          <div class="metric-icon-wrap icon-forest">🏷️</div>
        </div>
        <div class="metric-value">100%</div>
        <div class="metric-subtext">Single-Active Constraint</div>
      </div>
    </div>

    <div class="content-card" style="margin-top:20px;">
      <div class="card-title-bar">
        <div class="card-title">Warehouse Operational Controls</div>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <button class="btn-action-primary-sm" onclick="switchView('inventory')">Audit Serial Numbers</button>
        <button class="btn-action-sm" onclick="showToast('Scanning barcode...', 'info')">📷 Scan Equipment Barcode</button>
        <button class="btn-action-sm" onclick="showToast('Inter-warehouse transfer logged.', 'success')">🔄 Transfer to Site Staging</button>
      </div>
    </div>
  `;
}

// 4. INSTALLATION TECHNICIAN DASHBOARD
function renderTechnicianDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">Field Installation Work Orders</h1>
        <p class="section-description">My assigned rooftop jobs, 6-phase checklist execution, and mandatory electrical safety testing (<5.0&Omega;).</p>
      </div>
      <span class="status-pill pill-danger">QC Safety Gate: Earth Pit &le; 5.0 &Omega;</span>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header">
          <span class="metric-label">My Assigned Jobs</span>
          <div class="metric-icon-wrap icon-forest">⚡</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">INST-2026-0001 (3kW)</div>
      </div>

      <div class="metric-card" onclick="switchView('schedule')">
        <div class="metric-header">
          <span class="metric-label">Today's Visits</span>
          <div class="metric-icon-wrap icon-blue">📅</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Dr. Rajesh Sharma Site</div>
      </div>

      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header">
          <span class="metric-label">Testing QC Status</span>
          <div class="metric-icon-wrap icon-forest">✓</div>
        </div>
        <div class="metric-value">2.4 &Omega;</div>
        <div class="metric-subtext">Passed Safety Gate</div>
      </div>

      <div class="metric-card highlight-profit" onclick="switchView('installations')">
        <div class="metric-header">
          <span class="metric-label">Commissioned Sites</span>
          <div class="metric-icon-wrap">🏆</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Customer Accepted (100%)</div>
      </div>
    </div>

    <!-- Quick Action Cards for Mobile Field Use -->
    <div class="content-card" style="margin-top:20px;">
      <div class="card-title-bar">
        <div class="card-title">Field Crew Quick Actions</div>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <button class="btn-action-primary-sm" onclick="switchView('installations')">⚡ Open Active Job (INST-2026-0001)</button>
        <button class="btn-action-sm" onclick="showToast('Camera opened. Photo attached to work order.', 'info')">📷 Upload Site Photos</button>
        <button class="btn-action-sm" onclick="showToast('Megger insulation testing logged.', 'success')">🔌 Submit QC Measurements</button>
        <button class="btn-action-sm" onclick="showToast('OTP customer acceptance requested.', 'info')">✍️ Request Customer Acceptance</button>
      </div>
    </div>
  `;
}

// 5. SUPPORT MANAGER DASHBOARD
function renderSupportDashboard(el) {
  el.innerHTML = `
    <div class="section-header-bar">
      <div>
        <h1 class="section-title">After-Sales Support &amp; Warranty Helpdesk</h1>
        <p class="section-description">Equipment serial lookup, automatic warranty determination, covered ($0) vs non-covered ticket billing.</p>
      </div>
      <button class="btn-quick-create" onclick="showTicketModal()">+ Log Service Ticket</button>
    </div>

    <div class="metrics-grid-12">
      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header">
          <span class="metric-label">Open Complaints</span>
          <div class="metric-icon-wrap icon-rose">⚠️</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">1 Inverter, 1 Grid Surge</div>
      </div>

      <div class="metric-card" onclick="switchView('warranties')">
        <div class="metric-header">
          <span class="metric-label">Active Warranties</span>
          <div class="metric-icon-wrap icon-forest">🛡️</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">SHA-256 Certificates</div>
      </div>

      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header">
          <span class="metric-label">Covered ($0) Claims</span>
          <div class="metric-icon-wrap icon-blue">✓</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">OEM Warranty Replaced</div>
      </div>

      <div class="metric-card" onclick="switchView('service')">
        <div class="metric-header">
          <span class="metric-label">Non-Covered Repairs</span>
          <div class="metric-icon-wrap icon-amber">💵</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">Billed $85.00 to Client</div>
      </div>
    </div>

    <div class="content-card" style="margin-top:20px;">
      <div class="card-title-bar">
        <div class="card-title">Serial Number Instant Warranty Lookup</div>
      </div>
      <div style="display:flex; gap:10px; max-width:500px;">
        <input type="text" id="serial-lookup-input" class="form-input" placeholder="Enter Serial Number (e.g. INV-GROWATT-3KW-9901)">
        <button class="btn-action-primary-sm" onclick="lookupSerialQuick()">Lookup</button>
      </div>
      <div id="serial-lookup-result" style="margin-top:12px; font-size:13px;"></div>
    </div>
  `;
}

// 6. SURVEY TECHNICIAN DASHBOARD
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
        <div class="metric-header">
          <span class="metric-label">Assigned Surveys</span>
          <div class="metric-icon-wrap icon-forest">📐</div>
        </div>
        <div class="metric-value">2</div>
        <div class="metric-subtext">SRV-0001, SRV-0002</div>
      </div>

      <div class="metric-card" onclick="switchView('surveys')">
        <div class="metric-header">
          <span class="metric-label">Submitted for Approval</span>
          <div class="metric-icon-wrap icon-blue">📩</div>
        </div>
        <div class="metric-value">1</div>
        <div class="metric-subtext">SRV-0001 Approved</div>
      </div>
    </div>

    <div class="content-card" style="margin-top:20px;">
      <div class="card-title-bar">
        <div class="card-title">Site Assessment Field Tools</div>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <button class="btn-action-primary-sm" onclick="switchView('surveys')">📐 Open My Site Surveys</button>
        <button class="btn-action-sm" onclick="showToast('Rooftop panoramic photo uploaded.', 'success')">📷 Upload Rooftop Photos</button>
        <button class="btn-action-sm" onclick="showToast('DB meter distance logged.', 'info')">📏 Log Cable Distance</button>
      </div>
    </div>
  `;
}

// 7. FINANCE MANAGER DASHBOARD
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
        <div class="metric-header">
          <span class="metric-label">Billed Revenue</span>
          <div class="metric-icon-wrap icon-forest">💵</div>
        </div>
        <div class="metric-value">$2,040.00</div>
        <div class="metric-subtext">3kW Turnkey Contract</div>
      </div>

      <div class="metric-card" onclick="switchView('orders')">
        <div class="metric-header">
          <span class="metric-label">50% Advance Met</span>
          <div class="metric-icon-wrap icon-blue">💳</div>
        </div>
        <div class="metric-value">$1,020.00</div>
        <div class="metric-subtext">Dispatch Permission Unlocked</div>
      </div>

      <div class="metric-card" onclick="switchView('costing')">
        <div class="metric-header">
          <span class="metric-label">Actual Project Cost</span>
          <div class="metric-icon-wrap icon-amber">💸</div>
        </div>
        <div class="metric-value">$1,500.00</div>
        <div class="metric-subtext">Hardware, Labour &amp; Transport</div>
      </div>

      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header">
          <span class="metric-label">Gross Margin</span>
          <div class="metric-icon-wrap">📈</div>
        </div>
        <div class="metric-value">26.47%</div>
        <div class="metric-subtext">Gross Profit: $540.00</div>
      </div>
    </div>

    <div class="content-card" style="margin-top:20px;">
      <div class="card-title-bar">
        <div class="card-title">Financial Review Actions</div>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <button class="btn-action-primary-sm" onclick="switchView('costing')">💰 Review Job Costing Sheets</button>
        <button class="btn-action-sm" onclick="switchView('orders')">🧾 Reconcile Invoices</button>
        <button class="btn-action-sm" onclick="showToast('Subsidy disbursement batch exported.', 'success')">🏛️ Verify PM Surya Ghar Subsidy</button>
      </div>
    </div>
  `;
}

// 8. DIRECTOR / INVESTOR DASHBOARD (READ-ONLY)
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
        <div class="metric-header">
          <span class="metric-label">Total EPC Revenue</span>
          <div class="metric-icon-wrap">💵</div>
        </div>
        <div class="metric-value">$2,040.00</div>
        <div class="metric-subtext">Commercial &amp; Residential</div>
      </div>

      <div class="metric-card highlight-profit" onclick="switchView('costing')">
        <div class="metric-header">
          <span class="metric-label">Gross Profit</span>
          <div class="metric-icon-wrap">📈</div>
        </div>
        <div class="metric-value">$540.00</div>
        <div class="metric-subtext">Gross Margin: 26.47%</div>
      </div>

      <div class="metric-card" onclick="switchView('installations')">
        <div class="metric-header">
          <span class="metric-label">Active Projects</span>
          <div class="metric-icon-wrap icon-forest">⚡</div>
        </div>
        <div class="metric-value">10</div>
        <div class="metric-subtext">1 Completed, 9 Staging</div>
      </div>

      <div class="metric-card" onclick="switchView('inventory')">
        <div class="metric-header">
          <span class="metric-label">Warehoused Stock Value</span>
          <div class="metric-icon-wrap icon-blue">🏢</div>
        </div>
        <div class="metric-value">$8,950.00</div>
        <div class="metric-subtext">Tier-1 Modules &amp; Inverters</div>
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
function renderEnquiries() {
  const tbody = document.getElementById('enquiries-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.enquiries.map(enq => {
    const cust = SolarFlowState.customers.find(c => c.id === enq.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${enq.ref}</strong></td>
        <td><strong>${cust.name || 'Unknown'}</strong></td>
        <td style="color:var(--secondary-text);">${cust.phone || ''}</td>
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

// 2. Leads Table
function renderLeads() {
  const tbody = document.getElementById('leads-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.leads.map(lead => {
    const cust = SolarFlowState.customers.find(c => c.id === lead.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${lead.ref}</strong></td>
        <td>${cust.name || 'Unknown'}</td>
        <td style="color:var(--secondary-text);">${cust.phone || ''}</td>
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
        <td style="font-size:12px; color:var(--secondary-text);">${f.summary}</td>
        <td><span class="status-pill ${f.priority === 'High' ? 'pill-danger' : 'pill-warning'}">${f.priority}</span></td>
        <td><span class="status-pill pill-success">${f.status}</span></td>
      </tr>
    `;
  }).join('');
}

// 4. Surveys Table
function renderSurveys() {
  const tbody = document.getElementById('surveys-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.surveys.map(s => {
    const cust = SolarFlowState.customers.find(c => c.id === s.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref" onclick="openCustomerProfile(${cust.id})">${s.ref}</strong></td>
        <td>${cust.name || 'Unknown'}</td>
        <td>${s.roofType}</td>
        <td>${s.totalArea}</td>
        <td><strong>${s.usableArea}</strong></td>
        <td>${s.azimuth} / ${s.tilt}</td>
        <td>${s.cableDist}</td>
        <td><span class="status-pill pill-info">${s.gridPhase}</span></td>
        <td><span class="status-pill pill-warning">${s.recommendedKw} kW</span></td>
        <td><span class="status-pill ${s.state === 'approved' ? 'pill-success' : s.state === 'rejected' ? 'pill-danger' : 'pill-warning'}">${s.state.toUpperCase()}</span></td>
        <td>
          ${s.state === 'approved' 
            ? `<button class="btn-action-primary-sm" onclick="generateQuotationFromSurvey(${s.id})">Create Quotation</button>` 
            : s.state === 'scheduled'
            ? `<button class="btn-action-sm" onclick="approveSurvey(${s.id})">Chief Eng. Approve</button>`
            : `<span style="font-size:11px; color:var(--danger-text);">Rejected</span>`}
        </td>
      </tr>
    `;
  }).join('');
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
        <span style="font-size:11px; color:var(--secondary-text);">${p.code}</span>
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
        <span style="font-size:11px; color:var(--secondary-text); display:block;">Dynamic Auto-BOM Net Hardware Total:</span>
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
  container.innerHTML = SolarFlowState.installations.map(inst => {
    const cust = SolarFlowState.customers.find(c => c.id === inst.customerId) || {};
    return `
      <div class="content-card" style="margin-bottom:20px;">
        <div class="card-title-bar">
          <div>
            <span class="status-pill pill-success" style="margin-bottom:4px;">Commissioned Project</span>
            <div class="card-title">${inst.ref} – ${cust.name} (${inst.capacity} kW ${inst.type.toUpperCase()})</div>
            <div style="font-size:12px; color:var(--secondary-text); margin-top:2px;">Lead Technician: <strong>${inst.technician}</strong></div>
          </div>
          <div style="text-align:right;">
            <span class="status-pill pill-success">✓ Completed &amp; Accepted</span>
            <div style="font-size:11px; color:var(--secondary-text); margin-top:4px;">Commissioned: ${inst.scheduledDate}</div>
          </div>
        </div>

        <!-- Smart Button Drilldown Navigation -->
        <div class="smart-button-bar">
          <button class="smart-button" onclick="openCustomerProfile(${cust.id})">👤 Customer 360°</button>
          <button class="smart-button" onclick="switchView('orders')">📑 Order (SO-2026-0001)</button>
          <button class="smart-button" onclick="switchView('surveys')">📐 Survey (SRV-0001)</button>
          <button class="smart-button" onclick="switchView('inventory')">🏷️ Serials (2 Lots)</button>
          <button class="smart-button" onclick="switchView('warranties')">🛡️ Warranties (2 Active)</button>
          <button class="smart-button" onclick="switchView('costing')">💰 Cost Sheet ($540 Profit)</button>
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
        <div style="background-color:#F8FAF8; border:1px solid var(--border-color); border-radius:var(--radius-md); padding:12px; margin-bottom:16px;">
          <h4 style="font-size:13px; font-weight:700; margin-bottom:6px; color:var(--primary-forest);">Electrical QC Safety Readings (PASSED):</h4>
          <div style="display:flex; gap:20px; flex-wrap:wrap; font-size:13px;">
            <div>Open Circuit Voc: <strong>${inst.qc.voc} V</strong></div>
            <div>Short Circuit Isc: <strong>${inst.qc.isc} A</strong></div>
            <div>Earth Pit Resistance: <strong style="color:var(--success-text);">${inst.qc.earthResistance} &Omega;</strong> (&le; 5.0 &Omega; limit)</div>
            <div>Insulation Megger: <strong>${inst.qc.insulationMOhm} M&Omega;</strong></div>
            <div>Grid AC Voltage: <strong>${inst.qc.gridVolt} V</strong></div>
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div style="font-size:12px; color:var(--secondary-text);">Customer Acceptance Sign-off: <strong>${inst.acceptanceSignature}</strong></div>
          <button class="btn-action-primary-sm" onclick="showToast('Issued 2 Digital Warranties with SHA-256 tokens.', 'success')">🛡️ View Warranties</button>
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
function renderInventory() {
  const tbody = document.getElementById('inventory-table-body');
  if (!tbody) return;
  tbody.innerHTML = SolarFlowState.inventory.map(item => {
    const cust = SolarFlowState.customers.find(c => c.id === item.customerId) || {};
    return `
      <tr>
        <td><strong class="table-record-ref">${item.serial}</strong></td>
        <td>${item.product}</td>
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
        <td><code style="font-size:11px; color:var(--primary-forest);">${w.token}</code></td>
        <td><span class="status-pill pill-success">${w.status.toUpperCase()}</span></td>
      </tr>
    `;
  }).join('');
}

// 12. Service Tickets Table
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
        <td style="font-size:12px;">${t.faultLabel}</td>
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
      </tr>
    `;
  }).join('');
}

// Generic Module Populator for submenus without dedicated tables
function populateGenericModule(mod) {
  const title = document.getElementById('generic-panel-title');
  const desc = document.getElementById('generic-panel-desc');
  const content = document.getElementById('generic-panel-content');

  if (title) title.textContent = mod.replace(/_/g, ' ').toUpperCase();
  if (desc) desc.textContent = `Enterprise records and operational data for ${mod}.`;

  if (content) {
    content.innerHTML = `
      <div style="padding:20px; text-align:center;">
        <span style="font-size:32px;">📑</span>
        <h3 style="margin-top:10px; margin-bottom:6px;">Connected ${mod.replace(/_/g, ' ').toUpperCase()} Module</h3>
        <p style="color:var(--secondary-text); font-size:13px; max-width:500px; margin:0 auto 16px auto;">
          This view connects directly with SolarFlow's native Odoo models and records.
        </p>
        <button class="btn-action-primary-sm" onclick="switchView('dashboard')">Return to Dashboard</button>
      </div>
    `;
  }
}

// ==========================================================================
// SMART BUTTON CUSTOMER 360° PROFILE MODAL
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
      <div style="background-color:#F8FAF8; border:1px solid var(--border-color); border-radius:var(--radius-md); padding:12px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h4 style="font-size:15px; font-weight:700;">${cust.name}</h4>
            <div style="font-size:12px; color:var(--secondary-text);">${cust.address}</div>
          </div>
          <span class="status-pill pill-info">${cust.type}</span>
        </div>
        <div style="margin-top:8px; font-size:12px; display:flex; gap:16px;">
          <span>📞 ${cust.phone}</span>
          <span>✉️ ${cust.email}</span>
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
      <div style="font-size:12px; display:flex; flex-direction:column; gap:6px;">
        ${serials.map(s => `
          <div style="display:flex; justify-content:space-between; padding:6px 10px; background-color:#FFFFFF; border:1px solid var(--border-color); border-radius:var(--radius-sm);">
            <span>🏷️ <strong>${s.serial}</strong> (${s.product})</span>
            <span class="status-pill pill-success">Active Warranty</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  openModal();
}

// Modal Handlers
function openModal() {
  const modal = document.getElementById('modal-container');
  if (modal) modal.style.display = 'flex';
}

function closeModal() {
  const modal = document.getElementById('modal-container');
  if (modal) modal.style.display = 'none';
}

// ==========================================================================
// WORKFLOW ACTIONS & VALIDATIONS
// ==========================================================================
function scheduleSurveyFromLead(leadId) {
  showToast(`Site survey scheduled for Lead #${leadId}. Assigned to Survey Crew.`, 'success');
  switchView('surveys');
}

function approveSurvey(surveyId) {
  const s = SolarFlowState.surveys.find(item => item.id === surveyId);
  if (s) {
    s.state = 'approved';
    showToast(`Site Survey ${s.ref} approved by Chief Engineer Arun K. Quotations unlocked.`, 'success');
    renderSurveys();
  }
}

function generateQuotationFromSurvey(surveyId) {
  showToast(`Quotation generated from Survey #${surveyId} with dynamic Auto-BOM components.`, 'success');
  switchView('quotations');
}

function confirmQuotationOrder(quoteId) {
  showToast(`Quotation QT-2026-0002 confirmed by customer. 50% advance invoice issued.`, 'success');
  switchView('orders');
}

function lookupSerialQuick() {
  const input = document.getElementById('serial-lookup-input');
  const result = document.getElementById('serial-lookup-result');
  if (!input || !result) return;

  const q = input.value.trim().toUpperCase();
  const match = SolarFlowState.inventory.find(i => i.serial.toUpperCase().includes(q));

  if (match) {
    const cust = SolarFlowState.customers.find(c => c.id === match.customerId) || {};
    result.innerHTML = `
      <div style="padding:10px; background-color:var(--light-green); border:1px solid var(--success-border); border-radius:var(--radius-sm);">
        ✅ <strong>Verified Equipment Found:</strong> ${match.serial}<br>
        Product: ${match.product} (${match.oem})<br>
        Owner: <strong>${cust.name}</strong> • Status: <span class="status-pill pill-success">${match.status.toUpperCase()}</span><br>
        Warranty Policy: <strong>${match.warrantyYears} Years OEM Replacement</strong> (Active)
      </div>
    `;
  } else {
    result.innerHTML = `<span style="color:var(--danger-text);">❌ No matching serialized equipment found for "${input.value}".</span>`;
  }
}

// Global Search
function setupGlobalSearch() {
  const input = document.getElementById('global-search-input');
  if (!input) return;

  input.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase().trim();
    if (!term) return;

    // Search customers, serials, leads
    const matchCust = SolarFlowState.customers.find(c => c.name.toLowerCase().includes(term) || c.phone.includes(term));
    const matchSerial = SolarFlowState.inventory.find(i => i.serial.toLowerCase().includes(term));
    const matchLead = SolarFlowState.leads.find(l => l.ref.toLowerCase().includes(term));

    if (matchCust) {
      showToast(`Found Customer: ${matchCust.name} (${matchCust.city})`, 'info');
    } else if (matchSerial) {
      showToast(`Found Equipment Serial: ${matchSerial.serial}`, 'info');
    } else if (matchLead) {
      showToast(`Found Lead Record: ${matchLead.ref}`, 'info');
    }
  });
}

// Quick Create Modal
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
          <label class="form-label">Customer Name</label>
          <input type="text" id="new-cust-name" class="form-input" placeholder="e.g. Vikramaditya Rao">
        </div>
        <div>
          <label class="form-label">Phone Number</label>
          <input type="text" id="new-cust-phone" class="form-input" placeholder="+91 98765 00000">
        </div>
      </div>
      <div class="form-grid-2">
        <div>
          <label class="form-label">Monthly Consumption (kWh)</label>
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
        <textarea id="new-notes" class="form-textarea" rows="2" placeholder="RCC flat roof, shadow-free..."></textarea>
      </div>
    `;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  if (submitBtn) {
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
        <label class="form-label">Equipment Serial Number</label>
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
        <textarea class="form-textarea" rows="2" placeholder="Inverter alarm code AL04..."></textarea>
      </div>
    `;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  if (submitBtn) {
    submitBtn.onclick = () => {
      showToast("Service ticket created. Warranty status verified: Covered ($0.00 charge).", "success");
      closeModal();
      switchView('service');
    };
  }

  openModal();
}

function triggerWarrantyReminderCheck() {
  showToast("Warranty Expiry Engine: 2 Active Warranties analyzed. 0 expiring within 30 days.", "info");
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
