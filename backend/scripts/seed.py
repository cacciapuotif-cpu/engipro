"""Create the initial administrator using an explicitly configured password."""
import logging
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password, validate_password
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def seed() -> None:
    password = settings.ADMIN_INITIAL_PASSWORD
    if settings.ENV == "production" and not password:
        raise ValueError("ADMIN_INITIAL_PASSWORD obbligatoria in produzione")
    with SessionLocal() as db:
        if db.query(User).filter(User.email == settings.ADMIN_EMAIL).first():
            logger.info("Admin già presente: seed non necessario")
            return
        if not password:
            raise ValueError("Impostare ADMIN_INITIAL_PASSWORD per creare il primo admin")
        validate_password(password)
        db.add(User(email=settings.ADMIN_EMAIL, hashed_password=hash_password(password),
                    full_name="Administrator", role=UserRole.ADMIN, is_active=True))
        db.commit()
        logger.info("Admin iniziale creato")


if __name__ == "__main__":
    seed()
