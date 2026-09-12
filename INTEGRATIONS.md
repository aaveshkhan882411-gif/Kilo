# Integrations

## PayPal

### Setup
1. Create a PayPal Developer account
2. Create a REST API app
3. Copy `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` to `.env`
4. Set `PAYPAL_ENVIRONMENT=sandbox` for testing
5. Create a webhook in PayPal Developer Dashboard
6. Copy webhook ID to `PAYPAL_WEBHOOK_ID`
7. Set webhook URL to: `https://yourdomain.com/api/v1/paypal/webhook`

### Webhook Events
- `payment.completed`
- `payment.failed`
- `subscription.created`
- `subscription.activated`
- `subscription.cancelled`
- `dispute.created`

### Notes
- Server always verifies payment via capture API
- Idempotency keys prevent duplicate processing
- Replay protection via timestamp validation

## Google OAuth

### Setup
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Set authorized redirect URI: `https://yourdomain.com/api/v1/google/callback`
3. Copy `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `.env`

## WhatsApp

### Setup
1. Create a WhatsApp Business Account
2. Get phone number ID and access token
3. Set webhook URL in Meta App Dashboard
4. Copy credentials to `.env`

### Webhook URL
`https://yourdomain.com/api/v1/whatsapp/webhook`

## Email

### Setup
1. Configure SMTP provider (Gmail, SendGrid, etc.)
2. Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
3. Set `SMTP_FROM` and `EMAIL_FROM_NAME`

### Notes
- Email is optional for development
- Clean `NOT_CONFIGURED` state when SMTP is absent
- Supports verification, password reset, notifications

## Voice

### Setup
1. Configure voice provider (Twilio, Deepgram, etc.)
2. Set `VOICE_PROVIDER`, `VOICE_API_KEY`, etc.
3. Clean `NOT_CONFIGURED` state when absent
