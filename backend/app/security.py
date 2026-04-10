from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; connect-src 'self' http://127.0.0.1:8000 http://localhost:8000;"
            " style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:;"
            " font-src 'self'; object-src 'none'; frame-ancestors 'none';"
        )
        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_host = request.client.host if request.client else "unknown"
        now = time.monotonic()
        request_times = self.requests[client_host]

        while request_times and now - request_times[0] > self.window_seconds:
            request_times.popleft()

        if len(request_times) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        request_times.append(now)
        return await call_next(request)
