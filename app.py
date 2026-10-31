from pathlib import Path

import os
import sqlite3
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO

from flask import Flask, jsonify, request, send_file, send_from_directory
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web_app"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "solarflow.db"

app = Flask(__name__, static_folder=None)


def db():
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def initialize_database():
    with db() as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            specification TEXT NOT NULL,
            unit_price REAL NOT NULL,
            subsidy_eligible INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS quotation (
            id TEXT PRIMARY KEY,
            number TEXT NOT NULL,
            version INTEGER NOT NULL,
            parent_id TEXT,
            customer_name TEXT NOT NULL,
            customer_details TEXT,
            input_json TEXT NOT NULL,
            calculation_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS survey_request (
            id TEXT PRIMARY KEY,
            quotation_id TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            preferred_at TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            address TEXT,
            technician TEXT NOT NULL,
            status TEXT NOT NULL,
            report_json TEXT,
            created_at TEXT NOT NULL
        );
        """)
        count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            connection.executemany(
                "INSERT INTO products(category,name,specification,unit_price,subsidy_eligible) VALUES(?,?,?,?,?)",
                [
                    ("panel", "Mono PERC Solar Panel", "540 W mono-facial", 18500, 1),
                    ("panel", "TOPCon Solar Panel", "550 W bifacial-ready", 20500, 1),
                    ("inverter", "Hybrid Solar Inverter", "5 kW, single-phase", 78000, 1),
                    ("inverter", "On-grid Solar Inverter", "5 kW, single-phase", 62000, 1),
                    ("battery", "LiFePO4 Battery", "5.12 kWh modular battery", 95000, 0),
                    ("battery", "Backup Battery Bank", "3 kWh battery", 52000, 0),
                    ("accessory", "ACDB/DCDB Protection Kit", "With surge protection", 12500, 0),
                    ("accessory", "Solar DC Cable Set", "6 sq.mm, configured length", 8500, 0),
                    ("accessory", "Earthing Kit", "Chemical earthing kit", 6500, 0),
                    ("combo", "Residential Starter Combo", "5 kW system package", 325000, 1),
                ],
            )


initialize_database()


@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_files(filename: str):
    return send_from_directory(WEB_DIR, filename)


@app.get("/api/products")
def products():
    with db() as connection:
        rows = connection.execute(
            "SELECT id, category, name, specification, unit_price, subsidy_eligible FROM products ORDER BY category, name"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/quotes/calculate")
def calculate_quote():
    payload = request.get_json(silent=True) or {}
    with db() as connection:
        products_by_id = {
            row["id"]: dict(row)
            for row in connection.execute(
                "SELECT id, category, name, specification, unit_price, subsidy_eligible FROM products"
            )
        }

    line_items = []
    products_total = Decimal("0")
    subsidy_eligible = bool(payload.get("subsidy"))
    for selected in payload.get("items", []):
        product = products_by_id.get(int(selected.get("id", 0)))
        quantity = max(1, min(int(selected.get("quantity", 1)), 100))
        if not product:
            continue
        subtotal = money(Decimal(str(product["unit_price"])) * quantity)
        products_total += subtotal
        line_items.append({
            "id": product["id"],
            "category": product["category"],
            "name": product["name"],
            "specification": product["specification"],
            "quantity": quantity,
            "unit_price": float(money(product["unit_price"])),
            "subtotal": float(subtotal),
        })

    required_capacity = max(0, Decimal(str(payload.get("capacity", 0))))
    installation = money(required_capacity * Decimal(str(payload.get("installation_rate", 3500))))
    transportation = money(payload.get("transportation", 0))
    earthing = money(payload.get("earthing_cost", 6500)) if payload.get("earthing") else Decimal("0")
    other_charges = money(payload.get("other_charges", 0))
    subtotal_before_tax = products_total + installation + transportation + earthing + other_charges
    tax = money(subtotal_before_tax * Decimal(str(payload.get("tax_rate", 0.18))))
    subsidy = Decimal("0")
    if subsidy_eligible and payload.get("customer_type") == "Residential":
        eligible_subtotal = sum(
            money(item["unit_price"] * item["quantity"])
            for item in line_items if products_by_id[item["id"]]["subsidy_eligible"]
        )
        configured_cap = min(money(payload.get("subsidy_cap", 78000)), eligible_subtotal)
        subsidy = configured_cap if required_capacity <= Decimal("10") else min(configured_cap, money(eligible_subtotal * Decimal("0.30")))
    final_amount = money(subtotal_before_tax + tax - subsidy)
    result = {
        "items": line_items,
        "products_total": float(products_total),
        "installation": float(installation),
        "transportation": float(transportation),
        "earthing": float(earthing),
        "other_charges": float(other_charges),
        "tax": float(tax),
        "subsidy": float(subsidy),
        "final_amount": float(final_amount),
        "assumptions": {
            "tax_rate": payload.get("tax_rate", 0.18),
            "subsidy_requested": subsidy_eligible,
            "subsidy_applied": float(subsidy),
            "advance_payment_policy": "The existing configurable 50% advance policy applies only to orders when configured by an authorized user.",
        },
    }
    return jsonify(result)


@app.post("/api/quotes")
def save_quote():
    payload = request.get_json(silent=True) or {}
    calculation_response = calculate_quote()
    calculation = calculation_response.get_json()
    with db() as connection:
        quote = connection.execute(
            "SELECT number, parent_id, version FROM quotation WHERE id=?", (payload.get("parent_id"),)
        ).fetchone()
        number = quote["number"] if quote else f"SF-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        parent_id = quote["parent_id"] if quote and quote["parent_id"] else payload.get("parent_id")
        version = (quote["version"] + 1) if quote else 1
        quote_id = uuid.uuid4().hex
        connection.execute(
            "INSERT INTO quotation(id,number,version,parent_id,customer_name,customer_details,input_json,calculation_json,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (quote_id, number, version, parent_id, payload.get("customer_name", "Walk-in Customer"),
             payload.get("customer_details", ""), __import__("json").dumps(payload),
             __import__("json").dumps(calculation), datetime.now().isoformat()),
        )
    return jsonify({"id": quote_id, "number": number, "version": version, "calculation": calculation})


@app.get("/api/quotes/<quote_id>/pdf")
def quotation_pdf(quote_id):
    import json
    with db() as connection:
        quote = connection.execute("SELECT * FROM quotation WHERE id=?", (quote_id,)).fetchone()
    if not quote:
        return jsonify({"error": "Quotation not found"}), 404
    calculation = json.loads(quote["calculation_json"])
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("SolarFlow ERP", styles["Title"]),
        Paragraph("INDICATIVE ESTIMATE - NOT AN APPROVED QUOTATION", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph(f"Quotation: {quote['number']}  |  Version: {quote['version']}  |  Date: {quote['created_at'][:10]}", styles["BodyText"]),
        Paragraph(f"Customer: {quote['customer_name']}<br/>{quote['customer_details']}", styles["BodyText"]),
        Spacer(1, 18),
    ]
    table_data = [["Item", "Qty", "Unit price", "Subtotal"]]
    for item in calculation["items"]:
        table_data.append([item["name"], item["quantity"], f"INR {item['unit_price']:,.2f}", f"INR {item['subtotal']:,.2f}"])
    table = Table(table_data, colWidths=[280, 45, 100, 100])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#246b45")),
                               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                               ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                               ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(table)
    story.append(Spacer(1, 18))
    summary = [
        ("Products", calculation["products_total"]), ("Installation", calculation["installation"]),
        ("Transportation", calculation["transportation"]), ("Earthing", calculation["earthing"]),
        ("Other charges", calculation["other_charges"]), ("Tax", calculation["tax"]),
        ("Indicative subsidy", -calculation["subsidy"]), ("Estimated total", calculation["final_amount"]),
    ]
    story.append(Table([["Amount", "INR"]] + [[name, f"{amount:,.2f}"] for name, amount in summary],
                       colWidths=[360, 165], style=TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                                               ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf4ed")),
                                                               ("ALIGN", (1, 0), (-1, -1), "RIGHT")])))
    story += [Spacer(1, 18), Paragraph("Terms & Conditions", styles["Heading3"]),
              Paragraph("This estimate is indicative, subject to site survey, product availability, tax configuration, and written approval. Subsidy eligibility and approval are not guaranteed.", styles["BodyText"])]
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{quote['number']}-v{quote['version']}.pdf", mimetype="application/pdf")


@app.post("/api/site-visits")
def create_site_visit():
    payload = request.get_json(silent=True) or {}
    if not payload.get("preferred_at"):
        return jsonify({"error": "A preferred date and time is required."}), 400
    visit_id = uuid.uuid4().hex
    technicians = ["Arun Survey Tech", "Neha Survey Tech"]
    technician = technicians[int(visit_id[0], 16) % len(technicians)]
    with db() as connection:
        connection.execute(
            "INSERT INTO survey_request(id,quotation_id,customer_name,customer_phone,preferred_at,latitude,longitude,accuracy,address,technician,status,report_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (visit_id, payload.get("quotation_id"), payload.get("customer_name"), payload.get("customer_phone"),
             payload.get("preferred_at"), payload.get("latitude"), payload.get("longitude"),
             payload.get("accuracy"), payload.get("address"), technician, "Requested",
             None, datetime.now().isoformat()),
        )
    return jsonify({"id": visit_id, "technician": technician, "status": "Requested"})


@app.get("/api/solar-insights")
def solar_insights():
    api_key = os.getenv("GOOGLE_SOLAR_API_KEY")
    if not api_key:
        return jsonify({"available": False, "message": "Google Solar API is not configured. Manual measurement is available."})
    return jsonify({"available": False, "message": "Building insights require a live Google Solar API server integration with the configured API key."})


@app.post("/api/site-visits/<visit_id>/report")
def submit_survey_report(visit_id):
    payload = request.get_json(silent=True) or {}
    import json
    with db() as connection:
        result = connection.execute(
            "UPDATE survey_request SET status=?, report_json=? WHERE id=?",
            ("Submitted for approval", json.dumps(payload), visit_id),
        )
    if result.rowcount == 0:
        return jsonify({"error": "Survey request not found"}), 404
    return jsonify({"id": visit_id, "status": "Submitted for approval"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
