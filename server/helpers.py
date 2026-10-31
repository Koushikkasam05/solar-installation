# -*- coding: utf-8 -*-
"""SolarFlow ERP - Business Calculation Algorithms & Helpers."""
import hashlib
import math
from datetime import datetime
from server.database import query_db

def calculate_recommended_capacity(monthly_kwh, roof_area_sqft, sanctioned_load_kw):
    """Calculate recommended solar capacity (kW) based on consumption, roof, and load."""
    capacity_by_kwh = monthly_kwh / 120.0
    capacity_by_roof = roof_area_sqft / 90.0
    rec = min(capacity_by_kwh, capacity_by_roof)
    if sanctioned_load_kw > 0 and rec > sanctioned_load_kw:
        rec = sanctioned_load_kw
    return round(rec, 2)


def calculate_feasibility_score(roof_area_sqft, monthly_kwh):
    """Calculate site feasibility score (0-100)."""
    score = 100
    if roof_area_sqft < 450:
        score -= 15
    if monthly_kwh < 200:
        score -= 20
    return max(score, 0)


def calculate_auto_bom(system_kw, cable_distance_m=20):
    """Generate automatic Bill of Materials for a given system size."""
    total_watts = system_kw * 1000
    panel_wattage = 550
    panel_count = math.ceil(total_watts / panel_wattage)
    inverter_kw = round(system_kw * 1.0, 2)
    cable_length = cable_distance_m * 2 + 10
    return {
        'panel_count': panel_count,
        'panel_wattage': panel_wattage,
        'inverter_kw': inverter_kw,
        'cable_length_m': cable_length,
        'mounting_slots': panel_count,
    }


def calculate_subsidy(system_kw):
    """PM Surya Ghar subsidy calculation in INR for rooftop solar systems.

    Structure: up to 2 kW -> ₹30,000/kW, 2-3 kW -> ₹18,000/kW for additional capacity,
    capped at ₹78,000 for 3 kW and above.
    """
    if system_kw is None:
        return 0.0
    cap = max(float(system_kw), 0.0)
    if cap <= 2.0:
        return cap * 30000.0
    if cap <= 3.0:
        return 60000.0 + (cap - 2.0) * 18000.0
    return 78000.0


def calculate_readiness_score(survey_approved, payment_ok, stock_available, equipment_allocated, technician_assigned):
    """Calculate Installation Readiness Score (0-100)."""
    score = 0
    if survey_approved:
        score += 20
    if payment_ok:
        score += 20
    if stock_available:
        score += 20
    if equipment_allocated:
        score += 20
    if technician_assigned:
        score += 20

    if score >= 80:
        label = 'Ready for Execution'
    elif score >= 40:
        label = 'Partially Ready'
    else:
        label = 'Not Ready'
    return score, label


def generate_warranty_token(ref, customer_id, serial, equip_type, start_date):
    """Generate SHA-256 warranty verification token."""
    data = f"{ref}|{customer_id}|{serial}|{equip_type}|{start_date}"
    return hashlib.sha256(data.encode()).hexdigest()


def calculate_project_cost(revenue, material, labour, transport, additional, other, threshold=10.0):
    """Calculate project costing with profit leakage detection."""
    total_cost = material + labour + transport + additional + other
    gross_profit = revenue - total_cost
    margin = (gross_profit / revenue * 100) if revenue > 0 else 0

    if margin >= 20:
        health = 'healthy'
    elif margin >= 10:
        health = 'moderate'
    else:
        health = 'critical'

    leakage = 1 if (margin < threshold) else 0
    return {
        'total_cost': round(total_cost, 2),
        'gross_profit': round(gross_profit, 2),
        'gross_margin_percent': round(margin, 2),
        'margin_health': health,
        'leakage_alert': leakage,
    }


def get_next_ref(prefix, table, field='ref'):
    """Generate next sequential reference number."""
    result = query_db(f"SELECT {field} FROM {table} ORDER BY id DESC LIMIT 1", one=True)
    if result and result[field]:
        parts = result[field].split('/')
        try:
            num = int(parts[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    year = datetime.now().year
    return f"{prefix}/{year}/{num:04d}"

generate_auto_bom = calculate_auto_bom
