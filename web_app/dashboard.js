const role = document.body.dataset.role || new URLSearchParams(location.search).get('role') || 'customer';
const definitions = {
  customer: {name:'Customer', user:'Customer', cards:['Purchased products','Current orders','Warranty cards','Service history'], actions:['Raise complaint','Track complaint','Download quotation','Update profile']},
  warehouse: {name:'Warehouse Manager', user:'Sanjay Warehouse Manager', cards:['Total products','Available stock','Reserved stock','Low-stock alerts'], actions:['Check serial numbers','Assign delivery task','Create customer']},
  sales: {name:'Sales Team', user:'Vikram Sales Manager', cards:['New customers','Approved quotations','Confirmed orders','Completed deliveries'], actions:['Create customer','Assign delivery verification','View warehouse tasks']},
  technician: {name:'Technician', user:'Arun Survey Tech', cards:['Today’s tasks','Pending installations','Survey reports','Completed installations'], actions:['Navigate to site','Submit QC checklist','Customer verification']},
  support: {name:'Support Team', user:'Support Manager', cards:['New support tasks','Warranty issuance','Active warranties','Service tickets'], actions:['Issue warranty','Record acknowledgement','Create customer']},
  admin: {name:'Super Admin', user:'System Administrator', cards:['Customers','Active orders','Completed installations','Pending installations'], actions:['Manage employees','Manage catalogue','Configure policies','View audit logs']}
};
const info = definitions[role];
async function loadDashboard() {
  const data = await fetch(`/api/dashboard/${role}`).then(r => r.json());
  const unread = data.notifications.length;
  document.getElementById('app').innerHTML = `
    <aside class="dash-sidebar"><div class="dash-brand">☀ SolarFlow ERP</div>
      <a class="dash-side-link" href="${role}.html">Dashboard</a><a class="dash-side-link" href="quotation.html">Quotations</a><a class="dash-side-link" href="survey.html">Site Surveys</a>
      <nav class="mobile-nav"><a href="${role}.html">⌂</a><a href="quotation.html">▤</a><a href="survey.html">⌖</a></nav>
    </aside>
    <main class="dash-main"><header class="dash-top"><div><p class="eyebrow">${info.name}</p><h1>Namaste, ${info.user}</h1></div><div class="dash-actions"><button class="icon-button" title="Notifications">🔔${unread ? `<span class="badge">${unread}</span>` : ''}</button><button class="icon-button" title="Profile">👤</button><button class="icon-button" title="Logout">↪</button></div></header>
    <section class="metrics">${info.cards.map((card,i)=>`<div class="metric">${card}<strong>${[data.metrics.products,data.metrics.orders,data.metrics.surveys,data.metrics.warranties][i] ?? '—'}</strong></div>`).join('')}</section>
    <section class="panel-grid"><div class="panel"><h2>Current work</h2>${data.orders.length ? data.orders.map(order=>`<div class="list-row"><span>${order.customer_name}<small><br>${order.status}</small></span><span class="status">${order.id.slice(0,8)}</span></div>`).join('') : '<p>No orders are currently assigned.</p>'}</div>
    <div class="panel"><h2>Notifications</h2>${data.notifications.length ? data.notifications.map(n=>`<div class="list-row"><span>${n.title}<small><br>${n.message}</small></span><button class="task-button">Open</button></div>`).join('') : '<p>No unread notifications.</p>'}</div></section>
    <section class="panel"><h2>Actions</h2><div class="dash-actions">${info.actions.map(action=>`<button class="task-button" data-action="${action}">${action}</button>`).join('')}</div></section></main>`;
}
loadDashboard().catch(error => document.getElementById('app').textContent = error.message);
