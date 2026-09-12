# Deployment

## Production Deployment

### Prerequisites
- PostgreSQL database
- Redis instance
- Python 3.10+
- Node.js 18+ (for frontend)
- Optional: vLLM GPU server for production AI

### Environment Variables

See `.env.example` for all required variables.

### Backend Deployment

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Worker Deployment

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend Deployment

```bash
cd frontend
npm install
npm run build
npm start
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

### Health Check

```bash
curl https://yourdomain.com/health
```

### Graceful Shutdown

Send SIGTERM to the uvicorn process. The lifespan handler will close database connections.

### Rollback

1. Revert to previous git commit
2. Run database migrations if needed
3. Restart services
