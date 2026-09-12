# Database

## Schema

### Core Models
- `organizations` - Tenant organizations
- `users` - User accounts with roles
- `leads` - Lead records
- `contacts` - Contact records
- `companies` - Company records
- `customers` - Customer records
- `deals` - Deal records
- `activities` - Activity records
- `tasks` - Task records
- `appointments` - Appointment records
- `conversations` - Conversation records
- `campaigns` - Campaign records
- `workflows` - Workflow records
- `analytics` - Analytics records
- `outcomes` - Outcome records
- `audit_logs` - Audit log records
- `integrations` - Integration records
- `subscriptions` - Subscription records
- `payments` - Payment records

## Indexes

All tenant-owned tables have indexes on `org_id`.
Composite indexes for common query patterns.

## Migrations

Use Alembic for database migrations.

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Connection Pooling

Production should use PgBouncer for connection pooling.

## Isolation

Every tenant-owned record is isolated by `org_id`. Queries always filter by the current user's organization.
