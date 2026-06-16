"""Business rules for registration and login.

Routers call this; it owns the rules (unique email, password verification) and uses
the repository for persistence and the security helpers for hashing/tokens.
"""
from app.core import security
from app.models import User
from app.repositories.user_repository import UserRepository


class EmailAlreadyRegistered(Exception):
    """Raised when registering an email that already exists."""


class InvalidCredentials(Exception):
    """Raised when login email/password do not match."""


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, email: str, password: str) -> User:
        if self.users.get_by_email(email) is not None:
            raise EmailAlreadyRegistered(email)
        return self.users.create(email=email, hashed_password=security.hash_password(password))

    def login(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if user is None or not security.verify_password(password, user.hashed_password):
            raise InvalidCredentials()
        return security.create_access_token(subject=str(user.id))
