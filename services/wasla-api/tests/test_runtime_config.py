import pytest

from wasla_api.main import validate_runtime_configuration
from wasla_api.routes.auth import _registration_role


def _production_environment(monkeypatch, **overrides):
    values = {
        "APP_ENV": "production",
        "DATABASE_URL": (
            "postgresql+psycopg://wasla:secret@db.wasla.com/wasla?sslmode=require"
        ),
        "JWT_SECRET": "a-production-secret-with-at-least-32-characters",
        "AUTO_CREATE_SCHEMA": "false",
        "CORS_ORIGINS": "https://app.wasla.com",
    }
    values.update(overrides)
    for key in ("APP_ENV", "DATABASE_URL", "JWT_SECRET", "AUTO_CREATE_SCHEMA",
                "CORS_ORIGINS", "OPERATOR_EMAILS"):
        monkeypatch.delenv(key, raising=False)
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_local_runtime_defaults_remain_available(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    validate_runtime_configuration()


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"DATABASE_URL": ""}, "DATABASE_URL"),
        ({"DATABASE_URL": "sqlite:///./wasla.db"}, "DATABASE_URL"),
        (
            {"DATABASE_URL": "postgresql+psycopg://wasla:secret@db.example.test/wasla"},
            "sslmode",
        ),
        ({"JWT_SECRET": "too-short"}, "JWT_SECRET"),
        (
            {"JWT_SECRET": "replace-this-with-a-random-local-secret-at-least-32-chars"},
            "JWT_SECRET",
        ),
        ({"AUTO_CREATE_SCHEMA": "true"}, "AUTO_CREATE_SCHEMA"),
        ({"CORS_ORIGINS": ""}, "CORS_ORIGINS"),
        ({"CORS_ORIGINS": "http://app.wasla.com"}, "HTTPS"),
        ({"CORS_ORIGINS": "https://localhost:5173"}, "HTTPS"),
        ({"CORS_ORIGINS": "https://10.1.1.2"}, "HTTPS"),
        ({"CORS_ORIGINS": "https://service.internal"}, "HTTPS"),
        ({"CORS_ORIGINS": "https://*.wasla.com"}, "HTTPS"),
        ({"OPERATOR_EMAILS": "ops@example.test"}, "OPERATOR_EMAILS"),
    ],
)
def test_production_rejects_unsafe_or_missing_configuration(monkeypatch, overrides, message):
    _production_environment(monkeypatch, **overrides)
    with pytest.raises(RuntimeError, match=message):
        validate_runtime_configuration()


def test_production_accepts_explicit_safe_configuration(monkeypatch):
    _production_environment(monkeypatch)
    validate_runtime_configuration()


def test_unknown_runtime_environment_is_rejected(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prodution")
    with pytest.raises(RuntimeError, match="APP_ENV"):
        validate_runtime_configuration()


def test_missing_runtime_environment_is_rejected(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    with pytest.raises(RuntimeError, match="APP_ENV"):
        validate_runtime_configuration()


def test_operator_allowlist_only_applies_in_development(monkeypatch):
    monkeypatch.setenv("OPERATOR_EMAILS", "ops@example.test")
    monkeypatch.setenv("APP_ENV", "production")
    assert _registration_role("ops@example.test") == "customer"


def test_development_operator_allowlist_remains_available(monkeypatch):
    monkeypatch.setenv("OPERATOR_EMAILS", "ops@example.test")
    monkeypatch.setenv("APP_ENV", "development")
    assert _registration_role("ops@example.test") == "operator"


def test_operator_allowlist_does_not_apply_when_environment_is_missing(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setenv("OPERATOR_EMAILS", "ops@example.test")
    assert _registration_role("ops@example.test") == "customer"
