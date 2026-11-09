"""Best-effort Redis connection and token revocation."""
import logging
import time
from typing import Any
from redis import Redis
from redis.exceptions import RedisError
from app.core.config import settings

logger = logging.getLogger(__name__)
_client: Redis | None = None


def get_redis() -> Redis | None:
    global _client
    try:
        if _client is None:
            _client = Redis.from_url(settings.REDIS_URL, decode_responses=True,
                                     socket_connect_timeout=settings.REDIS_TIMEOUT_SECONDS,
                                     socket_timeout=settings.REDIS_TIMEOUT_SECONDS)
        _client.ping()
        return _client
    except RedisError:
        logger.warning("Redis non disponibile: revoca e rate limiting degradati")
        return None


def is_blacklisted(payload: dict[str, Any]) -> bool:
    client = get_redis()
    if client is None:
        return False
    try:
        return bool(client.exists(f"blacklist:{payload.get('jti')}"))
    except RedisError:
        logger.warning("Verifica revoca non disponibile")
        return False


def revoke_token(payload: dict[str, Any]) -> None:
    client = get_redis()
    ttl = max(0, int(payload["exp"] - time.time()))
    if client is None or ttl == 0:
        return
    try:
        client.setex(f"blacklist:{payload['jti']}", ttl, "1")
    except RedisError:
        logger.warning("Revoca token non disponibile")
