from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import async_session_factory
from app.config import settings


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request.state.tenant_id = tenant_id
        return await call_next(request)
