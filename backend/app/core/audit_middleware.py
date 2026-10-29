"""Metadata-only access logging, including failed authentication."""
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool
from app.core.rate_limit import client_ip
from app.services.audit import AuditService


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        parts = request.url.path.strip('/').split('/')
        resource = parts[2] if len(parts) > 2 else ''
        tracked = request.url.path.startswith('/api/v1/') and (
            resource in ('medical', 'workers', 'documents', 'attendance')
            or request.method in ('POST', 'PUT', 'PATCH', 'DELETE')
            or request.url.path.rstrip('/') in ('/api/v1/auth/login', '/api/v1/auth/logout')
        )
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            if tracked:
                resource_id = next((int(part) for part in parts[3:] if part.isdecimal()), None)
                await run_in_threadpool(AuditService.log,
                    user_id=getattr(request.state, 'user_id', None), action=request.method,
                    resource_type=resource, resource_id=resource_id,
                    path=request.url.path, ip_address=client_ip(request),
                    user_agent=request.headers.get('user-agent', ''), status_code=status_code)
