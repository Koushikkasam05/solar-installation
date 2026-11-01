from pathlib import Path

import os
import sqlite3
import uuid
import json
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO

from flask import Flask, jsonify, redirect, request, send_file, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import secrets
import hmac
import hashlib
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

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
RAZORPAY_MODE = os.getenv("RAZORPAY_MODE", "test").lower()


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
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
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
            customer_user_id INTEGER,
            status TEXT NOT NULL DEFAULT 'Draft',
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
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id TEXT PRIMARY KEY,
            quotation_id TEXT NOT NULL,
            quotation_version INTEGER NOT NULL,
            customer_user_id INTEGER NOT NULL,
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            amount_paise INTEGER NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            purpose TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'created',
            method TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            captured_at TEXT,
            provider_error TEXT,
            UNIQUE(quotation_id, purpose, quotation_version)
        );
        CREATE TABLE IF NOT EXISTS payment_refunds (
            id TEXT PRIMARY KEY,
            payment_transaction_id TEXT NOT NULL,
            razorpay_refund_id TEXT,
            amount_paise INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'created',
            initiated_by INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS payment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_event_id TEXT NOT NULL UNIQUE,
            event_type TEXT NOT NULL,
            raw_body TEXT NOT NULL,
            processed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS payment_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_transaction_id TEXT,
            action TEXT NOT NULL,
            actor_user_id INTEGER NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        quote_columns = {row["name"] for row in connection.execute("PRAGMA table_info(quotation)")}
        if "customer_user_id" not in quote_columns:
            connection.execute("ALTER TABLE quotation ADD COLUMN customer_user_id INTEGER")
        if "status" not in quote_columns:
            connection.execute("ALTER TABLE quotation ADD COLUMN status TEXT NOT NULL DEFAULT 'Draft'")
        user_columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)")}
        if "account_type" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN account_type TEXT NOT NULL DEFAULT 'customer'")
        if "email_verified" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 1")
        organization_columns = {row["name"] for row in connection.execute("PRAGMA table_info(b2b_organizations)")}
        if "email_verified" not in organization_columns:
            connection.execute("ALTER TABLE b2b_organizations ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")
        if "verification_code_hash" not in organization_columns:
            connection.execute("ALTER TABLE b2b_organizations ADD COLUMN verification_code_hash TEXT")
        if "discount_percent" not in organization_columns:
            connection.execute("ALTER TABLE b2b_organizations ADD COLUMN discount_percent REAL NOT NULL DEFAULT 5")
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
            ("finance@sunpower.local", "Demo Finance", "finance"),
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
            "SELECT id, email, name, role, approved, account_type, email_verified FROM users WHERE id=? AND approved=1",
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
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.path in {
        "/api/auth/login", "/api/auth/register", "/api/auth/forgot-password", "/api/auth/reset-password"
    }:
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


@app.route("/api/auth/logout", methods=["GET", "POST"])
def auth_logout():
    session.clear()
    if request.method == "GET":
        return redirect("/")
    return jsonify({"ok": True})


@app.post("/api/auth/register")
def auth_register():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    account_type = str(payload.get("accountType", "customer")).strip().lower()
    organization_name = str(payload.get("organizationName", "")).strip()
    if account_type not in {"customer", "b2b"}:
        account_type = "customer"
    if account_type == "b2b" and len(organization_name) < 2:
        return jsonify({"error": "Organization name is required for a B2B account."}), 400

    if len(name) < 2:
        return jsonify({"error": "Please enter your full name."}), 400
    if len(email) < 5 or "@" not in email or "." not in email:
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    with db() as connection:
        if connection.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            return jsonify({"error": "An account already exists for this email."}), 409
        connection.execute(
            """INSERT INTO users(email, name, password_hash, role, approved, account_type, email_verified, created_at)
               VALUES(?, ?, ?, 'customer', 1, ?, 0, ?)""",
            (email, name, generate_password_hash(password), account_type, datetime.now().isoformat()),
        )
        user_id = connection.execute(
            "SELECT id FROM users WHERE email=?", (email,)
        ).fetchone()["id"]
        verification_code = None
        if account_type == "b2b":
            verification_code = str(secrets.randbelow(900000) + 100000)
            connection.execute(
                """INSERT INTO b2b_organizations
                   (id, organization_name, business_type, contact_person, business_email, phone,
                    registered_address, gstin, documents_json, approval_status, email_verified,
                    verification_code_hash, discount_percent, created_at)
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 5, ?)""",
                (uuid.uuid4().hex, organization_name, "Business organization", name, email, "",
                 "", payload.get("gstin", ""), "[]", "Pending approval",
                 hashlib.sha256(verification_code.encode()).hexdigest(), datetime.now().isoformat()),
            )
    session["user_id"] = user_id
    session["csrf_token"] = secrets.token_urlsafe(32)
    return jsonify({
        "message": "Account created successfully.",
        "csrfToken": session["csrf_token"],
        "user": {"email": email, "name": name, "role": "customer"},
        "accountType": account_type,
        "emailVerificationRequired": account_type == "b2b",
        "demoVerificationCode": verification_code if account_type == "b2b" and os.getenv("SUNPOWER_DEMO_EMAIL_VERIFY", "0") == "1" else None,
    }), 201


@app.post("/api/auth/forgot-password")
def auth_forgot_password():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    with db() as connection:
        user = connection.execute(
            "SELECT id FROM users WHERE email=? AND approved=1", (email,)
        ).fetchone()
        reset_code = None
        if user:
            connection.execute(
                "UPDATE password_reset_tokens SET used=1 WHERE user_id=? AND used=0",
                (user["id"],),
            )
            reset_code = secrets.token_urlsafe(24)
            connection.execute(
                """INSERT INTO password_reset_tokens(user_id, token_hash, expires_at, created_at)
                   VALUES(?, ?, ?, ?)""",
                (user["id"], hashlib.sha256(reset_code.encode()).hexdigest(),
                 (datetime.now() + timedelta(minutes=30)).isoformat(),
                 datetime.now().isoformat()),
            )

    response = {"message": "If an account exists for that email, password reset instructions are ready."}
    if reset_code and os.getenv("SUNPOWER_DEMO_RESET", "0") == "1":
        response["demoResetCode"] = reset_code
    return jsonify(response)


@app.post("/api/auth/reset-password")
def auth_reset_password():
    payload = request.get_json(silent=True) or {}
    reset_code = str(payload.get("code", "")).strip()
    password = str(payload.get("password", ""))
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if not reset_code:
        return jsonify({"error": "Reset code is required."}), 400

    token_hash = hashlib.sha256(reset_code.encode()).hexdigest()
    with db() as connection:
        token = connection.execute(
            """SELECT id, user_id, expires_at FROM password_reset_tokens
               WHERE token_hash=? AND used=0""", (token_hash,)
        ).fetchone()
        if not token or datetime.fromisoformat(token["expires_at"]) < datetime.now():
            return jsonify({"error": "Reset code is invalid or has expired."}), 400
        connection.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (generate_password_hash(password), token["user_id"]),
        )
        connection.execute("UPDATE password_reset_tokens SET used=1 WHERE id=?", (token["id"],))
    return jsonify({"message": "Password updated successfully. You can sign in now."})


@app.get("/api/auth/me")
def auth_me():
    user = current_user()
    if user is None:
        return jsonify({"authenticated": False}), 401
    user_data = dict(user)
    user_data["business"] = None
    if user["account_type"] == "b2b":
        with db() as connection:
            business = connection.execute(
                """SELECT organization_name, email_verified, approval_status, discount_percent
                   FROM b2b_organizations WHERE business_email=?""",
                (user["email"],),
            ).fetchone()
        if business:
            user_data["business"] = dict(business)
    return jsonify({"authenticated": True, "user": user_data})


@app.post("/api/b2b/email/request-code")
@login_required()
def request_b2b_verification_code():
    user = current_user()
    if user["account_type"] != "b2b":
        return jsonify({"error": "Email verification is only required for B2B accounts."}), 400
    verification_code = str(secrets.randbelow(900000) + 100000)
    verification_hash = hashlib.sha256(verification_code.encode()).hexdigest()
    with db() as connection:
        connection.execute(
            "UPDATE b2b_organizations SET verification_code_hash=? WHERE business_email=?",
            (verification_hash, user["email"]),
        )
    response = {"message": "A verification code has been generated for your business email."}
    if os.getenv("SUNPOWER_DEMO_EMAIL_VERIFY", "0") == "1":
        response["demoVerificationCode"] = verification_code
    return jsonify(response)


@app.post("/api/b2b/email/verify")
@login_required()
def verify_b2b_email():
    payload = request.get_json(silent=True) or {}
    code = str(payload.get("code", "")).strip()
    if not code:
        return jsonify({"error": "Verification code is required."}), 400
    user = current_user()
    token_hash = hashlib.sha256(code.encode()).hexdigest()
    with db() as connection:
        organization = connection.execute(
            "SELECT id FROM b2b_organizations WHERE business_email=? AND verification_code_hash=?",
            (user["email"], token_hash),
        ).fetchone()
        if organization is None:
            return jsonify({"error": "Verification code is invalid or expired."}), 400
        connection.execute(
            "UPDATE b2b_organizations SET email_verified=1, verification_code_hash=NULL WHERE id=?",
            (organization["id"],),
        )
        connection.execute(
            "UPDATE users SET email_verified=1 WHERE id=?", (user["id"],)
        )
    return jsonify({"message": "Business email verified successfully.", "verified": True})


def razorpay_configured():
    return bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and RAZORPAY_MODE in {"test", "live"})


def razorpay_api(method, path, payload=None):
    import base64
    import urllib.request
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    credentials = base64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}
    request_object = urllib.request.Request(
        f"https://api.razorpay.com/v1{path}", data=body, headers=headers, method=method
    )
    with urllib.request.urlopen(request_object, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def captured_amount(connection, quotation_id, purpose=None):
    sql = "SELECT COALESCE(SUM(amount_paise), 0) FROM payment_transactions WHERE quotation_id=? AND status='captured'"
    params = [quotation_id]
    if purpose:
        sql += " AND purpose=?"
        params.append(purpose)
    return connection.execute(sql, params).fetchone()[0]


def advance_satisfied(connection, quotation_id):
    quote = connection.execute("SELECT calculation_json FROM quotation WHERE id=?", (quotation_id,)).fetchone()
    if not quote:
        return False
    amount_paise = int(Decimal(str(json.loads(quote["calculation_json"])["final_amount"])) * 100)
    paid_paise = captured_amount(connection, quotation_id, "advance")
    return paid_paise >= (amount_paise + 1) // 2


def update_payment_workflow(connection, quotation_id):
    satisfied = advance_satisfied(connection, quotation_id)
    if satisfied:
        connection.execute(
            "UPDATE orders SET evidence_json=?, updated_at=? WHERE quotation_id=? AND status NOT IN ('completed')",
            (json.dumps({"advance_payment_satisfied": True}), datetime.now().isoformat(), quotation_id),
        )
    return satisfied


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
            "INSERT INTO quotation(id,number,version,parent_id,customer_name,customer_details,input_json,calculation_json,customer_user_id,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (quote_id, number, version, parent_id, payload.get("customer_name", "Walk-in Customer"),
             payload.get("customer_details", ""), __import__("json").dumps(payload),
             __import__("json").dumps(calculation), current_user()["id"] if current_user() else None,
             "Draft", datetime.now().isoformat()),
        )
    return jsonify({"id": quote_id, "number": number, "version": version, "calculation": calculation})


@app.post("/api/quotes/<quote_id>/approve")
@login_required(["customer", "sales", "admin"])
def approve_quote(quote_id):
    with db() as connection:
        quote = connection.execute("SELECT * FROM quotation WHERE id=?", (quote_id,)).fetchone()
        if not quote:
            return jsonify({"error": "Quotation not found"}), 404
        if request.user["role"] != "admin" and quote["customer_user_id"] not in (None, request.user["id"]):
            return jsonify({"error": "Forbidden"}), 403
        connection.execute("UPDATE quotation SET status='Approved' WHERE id=?", (quote_id,))
    return jsonify({"id": quote_id, "status": "Approved"})


@app.get("/api/payments/config")
@login_required(["admin", "sales", "finance", "customer"])
def payment_config():
    return jsonify({
        "mode": RAZORPAY_MODE,
        "keyIdConfigured": bool(RAZORPAY_KEY_ID),
        "keyId": RAZORPAY_KEY_ID,
        "liveReady": RAZORPAY_MODE == "live" and bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and RAZORPAY_WEBHOOK_SECRET),
        "currency": "INR",
    })


@app.get("/api/payments/quotation/<quote_id>/summary")
@login_required(["customer", "sales", "admin"])
def payment_summary(quote_id):
    with db() as connection:
        quote = connection.execute("SELECT * FROM quotation WHERE id=?", (quote_id,)).fetchone()
        if not quote:
            return jsonify({"error": "Quotation not found"}), 404
        if request.user["role"] != "admin" and quote["customer_user_id"] != request.user["id"]:
            return jsonify({"error": "Forbidden"}), 403
        calculation = json.loads(quote["calculation_json"])
        paid = connection.execute(
            "SELECT COALESCE(SUM(amount_paise),0) FROM payment_transactions WHERE quotation_id=? AND status='captured'",
            (quote_id,),
        ).fetchone()[0]
        advance_required = (int(Decimal(str(calculation["final_amount"])) * 100) + 1) // 2
    return jsonify({
        "quotationId": quote["id"],
        "quotationNumber": quote["number"],
        "version": quote["version"],
        "customerName": quote["customer_name"],
        "items": calculation["items"],
        "confirmedAmountPaise": int(Decimal(str(calculation["final_amount"])) * 100),
        "paidPaise": paid,
        "balancePaise": max(0, int(Decimal(str(calculation["final_amount"])) * 100) - paid),
        "advanceRequiredPaise": advance_required,
        "status": quote["status"],
    })


@app.post("/api/payments/orders")
@login_required(["customer"])
def create_payment_order():
    payload = request.get_json(silent=True) or {}
    quotation_id = payload.get("quotationId")
    purpose = payload.get("purpose")
    if purpose not in {"advance", "balance"}:
        return jsonify({"error": "Invalid payment milestone"}), 400
    if not razorpay_configured():
        return jsonify({"error": "Razorpay credentials are not configured for payment creation", "configured": False}), 503
    with db() as connection:
        quote = connection.execute("SELECT * FROM quotation WHERE id=?", (quotation_id,)).fetchone()
        if not quote:
            return jsonify({"error": "Quotation not found"}), 404
        if quote["customer_user_id"] != request.user["id"] or quote["status"] != "Approved":
            return jsonify({"error": "Quotation is not approved for this customer"}), 403
        calculation = json.loads(quote["calculation_json"])
        total_paise = int(Decimal(str(calculation["final_amount"])) * 100)
        paid_paise = captured_amount(connection, quotation_id)
        advance_paise = (total_paise + 1) // 2
        advance_paid = captured_amount(connection, quotation_id, "advance")
        payable_paise = advance_paise if purpose == "advance" else max(0, total_paise - advance_paise)
        if purpose == "advance" and advance_paid >= advance_paise:
            return jsonify({"error": "Advance milestone is already completed"}), 409
        if purpose == "balance" and advance_paid < advance_paise:
            return jsonify({"error": "Advance milestone must be satisfied first"}), 409
        if purpose == "balance":
            balance_paid = captured_amount(connection, quotation_id, "balance")
            payable_paise = max(0, total_paise - advance_paid - balance_paid)
        if payable_paise <= 0:
            return jsonify({"error": "Payment milestone is already completed"}), 409
        existing = connection.execute(
            "SELECT * FROM payment_transactions WHERE quotation_id=? AND purpose=? AND quotation_version=?",
            (quotation_id, purpose, quote["version"]),
        ).fetchone()
        if existing and existing["status"] in {"created", "attempted", "authorized"}:
            return jsonify({
                "transactionId": existing["id"],
                "razorpayOrderId": existing["razorpay_order_id"],
                "keyId": RAZORPAY_KEY_ID,
                "amountPaise": existing["amount_paise"],
                "currency": "INR",
                "mode": RAZORPAY_MODE,
            })
    try:
        receipt = f"{quote['number']}-{purpose}"
        provider = razorpay_api("POST", "/orders", {
            "amount": payable_paise,
            "currency": "INR",
            "receipt": receipt[:40],
            "notes": {"quotationId": quote["id"], "purpose": purpose, "version": quote["version"]},
        })
    except Exception as error:
        return jsonify({"error": "Razorpay order creation failed", "details": str(error)}), 502
    transaction_id = existing["id"] if existing else uuid.uuid4().hex
    now = datetime.now().isoformat()
    with db() as connection:
        if existing:
            connection.execute(
                "UPDATE payment_transactions SET razorpay_order_id=?, amount_paise=?, status='created', updated_at=?, provider_error=NULL WHERE id=?",
                (provider["id"], payable_paise, now, transaction_id),
            )
        else:
            connection.execute(
                """INSERT INTO payment_transactions
                (id,quotation_id,quotation_version,customer_user_id,razorpay_order_id,amount_paise,currency,purpose,status,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (transaction_id, quotation_id, quote["version"], request.user["id"], provider["id"],
                 payable_paise, "INR", purpose, "created", now, now),
            )
    return jsonify({
        "transactionId": transaction_id,
        "razorpayOrderId": provider["id"],
        "keyId": RAZORPAY_KEY_ID,
        "amountPaise": payable_paise,
        "currency": "INR",
        "mode": RAZORPAY_MODE,
    })


@app.post("/api/payments/verify")
@login_required(["customer"])
def verify_payment():
    payload = request.get_json(silent=True) or {}
    razorpay_order_id = payload.get("razorpay_order_id")
    payment_id = payload.get("razorpay_payment_id")
    signature = payload.get("razorpay_signature")
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode("utf-8"),
        f"{razorpay_order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not signature or not hmac.compare_digest(expected, signature):
        return jsonify({"error": "Invalid Razorpay signature"}), 400
    with db() as connection:
        transaction = connection.execute(
            "SELECT * FROM payment_transactions WHERE razorpay_order_id=? AND customer_user_id=?",
            (razorpay_order_id, request.user["id"]),
        ).fetchone()
    if not transaction:
        return jsonify({"error": "Payment transaction not found"}), 404
    try:
        provider_payment = razorpay_api("GET", f"/payments/{payment_id}")
    except Exception as error:
        return jsonify({"error": "Payment could not be verified with Razorpay", "details": str(error)}), 502
    if provider_payment.get("order_id") != razorpay_order_id:
        return jsonify({"error": "Payment does not belong to this Razorpay order"}), 400
    captured = provider_payment.get("status") == "captured"
    now = datetime.now().isoformat()
    with db() as connection:
        connection.execute(
            "UPDATE payment_transactions SET razorpay_payment_id=?, status=?, method=?, updated_at=?, captured_at=? WHERE id=?",
            (payment_id, "captured" if captured else provider_payment.get("status", "attempted"),
             provider_payment.get("method"), now, now if captured else None, transaction["id"]),
        )
        connection.execute(
            "INSERT INTO payment_audit(payment_transaction_id,action,actor_user_id,details,created_at) VALUES(?,?,?,?,?)",
            (transaction["id"], "payment_callback_verified", request.user["id"], json.dumps({"provider_status": provider_payment.get("status")}), now),
        )
        satisfied = update_payment_workflow(connection, transaction["quotation_id"]) if captured else False
    if captured and satisfied:
        notify("warehouse", "Advance payment satisfied", f"Quotation {transaction['quotation_id'][:8]} cleared for dispatch.")
        notify("sales", "Advance payment received", f"Quotation {transaction['quotation_id'][:8]} advance is satisfied.")
    return jsonify({"status": "captured" if captured else provider_payment.get("status"), "advanceSatisfied": satisfied})


@app.post("/api/payments/webhook")
def razorpay_webhook():
    raw_body = request.get_data(cache=False)
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not RAZORPAY_WEBHOOK_SECRET:
        return jsonify({"error": "Webhook secret is not configured"}), 503
    expected = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return jsonify({"error": "Invalid webhook signature"}), 400
    payload = json.loads(raw_body.decode("utf-8"))
    event_id = payload.get("event_id") or payload.get("id")
    event_type = payload["event"]
    if not event_id or not isinstance(event_id, str):
        return jsonify({"error": "Webhook event ID is required"}), 400
    with db() as connection:
        if connection.execute("SELECT 1 FROM payment_events WHERE provider_event_id=?", (event_id,)).fetchone():
            return jsonify({"received": True, "duplicate": True})
        connection.execute(
            "INSERT INTO payment_events(provider_event_id,event_type,raw_body,processed_at) VALUES(?,?,?,?)",
            (event_id, event_type, raw_body.decode("utf-8"), datetime.now().isoformat()),
        )
        entity = payload.get("payload", {}).get("payment", {}).get("entity")
        if not entity and payload.get("payload", {}).get("order", {}):
            entity = payload["payload"]["order"]["entity"]
        provider_order_id = entity.get("order_id") if entity and entity.get("entity") == "payment" else (
            entity.get("id") if entity and entity.get("entity") == "order" else None
        )
        payment_id = entity.get("id") if entity and entity.get("entity") == "payment" else None
        provider_status = entity.get("status") if entity else None
        if provider_order_id:
            transaction = connection.execute(
                "SELECT * FROM payment_transactions WHERE razorpay_order_id=?", (provider_order_id,)
            ).fetchone()
        elif entity and entity.get("receipt"):
            transaction = connection.execute(
                "SELECT * FROM payment_transactions WHERE razorpay_order_id=?", (entity.get("receipt"),)
            ).fetchone()
        else:
            transaction = None
        if transaction:
            status = "captured" if event_type in {"payment.captured", "order.paid"} else (
                "failed" if event_type == "payment.failed" else provider_status or transaction["status"]
            )
            connection.execute(
                "UPDATE payment_transactions SET razorpay_payment_id=COALESCE(?,razorpay_payment_id), status=?, method=COALESCE(method,?,method), updated_at=?, captured_at=CASE WHEN ?='captured' THEN COALESCE(captured_at,?) ELSE captured_at END WHERE id=?",
                (payment_id, status, entity.get("method") if entity else None, datetime.now().isoformat(),
                 status, datetime.now().isoformat(), transaction["id"]),
            )
            if status == "captured":
                satisfied = update_payment_workflow(connection, transaction["quotation_id"])
                if satisfied:
                    notify("warehouse", "Advance payment satisfied", f"Quotation {transaction['quotation_id'][:8]} cleared for dispatch.")
                    notify("sales", "Advance payment received", f"Quotation {transaction['quotation_id'][:8]} advance is satisfied.")
    return jsonify({"received": True})


@app.get("/api/payments/history")
@login_required(["customer"])
def payment_history():
    with db() as connection:
        rows = connection.execute(
            "SELECT * FROM payment_transactions WHERE customer_user_id=? ORDER BY created_at DESC",
            (request.user["id"],),
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.get("/api/payments/<transaction_id>/receipt.pdf")
@login_required(["customer", "admin", "finance"])
def payment_receipt(transaction_id):
    with db() as connection:
        payment = connection.execute("SELECT * FROM payment_transactions WHERE id=?", (transaction_id,)).fetchone()
        if not payment or request.user["role"] == "customer" and payment["customer_user_id"] != request.user["id"]:
            return jsonify({"error": "Payment not found"}), 404
        quote = connection.execute("SELECT * FROM quotation WHERE id=?", (payment["quotation_id"],)).fetchone()
    if payment["status"] != "captured":
        return jsonify({"error": "A captured payment is required for a receipt"}), 409
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("SunPower Nexus - Payment Receipt", styles["Title"]),
        Paragraph(f"Receipt for {quote['number']} v{payment['quotation_version']}", styles["Heading2"]),
        Spacer(1, 16),
        Table([
            ["Payment ID", payment["razorpay_payment_id"] or "Pending"],
            ["Razorpay Order", payment["razorpay_order_id"] or "Pending"],
            ["Customer", quote["customer_name"]],
            ["Purpose", payment["purpose"].title()],
            ["Amount", f"INR {Decimal(payment['amount_paise']) / Decimal(100):.2f}"],
            ["Status", payment["status"].title()],
            ["Captured at", payment["captured_at"] or payment["updated_at"]],
        ], colWidths=[120, 320]),
    ]
    document.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"payment-{transaction_id[:8]}.pdf", mimetype="application/pdf")


@app.post("/api/payments/<transaction_id>/refund")
@login_required(["finance", "admin"])
def refund_payment(transaction_id):
    payload = request.get_json(silent=True) or {}
    amount = Decimal(str(payload.get("amount", 0)))
    reason = str(payload.get("reason", "")).strip()
    if amount <= 0 or not reason:
        return jsonify({"error": "Refund amount and reason are required"}), 400
    with db() as connection:
        payment = connection.execute(
            "SELECT * FROM payment_transactions WHERE id=? AND status='captured'", (transaction_id,)
        ).fetchone()
        if not payment:
            return jsonify({"error": "Captured payment not found"}), 404
        refunded = connection.execute(
            "SELECT COALESCE(SUM(amount_paise),0) FROM payment_refunds WHERE payment_transaction_id=? AND status IN ('processed','created')",
            (transaction_id,),
        ).fetchone()[0]
        amount_paise = int(amount * 100)
        if amount_paise > payment["amount_paise"] - refunded:
            return jsonify({"error": "Refund exceeds the remaining captured amount"}), 400
    if not razorpay_configured():
        return jsonify({"error": "Razorpay credentials are not configured"}), 503
    try:
        provider_refund = razorpay_api("POST", f"/payments/{payment['razorpay_payment_id']}/refund", {
            "amount": amount_paise,
            "notes": {"reason": reason},
        })
    except Exception as error:
        return jsonify({"error": "Razorpay refund failed", "details": str(error)}), 502
    refund_id = uuid.uuid4().hex
    now = datetime.now().isoformat()
    with db() as connection:
        connection.execute(
            """INSERT INTO payment_refunds
            (id,payment_transaction_id,razorpay_refund_id,amount_paise,reason,status,initiated_by,created_at)
            VALUES(?,?,?,?,?,?,?,?)""",
            (refund_id, transaction_id, provider_refund["id"], amount_paise, reason,
             provider_refund.get("status", "processed"), request.user["id"], now),
        )
        connection.execute(
            "INSERT INTO payment_audit(payment_transaction_id,action,actor_user_id,details,created_at) VALUES(?,?,?,?,?)",
            (transaction_id, "refund_initiated", request.user["id"],
             json.dumps({"refundId": provider_refund["id"], "amountPaise": amount_paise, "reason": reason}), now),
        )
    return jsonify({"id": refund_id, "razorpayRefundId": provider_refund["id"], "status": provider_refund.get("status")})


@app.get("/api/payments/admin/summary")
@login_required(["finance", "admin"])
def payment_admin_summary():
    with db() as connection:
        captured = connection.execute(
            "SELECT COALESCE(SUM(amount_paise),0) FROM payment_transactions WHERE status='captured'"
        ).fetchone()[0]
        pending = connection.execute(
            "SELECT COALESCE(SUM(amount_paise),0) FROM payment_transactions WHERE status IN ('created','attempted','authorized')"
        ).fetchone()[0]
        failed = connection.execute(
            "SELECT COALESCE(SUM(amount_paise),0) FROM payment_transactions WHERE status='failed'"
        ).fetchone()[0]
        refunds = connection.execute(
            "SELECT COALESCE(SUM(amount_paise),0) FROM payment_refunds"
        ).fetchone()[0]
        transactions = connection.execute(
            "SELECT * FROM payment_transactions ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    return jsonify({
        "mode": RAZORPAY_MODE,
        "capturedPaise": captured,
        "pendingPaise": pending,
        "failedPaise": failed,
        "refundedPaise": refunds,
        "transactions": [dict(row) for row in transactions],
    })


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
@login_required(["admin", "warehouse", "sales", "technician", "support", "finance", "director", "customer"])
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
        row = connection.execute("SELECT status, quotation_id FROM orders WHERE id=?", (order_id,)).fetchone()
        if not row:
            return jsonify({"error": "Order not found"}), 404
        allowed = ORDER_STATES.get(row["status"], set())
        if target != stage_roles.get(acting_role) or acting_role not in allowed:
            return jsonify({"error": f"Invalid transition from {row['status']} to {target} by {acting_role}"}), 409
        if target == "warehouse_ready" and row["quotation_id"] and not advance_satisfied(connection, row["quotation_id"]):
            return jsonify({"error": "Warehouse dispatch is locked until the 50% advance is captured"}), 409
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
