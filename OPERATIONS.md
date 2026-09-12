# Operations

## Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/api/v1/health/detailed
```

## Monitoring

- Structured JSON logging
- Request failure tracking
- AI failure tracking
- Tool failure tracking
- Webhook failure tracking
- Payment event tracking
- Queue failure tracking
- Integration failure tracking
- Authorization failure tracking
- Agent action tracking
- Outcome tracking

## Backup

### PostgreSQL Backup

```bash
pg_dump -U growthai growthai > backup.sql
```

### Restore

```bash
psql -U growthai growthai < backup.sql
```

## Logs

- Application logs: stdout/stderr
- Celery worker logs: celery worker output
- Database logs: PostgreSQL logs

## Queue

Start Celery worker:

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Scaling

1. Start with single app worker
2. Add more workers behind load balancer
3. Add Redis for caching
4. Add Celery workers for async tasks
5. Add PgBouncer for connection pooling
6. Add read replicas for reporting
7. Add CDN for static assets

## Incident Response

1. Detect issue via monitoring
2. Diagnose root cause
3. Apply fix or rollback
4. Verify resolution
5. Record incident
