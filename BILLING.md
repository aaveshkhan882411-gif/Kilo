# Billing

## Plans

| Plan | Monthly | Annual | Agents |
|------|---------|--------|--------|
| Standard | $1,999 | Configurable | 4 |
| Premium | $2,999 | $35,000 | 7 |
| Enterprise | $3,999 | $45,000 | 13 |
| Autonomous | Custom | Custom | 20 |

## Membership
- $150/month
- $700/6 months
- $1,000/year

## PayPal Flow

1. Customer selects plan
2. Server creates PayPal order
3. Customer approves in PayPal
4. Server captures order
5. Webhook confirms payment
6. Entitlement activated

## Important Notes
- Server ALWAYS verifies payment via capture API
- Never trust browser success
- Webhook URL must be registered in PayPal
- Idempotency keys prevent duplicate charges
