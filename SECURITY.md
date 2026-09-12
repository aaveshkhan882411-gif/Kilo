# Security

## Defense in Depth

GrowthAI implements security at multiple layers:

### Application Layer
- Secure cookies (HTTPOnly, SameSite, Secure in production)
- Server-side authorization enforced on all routes
- Role-based access control (RBAC): OWNER, ADMIN, MANAGER, AGENT, VIEWER
- CSRF protection where applicable
- CORS policy restricting origins
- Content Security Policy (CSP)
- HSTS in production
- Rate limiting per IP+path
- Input validation on all endpoints

### Data Layer
- Tenant isolation: every query scoped by organization ID
- Password hashing with bcrypt
- JWT tokens with expiration
- Audit logging for all sensitive actions
- No secrets in source code
- Environment variables for all credentials

### Integration Layer
- Webhook signature verification
- Payment verification server-side (never trust browser)
- SSRF protection on website analysis
- Replay protection on webhooks
- Idempotency keys on payments
- Clean NOT_CONFIGURED states for missing credentials

### Infrastructure
- PostgreSQL for durable storage
- Redis for cache and rate limiting
- Celery for durable async processing
- Structured logging
- Health checks

## What We Don't Do
- We never claim "unhackable"
- We never expose secrets
- We never bypass authorization
- We never trust browser-side payment success
- We never fake production credentials
