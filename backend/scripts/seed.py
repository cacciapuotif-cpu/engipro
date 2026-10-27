"""
Database seed script — creates the initial admin user.
Run once after first deploy: python -m scripts.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@engipro.it").first()
        if existing:
            print("Admin user already exists — skipping seed.")
            return

        admin = User(
            email="admin@engipro.it",
            hashed_password=hash_password("ChangeMe123!"),
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("Admin user created: admin@engipro.it / ChangeMe123!")
        print("IMPORTANT: change the password immediately after first login.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
