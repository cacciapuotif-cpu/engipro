"""Password policy and safe bootstrap tests."""
from unittest.mock import MagicMock, patch
import pytest
from app.core.security import validate_password
from app.core.config import settings
from scripts.seed import seed


@pytest.mark.parametrize(('password', 'message'), [
    ('Aa1!', 'almeno 10'),
    ('lowercase123!', 'maiuscola'),
    ('UPPERCASE123!', 'minuscola'),
    ('PasswordOnly!', 'cifra'),
    ('Password1234', 'speciale'),
    ('A' * 129, 'al massimo'),
])
def test_password_missing(password: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_password(password)


def test_valid_password() -> None:
    assert validate_password('ValidPassword123!') is True


def test_seed_requires_password_in_production(monkeypatch) -> None:
    monkeypatch.setattr(settings, 'ENV', 'production')
    monkeypatch.setattr(settings, 'ADMIN_INITIAL_PASSWORD', None)
    with patch('scripts.seed.SessionLocal') as factory:
        factory.return_value.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match='ADMIN_INITIAL_PASSWORD'):
            seed()
        factory.return_value.add.assert_not_called()
        factory.return_value.close.assert_called_once()


def test_seed_validates_password(monkeypatch) -> None:
    monkeypatch.setattr(settings, 'ADMIN_INITIAL_PASSWORD', 'weak')
    with patch('scripts.seed.SessionLocal') as factory:
        factory.return_value.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError):
            seed()
        factory.return_value.add.assert_not_called()
