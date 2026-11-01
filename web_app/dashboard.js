const role = new URLSearchParams(location.search).get('role') || document.body.dataset.role || 'customer';
const definitions = {
  customer: {name:'Customer', user:'Customer', cards:['Purchased products','Current orders','Warranty cards','Service history'], actions:['Raise complaint','Track complaint','Download quotation','Update profile']},
  warehouse: {name:'Warehouse Manager', user:'Sanjay Warehouse Manager', cards:['Total products','Available stock','Reserved stock','Low-stock alerts'], actions:['Check serial numbers','Assign delivery task','Create customer']},
  sales: {name:'Sales Team', user:'Vikram Sales Manager', cards:['New customers','Approved quotations','Confirmed orders','Completed deliveries'], actions:['Create customer','Assign delivery verification','View warehouse tasks']},
  technician: {name:'Technician', user:'Arun Survey Tech', cards:['Today’s tasks','Pending installations','Survey reports','Completed installations'], actions:['Navigate to site','Submit QC checklist','Customer verification']},
  support: {name:'Support Team', user:'Support Manager', cards:['New support tasks','Warranty issuance','Active warranties','Service tickets'], actions:['Issue warranty','Record acknowledgement','Create customer']},
  admin: {name:'Super Admin', user:'System Administrator', cards:['Customers','Active orders','Completed installations','Pending installations'], actions:['Manage employees','Manage catalogue','Configure policies','View audit logs']},
  finance: {name:'Finance Team', user:'Finance Manager', cards:['Invoices','Payments','Expenses','Project costing'], actions:['Approve payment','Review expenses','Export financial report','View costing']},
  director: {name:'Director', user:'Director', cards:['Portfolio revenue','Active projects','Margin overview','Risk summary'], actions:['View executive reports','Review project performance']}
};
const info = definitions[role];
async function loadDashboard() {
  const response = await fetch(`/api/dashboard/${role}`, { credentials: 'same-origin' });
  if (response.status === 401) {
    window.location.replace('/');
    return;
  }
  if (!response.ok) {
    document.getElementById('app').innerHTML = '<main class="dash-main"><h1>Access unavailable</h1><p>Please sign in again with an authorized account.</p><a href="/">Return to sign in</a></main>';
    return;
  }
  const data = await response.json();
  let customerName = 'Customer';
  let business = null;
  if (role === 'customer') {
    const meResponse = await fetch('/api/auth/me', { credentials: 'same-origin' });
    if (meResponse.ok) {
      const me = await meResponse.json();
      customerName = me.user.name || 'Customer';
      business = me.user.business;
    }
  }
  const unread = data.notifications.length;
  const customerExtras = role === 'customer' ? customerExperience() : '';
  document.getElementById('app').innerHTML = `
    <aside class="dash-sidebar"><div class="dash-brand"><span>☀</span> SunPower Nexus</div>
      <a class="dash-side-link active" href="${role}.html">⌂ &nbsp; Dashboard</a><a class="dash-side-link" href="quotation.html">▤ &nbsp; Quotations</a><a class="dash-side-link" href="survey.html">⌖ &nbsp; Site Surveys</a>
      <nav class="mobile-nav"><a href="${role}.html">⌂</a><a href="quotation.html">▤</a><a href="survey.html">⌖</a></nav>
    </aside>
    <main class="dash-main"><header class="dash-top"><div><p class="eyebrow">${info.name}</p><h1>Namaste, ${role === 'customer' ? customerName : info.user}</h1></div><div class="dash-actions"><button class="icon-button" title="Notifications" data-dashboard-action="notifications">🔔${unread ? `<span class="badge">${unread}</span>` : ''}</button><button class="icon-button" title="Profile" data-dashboard-action="profile">👤</button><button class="sign-out-button" type="button" data-dashboard-action="logout"><span aria-hidden="true">↪</span> Sign out</button></div></header>
    ${business ? `<section class="panel"><strong>${business.organization_name}</strong><p>B2B email: ${business.email_verified ? 'Verified' : 'Pending verification'} · Approval: ${business.approval_status} · Discount: ${Number(business.discount_percent || 0)}%</p></section>` : ''}
    ${role === 'customer' ? `<section class="customer-hero"><div><p class="eyebrow" style="color:#9fcdb1">YOUR SOLAR JOURNEY</p><h2>Your home is generating smarter energy.</h2><p>Installation 72% complete · Estimated commissioning in 8 days</p></div><div class="solar-score" aria-label="Project completion 84 percent"><span>84%</span></div></section>` : ''}
    <section class="metrics">${info.cards.map((card,i)=>`<div class="metric">${card}<strong>${[data.metrics.products,data.metrics.orders,data.metrics.surveys,data.metrics.warranties][i] ?? '—'}</strong><span>${i === 0 ? 'Current portfolio' : 'Updated now'}</span></div>`).join('')}</section>
    ${customerExtras}
    <section class="panel-grid"><div class="panel"><h2>Current work</h2>${data.orders.length ? data.orders.map(order=>`<div class="list-row"><span>${order.customer_name}<small><br>${order.status}</small></span><span class="status">${order.id.slice(0,8)}</span></div>`).join('') : '<p>No orders are currently assigned.</p>'}</div>
    <div class="panel"><h2>Notifications</h2>${data.notifications.length ? data.notifications.map(n=>`<div class="list-row"><span>${n.title}<small><br>${n.message}</small></span><button class="task-button">Open</button></div>`).join('') : '<p>No unread notifications.</p>'}</div></section>
    <section class="panel"><h2>Actions</h2><div class="dash-actions">${info.actions.map(action=>`<button class="task-button" data-action="${action}">${action}</button>`).join('')}</div></section></main>`;
  bindDashboardActions();
}

function customerExperience() {
  return `
    <section class="panel">
      <div class="dash-top"><div><p class="eyebrow">PROJECT PROGRESS</p><h2>Order SFL-2026-0048</h2></div><span class="status">Installation underway</span></div>
      <div class="order-timeline" aria-label="Solar installation order progress">
        <div class="timeline-step done"><i></i><strong>Consulted</strong></div>
        <div class="timeline-step done"><i></i><strong>Survey approved</strong></div>
        <div class="timeline-step current"><i></i><strong>Installation</strong></div>
        <div class="timeline-step"><i></i><strong>Energized</strong></div>
      </div>
    </section>
    <section class="panel">
      <div class="dash-top"><div><p class="eyebrow">RECOMMENDED SYSTEMS</p><h2>Designed for your roof</h2></div><button class="task-button secondary" data-action="Compare products">Compare products</button></div>
      <div class="product-grid">
        ${[
          ['Essential 3 kW','Ideal for compact homes','₹2.04L','Residential · 3 kW'],
          ['Performance 5 kW','Best value for growing families','₹3.25L','Hybrid · 5 kW'],
          ['Premium 7 kW','Maximum solar independence','₹4.68L','High-output · 7 kW']
        ].map(product => `<article class="product-card"><div class="product-visual" role="img" aria-label="${product[0]} solar product"><div class="mini-panel"><i></i><i></i><i></i><i></i><i></i><i></i></div></div><div class="product-info"><strong>${product[0]}</strong><small>${product[1]} · ${product[3]}</small><div class="product-price">${product[2]}</div><button class="task-button" style="margin-top:12px;width:100%" data-action="View ${product[0]}">View system</button></div></article>`).join('')}
      </div>
    </section>`;
}

function bindDashboardActions() {
  document.querySelectorAll('[data-dashboard-action]').forEach(button => button.addEventListener('click', () => {
    const action = button.dataset.dashboardAction;
    if (action === 'logout') {
      button.disabled = true;
      button.textContent = 'Signing out...';
      sessionStorage.clear();
      window.location.assign('/api/auth/logout');
    }
    if (action === 'profile') alert('Profile settings are available from your secure customer workspace.');
    if (action === 'notifications') {
      document.querySelector('.panel-grid')?.scrollIntoView({behavior:'smooth'});
      button.querySelector('.badge')?.remove();
    }
  }));
  document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => {
    button.textContent = 'Opening…';
    setTimeout(() => {
      button.textContent = button.dataset.action;
      window.location.href = 'quotation.html';
    }, 350);
  }));
}
loadDashboard().catch(error => document.getElementById('app').textContent = error.message);
