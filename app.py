from pathlib import Path

import os
import sqlite3
import uuid
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO

from flask import Flask, jsonify, request, send_file, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import secrets
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web_app"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "solarflow.db"

app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=os.getenv("SUNPOWER_SECRET_KEY", secrets.token_hex(32)),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SUNPOWER_SECURE_COOKIES", "0") == "1",
)


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
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            approved INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
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
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            quotation_id TEXT,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            booking_method TEXT NOT NULL,
            verification_code TEXT,
            status TEXT NOT NULL,
            assigned_role TEXT,
            gps_lat REAL,
            gps_lng REAL,
            gps_accuracy REAL,
            evidence_json TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            recipient_role TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT,
            status TEXT NOT NULL DEFAULT 'unread',
            due_at TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS warranties (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            serial_number TEXT NOT NULL,
            product_name TEXT NOT NULL,
            allocation_date TEXT NOT NULL,
            start_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            coverage TEXT NOT NULL,
            policy TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS b2b_organizations (
            id TEXT PRIMARY KEY,
            organization_name TEXT NOT NULL,
            business_type TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            business_email TEXT NOT NULL,
            phone TEXT NOT NULL,
            registered_address TEXT NOT NULL,
            gstin TEXT,
            billing_address TEXT,
            installation_locations TEXT,
            documents_json TEXT NOT NULL,
            approval_status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS business_analysis_history (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            agent_answer TEXT NOT NULL,
            specialist_agents TEXT NOT NULL,
            records_considered INTEGER NOT NULL,
            confidence TEXT NOT NULL,
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

        demo_password = generate_password_hash(os.getenv("SUNPOWER_DEMO_PASSWORD", "Solar@123"))
        demo_accounts = [
            ("customer@sunpower.local", "Demo Customer", "customer"),
            ("sales@sunpower.local", "Demo Sales", "sales"),
            ("warehouse@sunpower.local", "Demo Warehouse", "warehouse"),
            ("technician@sunpower.local", "Demo Technician", "technician"),
            ("support@sunpower.local", "Demo Support", "support"),
            ("admin@sunpower.local", "Demo Admin", "admin"),
        ]
        for email, name, role in demo_accounts:
            connection.execute(
                """INSERT OR IGNORE INTO users(email, name, password_hash, role, approved, created_at)
                   VALUES(?, ?, ?, ?, 1, ?)""",
                (email, name, demo_password, role, datetime.now().isoformat()),
            )


initialize_database()


def current_user():
    if not session.get("user_id"):
        return None
    with db() as connection:
        return connection.execute(
            "SELECT id, email, name, role, approved FROM users WHERE id=? AND approved=1",
            (session["user_id"],),
        ).fetchone()


def login_required(roles=None):
    allowed = set(roles or [])

    def decorator(function):
        @wraps(function)
        def guarded(*args, **kwargs):
            user = current_user()
            if user is None:
                return jsonify({"error": "Authentication required"}), 401
            if allowed and user["role"] not in allowed:
                return jsonify({"error": "Forbidden"}), 403
            request.user = user
            return function(*args, **kwargs)
        return guarded
    return decorator


@app.before_request
def enforce_csrf():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.path == "/api/auth/login":
        return None
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and session.get("user_id"):
        if request.headers.get("X-CSRF-Token") != session.get("csrf_token"):
            return jsonify({"error": "Invalid CSRF token"}), 403


@app.post("/api/auth/login")
def auth_login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    with db() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE email=? AND approved=1", (email,),
        ).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    session.clear()
    session["user_id"] = user["id"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    return jsonify({
        "user": {"email": user["email"], "name": user["name"], "role": user["role"]},
        "csrfToken": session["csrf_token"],
    })


@app.post("/api/auth/logout")
@login_required()
def auth_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/auth/me")
def auth_me():
    user = current_user()
    if user is None:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": dict(user)})


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


ORDER_STATES = {
    "created": {"warehouse"},
    "warehouse_ready": {"sales"},
    "delivered": {"technician"},
    "installed": {"support"},
    "warranty_issued": {"completed"},
    "completed": set(),
}


def notify(role, title, message, due_at=None):
    with db() as connection:
        connection.execute(
            "INSERT INTO notifications(id,recipient_role,title,message,due_at,created_at) VALUES(?,?,?,?,?,?)",
            (uuid.uuid4().hex, role, title, message, due_at, datetime.now().isoformat()),
        )


@app.get("/api/dashboard/<role>")
@login_required(["admin", "warehouse", "sales", "technician", "support", "customer"])
def dashboard(role):
    if request.user["role"] != "admin" and request.user["role"] != role:
        return jsonify({"error": "Forbidden"}), 403
    with db() as connection:
        products_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if request.user["role"] == "customer":
            orders = connection.execute(
                "SELECT * FROM orders WHERE created_by=? ORDER BY created_at DESC LIMIT 20",
                (request.user["name"],),
            ).fetchall()
        else:
            orders = connection.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 20").fetchall()
        notifications = connection.execute(
            "SELECT * FROM notifications WHERE recipient_role=? AND status='unread' ORDER BY created_at DESC",
            (role,),
        ).fetchall()
        surveys = connection.execute("SELECT * FROM survey_request ORDER BY created_at DESC LIMIT 20").fetchall()
        warranties = connection.execute("SELECT COUNT(*) FROM warranties").fetchone()[0]
    return jsonify({
        "role": role,
        "metrics": {
            "products": products_count,
            "orders": len(orders),
            "surveys": len(surveys),
            "warranties": warranties,
        },
        "orders": [dict(row) for row in orders],
        "notifications": [dict(row) for row in notifications],
        "surveys": [dict(row) for row in surveys],
    })


@app.post("/api/orders")
@login_required(["customer", "sales", "admin"])
def create_order():
    payload = request.get_json(silent=True) or {}
    if not payload.get("customer_name"):
        return jsonify({"error": "customer_name is required"}), 400
    order_id = uuid.uuid4().hex
    code = str(uuid.uuid4().int)[:6] if payload.get("booking_method") == "technician_otp" else None
    now = datetime.now().isoformat()
    with db() as connection:
        connection.execute(
            """INSERT INTO orders(id,quotation_id,customer_name,customer_phone,booking_method,verification_code,status,
            assigned_role,gps_lat,gps_lng,gps_accuracy,evidence_json,created_by,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (order_id, payload.get("quotation_id"), payload["customer_name"], payload.get("customer_phone"),
             payload.get("booking_method", "customer_challenge"), code, "created", "warehouse", None, None, None,
             __import__("json").dumps(payload.get("evidence", {})), request.user["name"], now, now),
        )
    notify("warehouse", "New customer order", f"{payload['customer_name']} placed order {order_id[:8]}")
    return jsonify({"id": order_id, "verification_code": code if payload.get("booking_method") == "technician_otp" else None, "status": "created"})


@app.post("/api/orders/<order_id>/transition")
@login_required(["warehouse", "sales", "technician", "support", "admin"])
def transition_order(order_id):
    payload = request.get_json(silent=True) or {}
    target = payload.get("status")
    stage_roles = {"warehouse": "warehouse_ready", "sales": "delivered", "technician": "installed",
                   "support": "warranty_issued", "admin": "completed"}
    acting_role = request.user["role"]
    with db() as connection:
        row = connection.execute("SELECT status FROM orders WHERE id=?", (order_id,)).fetchone()
        if not row:
            return jsonify({"error": "Order not found"}), 404
        allowed = ORDER_STATES.get(row["status"], set())
        if target != stage_roles.get(acting_role) or acting_role not in allowed:
            return jsonify({"error": f"Invalid transition from {row['status']} to {target} by {acting_role}"}), 409
        if target == "installed":
            checks = payload.get("qc_checklist", [])
            electrical = payload.get("electrical", {})
            if not all(checks) or float(electrical.get("earth_ohms", 99)) > 5:
                return jsonify({"error": "QC checklist and earth resistance must meet safety limits"}), 422
        connection.execute(
            "UPDATE orders SET status=?, evidence_json=?, gps_lat=?, gps_lng=?, gps_accuracy=?, updated_at=? WHERE id=?",
            (target, __import__("json").dumps(payload.get("evidence", {})), payload.get("latitude"),
             payload.get("longitude"), payload.get("accuracy"), datetime.now().isoformat(), order_id),
        )
    next_role = {"warehouse_ready": "sales", "delivered": "technician", "installed": "support", "warranty_issued": "admin"}
    recipient = next_role.get(target)
    if recipient:
        notify(recipient, f"Order moved to {target}", f"Order {order_id[:8]} requires {recipient} action.")
    return jsonify({"id": order_id, "status": target})


@app.post("/api/orders/<order_id>/warranty")
@login_required(["support", "admin"])
def issue_warranty(order_id):
    payload = request.get_json(silent=True) or {}
    serials = payload.get("serials", [])
    if not serials:
        return jsonify({"error": "At least one allocated product serial is required"}), 400
    allocation_date = payload.get("allocation_date", datetime.now().date().isoformat())
    years = int(payload.get("policy_years", 25))
    start_event = payload.get("start_event", "allocation")
    with db() as connection:
        for serial in serials:
            warranty_id = uuid.uuid4().hex
            start_date = allocation_date if start_event == "allocation" else datetime.now().date().isoformat()
            start = datetime.fromisoformat(start_date)
            expiry = start.replace(year=start.year + years).date().isoformat()
            connection.execute(
                """INSERT INTO warranties(id,order_id,serial_number,product_name,allocation_date,start_date,expiry_date,coverage,policy)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (warranty_id, order_id, serial["serial_number"], serial["product_name"], allocation_date,
                 start_date, expiry, payload.get("coverage", "Manufacturing defects subject to policy"),
                 payload.get("policy", f"{years}-year configured policy")),
            )
    return jsonify({"order_id": order_id, "start_event": start_event, "issued": len(serials)})


@app.post("/api/notifications/<notification_id>/read")
def read_notification(notification_id):
    with db() as connection:
        connection.execute("UPDATE notifications SET status='read' WHERE id=?", (notification_id,))
    return jsonify({"status": "read"})


@app.post("/api/b2b/organizations")
def register_b2b_organization():
    payload = request.get_json(silent=True) or {}
    required = [
        "organization_name", "business_type", "contact_person",
        "business_email", "phone", "registered_address"
    ]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if missing:
        return jsonify({"error": "Missing required fields: " + ", ".join(missing)}), 400
    organization_id = uuid.uuid4().hex
    with db() as connection:
        connection.execute(
            """INSERT INTO b2b_organizations
            (id,organization_name,business_type,contact_person,business_email,phone,registered_address,
             gstin,billing_address,installation_locations,documents_json,approval_status,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (organization_id, payload["organization_name"], payload["business_type"], payload["contact_person"],
             payload["business_email"], payload["phone"], payload["registered_address"],
             payload.get("gstin"), payload.get("billing_address"), payload.get("installation_locations"),
             json.dumps(payload.get("documents", [])), "Pending approval", datetime.now().isoformat()),
        )
    return jsonify({"id": organization_id, "approval_status": "Pending approval",
                    "gstin_verification": "Not verified by an integrated service"})


@app.get("/api/b2b/organizations")
@login_required(["admin"])
def list_b2b_organizations():
    with db() as connection:
        rows = connection.execute(
            "SELECT * FROM b2b_organizations ORDER BY created_at DESC"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.get("/api/agent/history")
@login_required(["admin", "sales", "support"])
def agent_history():
    with db() as connection:
        rows = connection.execute(
            "SELECT * FROM business_analysis_history ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/agent/analyze")
@login_required(["admin", "sales", "support"])
def agent_analyze():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "A management question is required."}), 400

    lowered = question.lower()
    with db() as connection:
        products = [dict(row) for row in connection.execute(
            "SELECT id, category, name, specification, unit_price FROM products"
        ).fetchall()]
        orders = [dict(row) for row in connection.execute("SELECT * FROM orders").fetchall()]
        surveys = [dict(row) for row in connection.execute("SELECT * FROM survey_request").fetchall()]
        warranties = connection.execute("SELECT COUNT(*) FROM warranties").fetchone()[0]

    records_considered = len(products) + len(orders) + len(surveys) + warranties
    agents = ["Manager Agent"]
    evidence = []
    recommendations = []

    if any(word in lowered for word in ("sales", "quote", "lead", "conversion", "demand", "margin", "month")):
        agents += ["Sales Agent", "Finance Agent"]
        total_orders = len(orders)
        evidence.append(f"{total_orders} orders are present in the current operational dataset.")
        evidence.append(f"{len(products)} active catalogue products are available for demand analysis.")
        recommendations.append("Segment month-over-month quote conversion before increasing sales spend; historical order volume is insufficient for a trend claim.")
        answer = "The current records do not contain enough dated historical sales to prove that sales decreased this month."
    elif any(word in lowered for word in ("warehouse", "stock", "inventory", "shortage", "reorder")):
        agents += ["Inventory Agent", "Risk Agent"]
        low_stock_product = min(products, key=lambda item: item["unit_price"])["name"]
        evidence.append(f"{len(products)} catalogue items were reviewed for stock context.")
        evidence.append(f"{low_stock_product} is the lowest-priced catalogue proxy, not a measured stock quantity.")
        recommendations.append("Load warehouse-on-hand quantities and reorder points before assigning a shortage to a specific warehouse.")
        answer = "A warehouse shortage cannot be ranked because this dataset does not contain warehouse-level stock quantities."
    elif any(word in lowered for word in ("installation", "installations", "delay", "delivery", "operations")):
        agents += ["Operations Agent", "Risk Agent"]
        pending_surveys = sum(1 for survey in surveys if survey["status"] not in ("Completed", "Approved"))
        evidence.append(f"{pending_surveys} of {len(surveys)} survey requests are not yet completed or approved.")
        evidence.append(f"{len(orders)} operational orders were reviewed for status context.")
        recommendations.append("Review overdue survey and dispatch timestamps; installation resource allocation should use actual commitments and capacity.")
        answer = f"Operations records identify {pending_surveys} survey requests that remain outside the completed/approved states."
    elif any(word in lowered for word in ("customer", "complaint", "service", "retention", "repeat")):
        agents += ["Customer Agent", "Operations Agent"]
        evidence.append(f"{warranties} warranty records and the available service dataset were considered.")
        evidence.append(f"{len(surveys)} customer surveys are present.")
        recommendations.append("Connect complaint ticket dates and ownership to calculate backlog and repeat-contact rates.")
        answer = "The pending complaint count cannot be verified because complaint records are not loaded in the analysis backend."
    elif any(word in lowered for word in ("forecast", "predict", "next month", "demand")):
        agents += ["Sales Agent", "Inventory Agent"]
        evidence.append("No monthly historical demand series is present in the database.")
        recommendations.append("Collect at least several complete monthly periods by product before producing a forecast.")
        answer = "A numeric next-month demand forecast is not available: the required historical time series is insufficient."
    else:
        agents += ["Sales Agent", "Finance Agent", "Inventory Agent", "Customer Agent", "Operations Agent", "Risk Agent"]
        evidence.append(f"{len(orders)} orders, {len(products)} products, and {len(surveys)} survey requests were reviewed.")
        recommendations.append("Specify a KPI such as sales, margin, stock shortage, pending complaints, or delayed installations.")
        answer = "The Manager Agent reviewed the available business records and selected every specialist domain because the question was broad."

    result = {
        "answer": answer,
        "mode": "deterministic backend analysis with rule-based explanation",
        "agents": agents,
        "evidence": evidence,
        "recommendations": recommendations,
        "confidence": "Medium" if records_considered else "Low",
        "records_considered": records_considered,
        "assumptions": [
            "Results use only records stored in SunPower Nexus.",
            "Correlation is not inferred as causation.",
            "A forecast is suppressed when the historical series is insufficient."
        ],
    }
    with db() as connection:
        connection.execute(
            """INSERT INTO business_analysis_history
            (id,question,agent_answer,specialist_agents,records_considered,confidence,created_at)
            VALUES(?,?,?,?,?,?,?)""",
            (uuid.uuid4().hex, question, answer, json.dumps(agents), records_considered, result["confidence"],
             datetime.now().isoformat()),
        )
    return jsonify(result)


@app.get("/api/agent/report.pdf")
@login_required(["admin", "sales", "support"])
def agent_report_pdf():
    with db() as connection:
        recent = connection.execute(
            "SELECT * FROM business_analysis_history ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("SunPower Nexus - Agentic Business Analysis Report", styles["Title"]),
        Paragraph("Evidence is limited to records stored in the application.", styles["BodyText"]),
        Spacer(1, 18),
        Table([["Generated", datetime.now().isoformat()]], colWidths=[525],
              style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eaf4ed"))])),
        Spacer(1, 18),
    ]
    if recent:
        for row in recent[:10]:
            story.append(Paragraph(str(row["question"]), styles["Heading3"]))
            story.append(Paragraph(str(row["agent_answer"]), styles["BodyText"]))
            story.append(Paragraph(
                f"Records considered: {row['records_considered']} | Confidence: {row['confidence']} | "
                f"Time: {row['created_at']}",
                styles["BodyText"],
            ))
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("No management analyses have been stored yet.", styles["BodyText"]))
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="sunpower-nexus-agent-report.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
