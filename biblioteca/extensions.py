"""Flask extensions and MongoDB connection management."""

from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from pymongo import ASCENDING, TEXT

login_manager = LoginManager()
bcrypt = Bcrypt()


class _MongoWrapper:
    """Simple wrapper around PyMongo for Flask integration.

    Usage inside app factory:
        mongo.init_app(app)
        mongo.db.usuarios.find_one(...)
    """

    def __init__(self):
        self.client = None
        self._db = None

    def init_app(self, app):
        uri = app.config.get("MONGODB_URI", "mongodb://localhost:27017/biblioteca")
        self.client = MongoClient(uri)
        self._db = self.client.get_database()

    @property
    def db(self):
        if self._db is None:
            raise RuntimeError(
                "Database not initialised. Call mongo.init_app(app) first."
            )
        return self._db


mongo = _MongoWrapper()


def init_db(app):
    """Create indexes on all collections.

    Called once during application startup from the app factory.
    """
    db = mongo.db

    # usuarios: unique email index
    db.usuarios.create_index("email", unique=True)

    # libros: unique ISBN, full-text search on title + author
    db.libros.create_index("isbn", unique=True)
    db.libros.create_index(
        [("titulo", TEXT), ("autor", TEXT)],
        name="text_titulo_autor",
    )

    # prestamos: index for book lookups and active-loan queries
    db.prestamos.create_index("libro_id")
    db.prestamos.create_index(
        [("estado", ASCENDING), ("fecha_prestamo", ASCENDING)],
    )
