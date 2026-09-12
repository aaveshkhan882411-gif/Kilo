# Environment Variables

## Required

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `AUTH_SECRET` | JWT signing secret |
| `PAYPAL_CLIENT_ID` | PayPal client ID (sandbox or live) |
| `PAYPAL_CLIENT_SECRET` | PayPal client secret |
| `PAYPAL_WEBHOOK_ID` | PayPal webhook ID for verification |
| `PAYPAL_ENVIRONMENT` | `sandbox` or `live` |

## Optional

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | WhatsApp business account ID |
| `WHATSAPP_VERIFY_TOKEN` | WhatsApp webhook verify token |
| `SMTP_HOST` | SMTP host |
| `SMTP_PORT` | SMTP port |
| `SMTP_USER` | SMTP username |
| `SMTP_PASSWORD` | SMTP password |
| `SMTP_FROM` | From email address |
| `VOICE_API_KEY` | Voice provider API key |
| `VLLM_BASE_URL` | vLLM inference server URL |
| `VLLM_MODEL` | vLLM model name |

## AI Gateway

| Variable | Description |
|----------|-------------|
| `AI_PROVIDER` | `mock` (development) or `vllm` (production) |
| `VLLM_BASE_URL` | vLLM endpoint URL |
| `VLLM_MODEL` | Model identifier |
| `VLLM_API_KEY` | vLLM API key |

## Application

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | `GrowthAI` |
| `APP_ENV` | Environment | `development` |
| `APP_DEBUG` | Debug mode | `true` |
| `APP_URL` | Application URL | `http://localhost:8000` |
| `FRONTEND_URL` | Frontend URL | `http://localhost:3000` |
| `API_PREFIX` | API prefix | `/api/v1` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |

## Security

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTH_ALGORITHM` | JWT algorithm | `HS256` |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `60` |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `SESSION_COOKIE_SECURE` | Secure cookie flag | `false` (true in production) |
| `SESSION_COOKIE_HTTPONLY` | HTTPOnly flag | `true` |
| `SESSION_COOKIE_SAMESITE` | SameSite attribute | `lax` |
