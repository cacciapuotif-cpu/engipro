"""Fixed-window Redis rate limiting; forwarding trusted only from explicit peers."""
import logging
import time
from ipaddress import ip_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from redis.exceptions import RedisError
from app.core import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path.rstrip("/")
        if not path.startswith("/api/"):
            return await call_next(request)
        client = redis_client.get_redis()
        if client is None:
            return await call_next(request)
        peer = request.client.host if request.client else "unknown"
        address = peer
        if peer in settings.TRUSTED_PROXY_IPS:
            # Nginx appends the actual peer: the last entry cannot be spoofed by the caller.
            forwarded = request.headers.get("x-forwarded-for", "").split(",")[-1].strip()
            try:
                address = str(ip_address(forwarded))
            except ValueError:
                pass
        auth = path in (f"{settings.API_V1_STR}/auth/login", f"{settings.API_V1_STR}/auth/register")
        limit = settings.RATE_LIMIT_AUTH_REQUESTS if auth else settings.RATE_LIMIT_REQUESTS
        period = settings.RATE_LIMIT_PERIOD_SECONDS
        now = int(time.time())
        retry = period - now % period
        key = f"rate:{'auth' if auth else 'api'}:{address}:{now // period}"
        try:
            # Transaction prevents a process crash between increment and expiry.
            with client.pipeline(transaction=True) as pipe:
                count, _ = pipe.incr(key).expire(key, retry).execute()
            if count > limit:
                return JSONResponse({"detail": "Troppe richieste"}, status_code=429,
                                    headers={"Retry-After": str(retry)})
        except RedisError:
            logger.warning("Rate limiting non disponibile")
        return await call_next(request)
