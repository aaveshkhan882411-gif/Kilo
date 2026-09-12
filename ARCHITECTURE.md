# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                     │
│                     http://localhost:3000                     │
└─────────────────────────────┬─────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                     │
│                     http://localhost:8000                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Auth       │ │   CRM       │ │   Billing   │ │ Admin  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Agents     │ │   AI        │ │   Integrations│ │Health ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────┬─────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │PostgreSQL│   │  Redis   │   │  Celery  │
        │  (PG)    │   │  Cache   │   │  Workers │
        └──────────┘   └──────────┘   └──────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  AI Gateway      │
                    │  ┌────────────┐  │
                    │  │Mock Provider│  │
                    │  └────────────┘  │
                    │  ┌────────────┐  │
                    │  │ vLLM Prov. │  │
                    │  └────────────┘  │
                    │  ┌────────────┐  │
                    │  │  Router    │  │
                    │  └────────────┘  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Integrations     │
                    │ PayPal, Google,  │
                    │ WhatsApp, Email, │
                    │ Voice, Calendar  │
                    └──────────────────┘
```

## Directory Structure

```
backend/
  app/
    main.py              # FastAPI application
    config.py            # Settings
    database.py          # Database connection
    models/              # SQLAlchemy models
    schemas/             # Pydantic schemas
    routers/             # API routes
    services/            # Business logic
    agents/              # AI agent system
    ai/                  # AI Gateway and providers
    integrations/        # External integrations
    workers/             # Celery background tasks
    middleware/          # Security, rate limit, tenant
    auth/                # Authentication utilities
  tests/                 # Test suite
  requirements.txt       # Python dependencies
  .env.example          # Environment template
```

## Core Components

### AI Workforce
20 specialized agents registered in `app/agents/registry.py`, each with machine-readable contracts.

### AI Gateway
Abstraction layer (`app/ai/gateway.py`) supporting MockProvider (development) and VLLMProvider (production).

### Integration Gateway
Centralized adapters for PayPal, Google OAuth, WhatsApp, Email, Voice, Calendar.

### Outcome Engine
State machine tracking: REQUESTED → PLANNED → AUTHORIZED → EXECUTING → EXECUTED → VERIFIED → OUTCOME_RECORDED.

### Action Engine
AI Decision → Action Plan → Permission Check → Tool → Execution → Result → Verification → Outcome.

### GIP
Structured internal event protocol with 20 event types.

## Scalability

- CDN/edge → API/app workers → Redis → queues → PostgreSQL with connection pooling
- Designed for: 1K → 10K → 50K → 100K → 200K → 1M+ → 2M+ users
