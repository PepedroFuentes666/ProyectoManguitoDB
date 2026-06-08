"""Authentication blueprint — login, logout, and minimal registration."""

from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import bcrypt, mongo
from ..services.auth_service import autenticar

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Render login form (GET) or validate credentials (POST)."""
    if current_user.is_authenticated:
        return redirect(url_for("books.listar"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = autenticar(email, password)
        if user:
            login_user(user)
            flash("Inicio de sesión exitoso. ¡Bienvenido!", "success")
            return redirect(url_for("books.listar"))

        flash("Email o contraseña incorrectos.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user and redirect to login."""
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["POST"])
def register():
    """Minimal registration endpoint — not linked from UI, for seed/admin use."""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    nombre = request.form.get("nombre", "").strip()

    if not email or not password or not nombre:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("auth.login"))

    existing = mongo.db.usuarios.find_one({"email": email})
    if existing:
        flash("El email ya está registrado.", "error")
        return redirect(url_for("auth.login"))

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    mongo.db.usuarios.insert_one({
        "email": email,
        "nombre": nombre,
        "password_hash": password_hash,
        "fecha_creacion": datetime.utcnow(),
    })

    flash("Usuario registrado exitosamente.", "success")
    return redirect(url_for("auth.login"))
