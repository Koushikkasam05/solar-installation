const rupees = paise => new Intl.NumberFormat('en-IN', {style:'currency', currency:'INR'}).format(paise / 100);

async function request(path, options = {}) {
  const response = await fetch(path, {credentials:'same-origin', ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}

async function load() {
  try {
    const summary = await request('/api/payments/admin/summary');
    document.getElementById('payment-mode').textContent = `${summary.mode.toUpperCase()} MODE`;
    document.getElementById('payment-mode').classList.toggle('live', summary.mode === 'live');
    document.getElementById('finance-summary').innerHTML = `
      <div><small>Captured</small><strong>${rupees(summary.capturedPaise)}</strong></div>
      <div><small>Pending / authorized</small><strong>${rupees(summary.pendingPaise)}</strong></div>
      <div><small>Failed</small><strong>${rupees(summary.failedPaise)}</strong></div>
      <div><small>Refunded</small><strong>${rupees(summary.refundedPaise)}</strong></div>`;
    document.getElementById('transaction-list').innerHTML = summary.transactions.length ? `
      <table class="history-table"><thead><tr><th>Order / Payment</th><th>Milestone</th><th>Amount</th><th>Status</th><th>Action</th></tr></thead>
      <tbody>${summary.transactions.map(payment => `<tr>
        <td>${payment.razorpay_payment_id || payment.razorpay_order_id || payment.id}</td>
        <td>${payment.purpose}</td><td>${rupees(payment.amount_paise)}</td>
        <td><span class="status ${payment.status}">${payment.status}</span></td>
        <td>${payment.status === 'captured' ? `<button class="milestone" data-refund="${payment.id}">Refund</button>` : '—'}</td>
      </tr>`).join('')}</tbody></table>` : '<p>No transactions require reconciliation.</p>';
    document.querySelectorAll('[data-refund]').forEach(button => button.addEventListener('click', () => refundPayment(button.dataset.refund)));
  } catch (error) {
    document.getElementById('transaction-list').innerHTML = `<p class="error-message">${error.message}</p>`;
  }
}

async function refundPayment(transactionId) {
  const amount = prompt('Refund amount in INR (use a smaller amount for partial refund):');
  const reason = prompt('Reason for refund:');
  if (!amount || !reason) return;
  try {
    const response = await fetch(`/api/payments/${transactionId}/refund`, {
      method:'POST', credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-CSRF-Token':sessionStorage.getItem('nexus-csrf') || ''},
      body:JSON.stringify({amount:Number(amount), reason})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Refund failed');
    alert(`Refund submitted: ${data.razorpayRefundId}`);
    load();
  } catch (error) {
    alert(error.message);
  }
}

load();
