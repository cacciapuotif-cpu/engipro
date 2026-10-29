"""Redis availability and best-effort token revocation."""
import logging
import math
import time
from typing import Any
from redis import Redis
from redis.exceptions import RedisError
from app.core.config import settings

logger = logging.getLogger(__name__)
_client: Redis | None = None
_retry_after: float = 0


def get_redis() -> Redis | None:
    global _client, _retry_after
    if time.monotonic() < _retry_after:
        return None
    try:
        if _client is None:
            _client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.2, socket_timeout=0.2)
        _client.ping()
        return _client
    except RedisError:
        logger.warning('Redis non disponibile: revoca e rate limiting temporaneamente disabilitati')
        _retry_after = time.monotonic() + 5
        return None


def is_revoked(payload: dict[str, Any]) -> bool:
    client = get_redis()
    try:
        return bool(client and payload.get('jti') and client.exists(f"blacklist:{payload['jti']}"))
    except RedisError:
        logger.warning('Redis non disponibile durante verifica revoca', exc_info=True)
        return False


def revoke(payload: dict[str, Any]) -> None:
    client = get_redis()
    ttl = math.ceil(float(payload['exp']) - time.time())
    if client is not None and ttl > 0 and payload.get('jti'):
        try:
            client.setex(f"blacklist:{payload['jti']}", ttl, '1')
        except RedisError:
            logger.warning('Redis non disponibile durante logout', exc_info=True)
