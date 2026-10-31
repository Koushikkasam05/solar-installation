# SolarFlow ERP – Known Limitations & Future Technical Roadmap

---

## 1. Known Limitations in Current Release

| # | Domain Area | Current Implementation Boundary | Recommended Production Workaround |
| :-: | :--- | :--- | :--- |
| **1** | **3D Shadow Ray-Tracing** | Rooftop shadow assessment utilizes measured azimuth, tilt angle, obstacle height, and hourly sunlight window. Automated LiDAR 3D mesh rendering is not native to Odoo Community. | Technicians attach drone orthophotos, Helioscope/PVsyst PDF exports, or sketch diagrams via native Odoo attachment widgets. |
| **2** | **DISCOM Net Meter APIs** | State electricity distribution utilities (DISCOMs) in India / US have heterogeneous legacy portal interfaces lacking unified public REST APIs. | Handled via Odoo milestone workflow gates (`phase_6_discom_sync`) requiring inspector sign-off and reference upload. |
| **3** | **IoT Inverter Telemetry** | Ticket creation maps Inverter Fault error codes and root cause diagnostics manually or via webhook endpoints. Continuous 5-second raw MQTT streaming is not processed directly in Odoo ORM to protect Postgres transaction throughput. | An external edge broker (e.g., EMQX / Telegraf) aggregates raw high-frequency telemetry, pushing only critical breakdown alerts to Odoo via REST / XML-RPC. |
| **4** | **Offline Mobile App Sync** | Field technicians access mobile-optimized responsive web forms (Kanban cards, touchscreen buttons, photo capture). Full offline caching when operating in zero-cellular basements relies on browser PWA cache. | Install mobile browser shortcut as PWA or sync data before descending into shielded basements. |

---

## 2. Technical Roadmap (Future Phases)

1. **AI Rooftop Geometry Recognition:** Satellite imagery segmentation via computer vision to automatically detect roof perimeter and calculate usable area.
2. **Dynamic Tariff Scraper:** Automated scraper for regional electricity board tariff hikes to update customer ROI payback projections automatically.
3. **Automated WhatsApp Notifications:** Automated transactional WhatsApp updates to customers when field crew is dispatched and when digital warranty is generated.
4. **Subcontractor Crew Portal:** Dedicated self-service portal for third-party civil structure installation contractors to submit work completion photos and claim labor payments.
