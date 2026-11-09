from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings
from app.services.audit import AuditService


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        prefix = settings.API_V1_STR + "/"
        path = request.url.path
        parts = path[len(prefix):].strip("/").split("/") if path.startswith(prefix) else []
        resource = parts[0] if parts else ""
        track = bool(parts) and (
            resource in {"medical", "workers", "documents", "attendance"}
            or request.method in {"POST", "PUT", "PATCH", "DELETE"}
            or (resource == "auth" and len(parts) > 1 and parts[1] in {"login", "logout"}))
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            if track:
                resource_id = next((int(part) for part in parts[1:] if part.isdecimal() and len(part) < 10), None)
                AuditService.log(user_id=getattr(request.state, "user_id", None), action=request.method,
                    resource_type=resource, resource_id=resource_id, path=path[:2048],
                    ip_address=request.client.host[:45] if request.client else None,
                    user_agent=request.headers.get("user-agent", "")[:512], status_code=status_code)
