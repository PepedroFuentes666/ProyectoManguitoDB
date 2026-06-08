"""User model wrapping a usuarios document for Flask-Login."""

from flask_login import UserMixin
from bson.objectid import ObjectId

from ..extensions import mongo


class User(UserMixin):
    """Wrapper around a `usuarios` MongoDB document.

    Usage:
        user = User.get_by_email("demo@demo.com")
        login_user(user)  # Flask-Login
        user.get_id()     # → "507f1f77bcf86cd799439011"
    """

    def __init__(self, user_doc: dict):
        self._doc = user_doc
        self.id = str(user_doc["_id"])
        self.email = user_doc.get("email", "")
        self.nombre = user_doc.get("nombre", "")

    def get_id(self) -> str:
        """Return the user's MongoDB _id as a string (required by Flask-Login)."""
        return self.id

    @staticmethod
    def get_by_id(user_id: str) -> "User | None":
        """Fetch a user by their string _id. Returns None if not found."""
        try:
            doc = mongo.db.usuarios.find_one({"_id": ObjectId(user_id)})
            return User(doc) if doc else None
        except Exception:
            return None

    @staticmethod
    def get_by_email(email: str) -> "User | None":
        """Fetch a user by email. Returns None if not found."""
        doc = mongo.db.usuarios.find_one({"email": email})
        return User(doc) if doc else None
