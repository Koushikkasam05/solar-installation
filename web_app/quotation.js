let products = [];
let savedQuote = null;
const format = value => Number(value || 0).toLocaleString('en-IN', {maximumFractionDigits: 2});
async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
async function load() {
  products = await api('/api/products');
  addProductRow();
  await recalculate();
}
function addProductRow(productId = products[0]?.id, quantity = 1) {
  const row = document.createElement('div');
  row.className = 'product-row';
  row.innerHTML = `<select>${products.map(p => `<option value="${p.id}" ${p.id === Number(productId) ? 'selected' : ''}>${p.category}: ${p.name}</option>`).join('')}</select>
    <input type="number" min="1" max="100" value="${quantity}" aria-label="Quantity">
    <button class="remove-product" type="button" title="Remove product">×</button>`;
  row.querySelector('.remove-product').onclick = () => row.remove();
  document.getElementById('productRows').appendChild(row);
}
function payload() {
  return {
    customer_name: document.getElementById('customerName').value,
    customer_details: `${document.getElementById('customerPhone').value} | ${document.getElementById('customerType').value} | ${document.getElementById('systemType').value}`,
    customer_type: document.getElementById('customerType').value,
    capacity: Number(document.getElementById('capacity').value),
    installation_rate: Number(document.getElementById('installationRate').value),
    transportation: Number(document.getElementById('transportation').value),
    earthing: document.getElementById('earthing').checked,
    earthing_cost: 6500,
    subsidy: document.getElementById('subsidy').checked,
    items: [...document.querySelectorAll('.product-row')].map(row => ({
      id: Number(row.querySelector('select').value),
      quantity: Number(row.querySelector('input').value)
    }))
  };
}
async function recalculate() {
  const calculation = await api('/api/quotes/calculate', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});
  savedQuote = null;
  document.getElementById('downloadPdf').disabled = true;
  document.getElementById('finalAmount').textContent = format(calculation.final_amount);
  document.getElementById('summaryRows').innerHTML = [
    ['Products', calculation.products_total], ['Installation', calculation.installation],
    ['Transportation', calculation.transportation], ['Earthing', calculation.earthing],
    ['Other charges', calculation.other_charges], ['Tax', calculation.tax],
    ['Indicative subsidy', -calculation.subsidy], ['Estimated total', calculation.final_amount]
  ].map(([label,value]) => `<div class="summary-row"><span>${label}</span><strong>₹ ${format(value)}</strong></div>`).join('');
}
async function saveQuote() {
  savedQuote = await api('/api/quotes', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});
  document.getElementById('downloadPdf').disabled = false;
  document.getElementById('requestVisit').href = `survey.html?quotation=${savedQuote.id}`;
  alert(`Saved ${savedQuote.number}, version ${savedQuote.version}`);
}
document.getElementById('addProduct').onclick = () => addProductRow();
document.getElementById('recalculate').onclick = () => recalculate().catch(alert);
document.getElementById('saveQuote').onclick = () => saveQuote().catch(alert);
document.getElementById('viewQuote').onclick = () => {
  if (!savedQuote) return alert('Save the estimate first to view it.');
  alert(`${savedQuote.number} version ${savedQuote.version}\nIndicative amount: ₹${format(savedQuote.calculation.final_amount)}`);
};
document.getElementById('downloadPdf').onclick = () => {
  if (savedQuote) window.open(`/api/quotes/${savedQuote.id}/pdf`, '_blank');
};
load().catch(error => alert(error.message));
