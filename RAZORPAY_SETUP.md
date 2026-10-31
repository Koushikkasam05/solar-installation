# Razorpay Integration Setup

SunPower Nexus uses Razorpay Standard Checkout. Credentials are read only from server environment variables:

```powershell
$env:RAZORPAY_KEY_ID = "rzp_test_..."
$env:RAZORPAY_KEY_SECRET = "..."
$env:RAZORPAY_WEBHOOK_SECRET = "..."
$env:RAZORPAY_MODE = "test"
python app.py
```

Never commit secrets. Use a separate live merchant account for live credentials.

## Webhook

Register this HTTPS endpoint with Razorpay:

`https://your-domain.example/api/payments/webhook`

Enable:

- `payment.captured`
- `payment.failed`
- `order.paid`

The server verifies Razorpay's raw-body `X-Razorpay-Signature` before processing events and stores provider event IDs to prevent duplicate processing.

## Workflow

Approved quotations use a trusted 50% advance milestone. Captured payments unlock warehouse dispatch. The final milestone is available only after advance capture.

## Test Mode Limitation

Checkout and refunds execute only when valid Razorpay Test credentials are configured. Without credentials the API returns service-unavailable responses. Live payments require actual merchant credentials, a production webhook URL, account-specific payment-method verification, and live checkout testing.
