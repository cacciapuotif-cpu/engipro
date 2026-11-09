from unittest.mock import patch
import pytest
from app.core.security import validate_password
from app.core.config import settings
from scripts.seed import seed


@pytest.mark.parametrize("password,missing", [
    ("Aa1!", "almeno 10"),
    ("lowercase123!", "maiuscola"),
    ("UPPERCASE123!", "minuscola"),
    ("NoDigitsHere!", "cifra"),
    ("NoSpecial123", "speciale"),
    ("Aa1!" * 40, "al massimo"),
])
def test_invalid_password(password: str, missing: str) -> None:
    with pytest.raises(ValueError, match=missing):
        validate_password(password)


def test_valid_password() -> None:
    assert validate_password("ValidPassword123!")


def test_production_seed_requires_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ENV", "production")
    monkeypatch.setattr(settings, "ADMIN_INITIAL_PASSWORD", None)
    with pytest.raises(ValueError, match="obbligatoria"):
        seed()


def test_seed_validates_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ADMIN_INITIAL_PASSWORD", "invalidpassword")
    with patch("scripts.seed.SessionLocal") as factory:
        factory.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="maiuscola"):
            seed()
        factory.return_value.__enter__.return_value.add.assert_not_called()
