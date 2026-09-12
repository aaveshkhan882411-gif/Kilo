from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import redis.asyncio as redis
from app.config import settings

_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        key = f"rate:{request.client.host}:{request.url.path}"
        current = await _client.incr(key)
        if current == 1:
            await _client.expire(key, settings.RATE_LIMIT_WINDOW)
        if current > settings.RATE_LIMIT_MAX_REQUESTS:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        return await call_next(request)
