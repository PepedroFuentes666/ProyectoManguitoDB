"""Flask application factory for Biblioteca ManguitoDB.

Usage:
    flask --app biblioteca.app:create_app run
    gunicorn biblioteca.app:create_app()
"""

from datetime import datetime

from flask import Flask, redirect, url_for, render_template
from flask_login import login_required, current_user

from .config import Config
from .extensions import login_manager, bcrypt, mongo, init_db


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extensions ---
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login callback: load a user from the session user_id."""
        from .models.user import User

        return User.get_by_id(user_id)

    # --- Blueprints ---
    from .routes.auth import auth_bp
    from .routes.books import books_bp
    from .routes.loans import loans_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(books_bp, url_prefix="/libros")
    app.register_blueprint(loans_bp, url_prefix="/prestamos")

    # --- Template globals ---
    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    # --- Indexes ---
    init_db(app)

    # --- Root route: Dashboard ---
    @app.route("/")
    @login_required
    def index():
        """Render dashboard with library stats."""
        total_libros = mongo.db.libros.count_documents({})
        total_prestamos = mongo.db.prestamos.count_documents({})
        prestamos_activos = mongo.db.prestamos.count_documents(
            {"estado": "activo"}
        )
        return render_template(
            "dashboard.html",
            total_libros=total_libros,
            total_prestamos=total_prestamos,
            prestamos_activos=prestamos_activos,
        )

    return app
