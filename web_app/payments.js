const money = paise => new Intl.NumberFormat('en-IN', {style:'currency', currency:'INR', maximumFractionDigits:0}).format(paise / 100);
const params = new URLSearchParams(location.search);
const quotationId = params.get('quotation');
let selectedPurpose = 'advance';
let paymentSummary;

function csrfHeaders(extra = {}) {
  return {'Content-Type':'application/json', 'X-CSRF-Token':sessionStorage.getItem('nexus-csrf') || '', ...extra};
}

async function api(path, options = {}) {
  const response = await fetch(path, {credentials:'same-origin', ...options});
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed');
  return body;
}

async function load() {
  if (!quotationId) {
    document.getElementById('payment-message').textContent = 'Select an approved quotation from your dashboard to continue.';
    document.getElementById('pay-now').disabled = true;
    return;
  }
  try {
    const [config, summary] = await Promise.all([
      api('/api/payments/config'),
      api(`/api/payments/quotation/${encodeURIComponent(quotationId)}/summary`)
    ]);
    paymentSummary = summary;
    const environment = document.getElementById('environment');
    environment.textContent = `${config.mode.toUpperCase()} MODE`;
    environment.classList.toggle('live', config.mode === 'live');
    document.getElementById('quotation-number').textContent = summary.quotationNumber;
    document.getElementById('customer-name').textContent = summary.customerName;
    document.getElementById('confirmed-amount').textContent = money(summary.confirmedAmountPaise);
    document.getElementById('paid-amount').textContent = money(summary.paidPaise);
    document.getElementById('balance-amount').textContent = money(summary.balancePaise);
    document.getElementById('advance-amount').textContent = money(summary.advanceRequiredPaise);
    document.getElementById('pay-now').disabled = summary.status !== 'Approved';
    if (summary.status !== 'Approved') document.getElementById('payment-message').textContent = 'This quotation must be approved before payment.';
  } catch (error) {
    document.getElementById('payment-message').className = 'error-message';
    document.getElementById('payment-message').textContent = error.message;
  }
  await loadHistory();
}

async function loadHistory() {
  try {
    const history = await api('/api/payments/history');
    document.getElementById('payment-history').innerHTML = history.length ? `
      <table class="history-table"><thead><tr><th>Payment</th><th>Purpose</th><th>Amount</th><th>Status</th></tr></thead>
      <tbody>${history.map(item => `<tr><td>${item.razorpay_payment_id || item.razorpay_order_id || '—'}</td><td>${item.purpose}</td><td>${money(item.amount_paise)}</td><td><span class="status ${item.status}">${item.status}</span></td></tr>`).join('')}</tbody></table>` : '<p>No payment transactions yet.</p>';
  } catch (error) {
    document.getElementById('payment-history').innerHTML = `<p class="error-message">${error.message}</p>`;
  }
}

document.querySelectorAll('.milestone').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.milestone').forEach(item => {item.classList.remove('active'); item.setAttribute('aria-checked', 'false');});
  button.classList.add('active');
  button.setAttribute('aria-checked', 'true');
  selectedPurpose = button.dataset.purpose;
}));

document.getElementById('pay-now').addEventListener('click', async () => {
  const button = document.getElementById('pay-now');
  button.disabled = true;
  button.textContent = 'Creating secure order...';
  try {
    const order = await api('/api/payments/orders', {method:'POST', headers:csrfHeaders(), body:JSON.stringify({quotationId, purpose:selectedPurpose})});
    const checkout = new Razorpay({
      key: order.keyId,
      amount: order.amountPaise,
      currency: order.currency,
      name: 'SunPower Nexus',
      description: `${paymentSummary.quotationNumber} - ${selectedPurpose}`,
      order_id: order.razorpayOrderId,
      handler: async response => {
        try {
          await api('/api/payments/verify', {method:'POST', headers:csrfHeaders(), body:JSON.stringify({
            razorpay_order_id:response.razorpay_order_id,
            razorpay_payment_id:response.razorpay_payment_id,
            razorpay_signature:response.razorpay_signature
          })});
          location.reload();
        } catch (error) {
          document.getElementById('payment-message').className = 'error-message';
          document.getElementById('payment-message').textContent = error.message;
        }
      },
      modal: {ondismiss: () => {button.disabled = false; button.textContent = 'Pay Now';}},
      theme: {color:'#071d3a'}
    });
    checkout.open();
    button.textContent = 'Checkout opened';
  } catch (error) {
    document.getElementById('payment-message').className = 'error-message';
    document.getElementById('payment-message').textContent = error.message;
    button.disabled = false;
    button.textContent = 'Pay Now';
  }
});

load();
