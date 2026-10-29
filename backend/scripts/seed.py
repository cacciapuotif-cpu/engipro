"""
Database seed script — creates the initial admin user.
Run once after first deploy: python -m scripts.seed
"""
import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password, validate_password
from app.core.config import settings
from app.models.user import User, UserRole


logger = logging.getLogger(__name__)


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@engipro.it").first()
        if existing:
            logger.info("Admin già esistente: seed saltato")
            return

        password = settings.ADMIN_INITIAL_PASSWORD
        if not password:
            raise ValueError("Impostare ADMIN_INITIAL_PASSWORD per creare il primo amministratore")
        validate_password(password)

        admin = User(
            email="admin@engipro.it",
            hashed_password=hash_password(password),
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Amministratore iniziale creato")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
