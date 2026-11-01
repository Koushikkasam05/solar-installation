import hashlib
import hmac
import json

import app as solar_app


def login(client, email="customer@sunpower.local"):
    response = client.post("/api/auth/login", json={"email": email, "password": "Solar@123"})
    assert response.status_code == 200
    return response.get_json()["csrfToken"]


def test_payment_webhook_rejects_invalid_signature():
    client = solar_app.app.test_client()
    solar_app.RAZORPAY_WEBHOOK_SECRET = "test-webhook-secret"
    response = client.post(
        "/api/payments/webhook",
        data=b'{"event":"payment.failed","payload":{}}',
        headers={"X-Razorpay-Signature": "invalid"},
    )
    assert response.status_code == 400


def test_payment_webhook_accepts_and_deduplicates_valid_event():
    client = solar_app.app.test_client()
    solar_app.RAZORPAY_WEBHOOK_SECRET = "test-webhook-secret"
    body = json.dumps({
        "event_id": "evt_payment_test_1",
        "event": "payment.failed",
        "payload": {"payment": {"entity": {"id": "pay_unknown", "order_id": "order_unknown", "status": "failed"}}},
    }).encode()
    signature = hmac.new(b"test-webhook-secret", body, hashlib.sha256).hexdigest()
    headers = {"X-Razorpay-Signature": signature, "Content-Type": "application/json"}
    first = client.post("/api/payments/webhook", data=body, headers=headers)
    second = client.post("/api/payments/webhook", data=body, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.get_json()["duplicate"] is True


def test_payment_creation_requires_authentication():
    client = solar_app.app.test_client()
    response = client.post("/api/payments/orders", json={"quotationId": "unknown", "purpose": "balance"})
    assert response.status_code == 401


def test_callback_rejects_invalid_signature():
    client = solar_app.app.test_client()
    csrf = login(client)
    response = client.post(
        "/api/payments/verify",
        json={"razorpay_order_id": "order_tampered", "razorpay_payment_id": "pay_tampered", "razorpay_signature": "bad"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 400


def test_admin_payment_summary_requires_authorized_role():
    client = solar_app.app.test_client()
    login(client)
    response = client.get("/api/payments/admin/summary")
    assert response.status_code == 403
