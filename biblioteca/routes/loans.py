"""Prestamos blueprint — loan CRUD routes with atomic stock operations."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import mongo
from ..services import loan_service

loans_bp = Blueprint("loans", __name__, template_folder="../templates")


# ── List ────────────────────────────────────────────────────────────────────


@loans_bp.route("/")
@login_required
def listar():
    """List all loans with optional estado filter.

    Query param ``?estado=`` accepts: ``activos``, ``devueltos``, or
    ``todos`` (default).
    """
    filtro = request.args.get("estado", "todos").strip()

    estado_map = {
        "activos": "activo",
        "devueltos": "devuelto",
        "todos": None,
    }

    estado_filter = estado_map.get(filtro, None)
    prestamos = loan_service.listar_prestamos(estado_filter)

    return render_template(
        "prestamos/listar.html",
        prestamos=prestamos,
        filtro_actual=filtro,
    )


# ── Create ──────────────────────────────────────────────────────────────────


@loans_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    """Show create form (GET) or process loan creation (POST)."""
    if request.method == "POST":
        libro_id = request.form.get("libro_id", "").strip()

        if not libro_id:
            flash("Debes seleccionar un libro.", "error")
            return redirect(url_for("loans.crear"))

        prestamo_id, error = loan_service.crear_prestamo(
            str(current_user.get_id()), libro_id
        )

        if error:
            flash(error, "error")
            return redirect(url_for("loans.crear"))

        flash("Préstamo creado exitosamente.", "success")
        return redirect(url_for("loans.listar"))

    # GET: show form — only books with available copies
    libros_disponibles = list(
        mongo.db.libros.find(
            {"ejemplares_disponibles": {"$gt": 0}}
        ).sort("titulo", 1)
    )

    return render_template(
        "prestamos/form.html",
        libros=libros_disponibles,
    )


# ── Return ──────────────────────────────────────────────────────────────────


@loans_bp.route("/<id>/devolver", methods=["POST"])
@login_required
def devolver(id):
    """Return a book by marking the loan as returned.

    Only active loans can be returned. If the loan is already returned,
    the request is rejected with an error flash message.
    """
    prestamo = loan_service.obtener_prestamo(id)
    if not prestamo:
        flash("Préstamo no encontrado.", "error")
        return redirect(url_for("loans.listar"))

    if prestamo.get("estado") != "activo":
        flash("Este préstamo ya fue devuelto.", "error")
        return redirect(url_for("loans.listar"))

    libro_id = str(prestamo["libro_id"])
    success = loan_service.devolver_prestamo(id, libro_id)

    if success:
        flash("Libro devuelto exitosamente.", "success")
    else:
        flash("No se pudo procesar la devolución.", "error")

    return redirect(url_for("loans.listar"))
