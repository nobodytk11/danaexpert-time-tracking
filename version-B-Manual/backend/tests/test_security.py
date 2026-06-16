"""Unit tests for the security helpers (password hashing + JWT)."""
from app.core import security


def test_password_hash_is_not_plaintext_and_verifies():
    hashed = security.hash_password("s3cret")
    assert hashed != "s3cret"
    assert security.verify_password("s3cret", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = security.hash_password("s3cret")
    assert security.verify_password("wrong", hashed) is False


def test_access_token_round_trips_subject():
    token = security.create_access_token(subject="42")
    assert security.decode_token(token) == "42"


def test_decode_invalid_token_returns_none():
    assert security.decode_token("not-a-real-token") is None
