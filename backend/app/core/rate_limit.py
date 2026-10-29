"""Fixed minute windows; only explicitly trusted proxies may supply XFF."""
import ipaddress
import logging
import math
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from redis.exceptions import RedisError
from app.core.config import settings
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def client_ip(request: Request) -> str:
    peer = request.client.host if request.client else 'unknown'
    try:
        address = ipaddress.ip_address(peer)
        trusted = any(address in ipaddress.ip_network(network) for network in settings.TRUSTED_PROXY_NETWORKS)
        # Use the final address appended by our immediate trusted proxy.
        if trusted and request.headers.get('x-forwarded-for'):
            return str(ipaddress.ip_address(request.headers['x-forwarded-for'].split(',')[-1].strip()))
    except ValueError:
        pass
    return peer


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if path.startswith('/api/'):
            client = get_redis()
            if client is not None:
                now = time.time()
                window = settings.RATE_LIMIT_PERIOD_SECONDS
                bucket = int(now // window)
                auth = path.rstrip('/') in ('/api/v1/auth/login', '/api/v1/auth/register')
                limit = settings.AUTH_RATE_LIMIT_REQUESTS if auth else settings.RATE_LIMIT_REQUESTS
                key = f"rate:{'auth' if auth else 'api'}:{client_ip(request)}:{bucket}"
                try:
                    pipeline = client.pipeline(transaction=True)
                    pipeline.incr(key)
                    pipeline.expire(key, window + 1)
                    count = pipeline.execute()[0]
                    if count > limit:
                        return JSONResponse({'detail': 'Troppe richieste'}, status_code=429,
                                            headers={'Retry-After': str(max(1, math.ceil((bucket + 1) * window - now)))})
                except RedisError:
                    logger.warning('Redis non disponibile durante rate limiting', exc_info=True)
        return await call_next(request)
