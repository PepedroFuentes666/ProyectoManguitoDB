"""Authentication service — login validation against usuarios collection."""

from ..extensions import bcrypt, mongo
from ..models.user import User


def autenticar(email: str, password: str) -> User | None:
    """Authenticate a user by email and bcrypt-hashed password.

    Args:
        email: User email address.
        password: Plaintext password to verify.

    Returns:
        User object on success, or None if credentials are invalid.
    """
    user_doc = mongo.db.usuarios.find_one({"email": email})
    if user_doc is None:
        return None

    if bcrypt.check_password_hash(user_doc["password_hash"], password):
        return User(user_doc)

    return None
