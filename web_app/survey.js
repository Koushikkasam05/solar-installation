const params = new URLSearchParams(location.search);
let visitId = null;
let currentPosition = null;
let drawnPolygon = null;
const map = L.map('roofMap').setView([20.5937, 78.9629], 5);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 19,
  attribution: 'Tiles © Esri'
}).addTo(map);
const satelliteNote = L.control({position:'bottomright'});
satelliteNote.onAdd = () => { const div=L.DomUtil.create('div','notice'); div.style.margin='0'; div.textContent='Satellite imagery © Esri. Confirm imagery age/location accuracy on site.'; return div; };
satelliteNote.addTo(map);
const drawnItems = new L.FeatureGroup().addTo(map);
const drawControl = new L.Control.Draw({
  draw: {polygon:{shapeOptions:{color:'#246b45'}}, polyline:false, rectangle:false, circle:false, marker:false, circlemarker:false},
  edit:{featureGroup:drawnItems, remove:false}
});

document.getElementById('useLocation').onclick = () => {
  if (!navigator.geolocation) return document.getElementById('locationStatus').textContent = 'Geolocation is not supported by this browser.';
  document.getElementById('locationStatus').textContent = 'Waiting for location permission…';
  navigator.geolocation.getCurrentPosition(position => {
    currentPosition = position.coords;
    const lat = currentPosition.latitude, lng = currentPosition.longitude;
    map.setView([lat,lng],18);
    L.marker([lat,lng]).addTo(map).bindPopup('Customer site location').openPopup();
    document.getElementById('address').value ||= `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    document.getElementById('locationStatus').textContent = `Latitude ${lat.toFixed(6)}, longitude ${lng.toFixed(6)}, accuracy ±${Math.round(currentPosition.accuracy)} m`;
  }, error => document.getElementById('locationStatus').textContent = `Location unavailable: ${error.message}`);
};
document.getElementById('startDraw').onclick = () => map.addControl(drawControl);
document.getElementById('clearDraw').onclick = () => { drawnItems.clearLayers(); updateMeasurements(null); map.removeControl(drawControl); };
map.on(L.Draw.Event.CREATED, event => {
  drawnItems.clearLayers();
  drawnPolygon = event.layer;
  drawnItems.addLayer(drawnPolygon);
  map.removeControl(drawControl);
  updateMeasurements(drawnPolygon.getLatLngs()[0]);
});
function distance(a,b) {
  const earth=6371000, rad=n=>n*Math.PI/180;
  const dLat=rad(b.lat-a.lat), dLng=rad(b.lng-a.lng);
  return 2*earth*Math.asin(Math.sqrt(Math.sin(dLat/2)**2 + Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(dLng/2)**2));
}
function updateMeasurements(points) {
  if (!points || points.length < 3) {
    roofArea.textContent='—'; roofPerimeter.textContent='—'; roofCapacity.textContent='—'; return;
  }
  let area=0;
  for(let i=0;i<points.length;i++) {
    const a=points[i], b=points[(i+1)%points.length];
    const x1=a.lng*Math.PI/180*Math.cos(a.lat*Math.PI/180), y1=a.lat*Math.PI/180;
    const x2=b.lng*Math.PI/180*Math.cos(b.lat*Math.PI/180), y2=b.lat*Math.PI/180;
    area += x1*y2-x2*y1;
  }
  let perimeter=0;
  for(let i=0;i<points.length;i++) perimeter+=distance(points[i],points[(i+1)%points.length]);
  const polygonArea=Math.abs(area)*6371000*6371000/2;
  const usable=polygonArea*0.75;
  const capacity=(usable/Math.pow(180,-1))/1000; // descriptive fallback uses 180 W/m²
  document.getElementById('roofArea').textContent=`${Math.max(polygonArea,0).toFixed(0)} m²`;
  document.getElementById('roofPerimeter').textContent=`${perimeter.toFixed(1)} m`;
  document.getElementById('roofCapacity').textContent=`${(usable*180/1000).toFixed(1)} kWp`;
}
async function post(url, data) {
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  if(!response.ok) throw new Error(await response.text());
  return response.json();
}
document.getElementById('requestVisit').onclick=async()=>{
  try {
    const result=await post('/api/site-visits',{
      quotation_id:new URLSearchParams(location.search).get('quotation'),
      customer_name:customerName.value, customer_phone:customerPhone.value,
      preferred_at:preferredAt.value, address:address.value,
      latitude:currentPosition?.latitude, longitude:currentPosition?.longitude, accuracy:currentPosition?.accuracy
    });
    visitId=result.id;
    locationStatus.textContent=`Requested. Assigned technician: ${result.technician}`;
  } catch(error) { locationStatus.textContent=error.message; }
};
document.getElementById('submitReport').onclick=async()=>{
  if(!visitId) return submissionStatus.textContent='Request a site visit before submitting its report.';
  const photos=[...document.getElementById('photos').files].map(file=>({name:file.name,size:file.size}));
  try {
    const result=await post(`/api/site-visits/${visitId}/report`,{
      roof_condition:roofCondition.value, shading:shading.value, orientation:orientation.value,
      inclination:inclination.value, available_area:availableArea.value, cable_distance:cableDistance.value,
      electrical_condition:electrical.value, earthing_required:earthingRequired.value,
      preferences:preferences.value, remarks:remarks.value, photographs:photos,
      measurements:{area:roofArea.textContent,perimeter:roofPerimeter.textContent,capacity:roofCapacity.textContent}
    });
    submissionStatus.textContent=`Report status: ${result.status}`;
  } catch(error) { submissionStatus.textContent=error.message; }
};
fetch('/api/solar-insights?lat=20.5937&lng=78.9629').then(r=>r.json()).then(data=>{
  document.getElementById('apiStatus').textContent=data.message || 'Building insights unavailable. Manual measurement remains active.';
});
