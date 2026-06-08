"""Libros blueprint — book CRUD routes with search and loan history."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from bson.objectid import ObjectId

from ..extensions import mongo
from ..services import book_service

books_bp = Blueprint("books", __name__, template_folder="../templates")


# ── List / Search ──────────────────────────────────────────────────────────


@books_bp.route("/")
@login_required
def listar():
    """List all books, with optional text search via ``?q=``."""
    q = request.args.get("q", "").strip()
    libros = book_service.buscar_libros(q)
    return render_template("libros/listar.html", libros=libros, q=q)


# ── Create ─────────────────────────────────────────────────────────────────


@books_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    """Show create form (GET) or process creation (POST)."""
    if request.method == "POST":
        libro_id, error = book_service.crear_libro(request.form)
        if error:
            flash(error, "error")
            return render_template(
                "libros/form.html", libro=None, form_data=request.form
            )
        flash("Libro creado exitosamente.", "success")
        return redirect(url_for("books.listar"))

    return render_template("libros/form.html", libro=None, form_data=None)


# ── Edit ───────────────────────────────────────────────────────────────────


@books_bp.route("/<id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    """Show edit form (GET) or process update (POST)."""
    libro = book_service.obtener_libro(id)
    if not libro:
        flash("Libro no encontrado.", "error")
        return redirect(url_for("books.listar"))

    if request.method == "POST":
        try:
            # Check for ISBN conflict *before* calling the service
            new_isbn = request.form.get("isbn", "").strip()
            if new_isbn and new_isbn != libro.get("isbn", ""):
                existing = mongo.db.libros.find_one(
                    {"isbn": new_isbn, "_id": {"$ne": ObjectId(id)}}
                )
                if existing:
                    flash(
                        "El ISBN ingresado ya está en uso por otro libro.",
                        "error",
                    )
                    return render_template(
                        "libros/form.html", libro=libro, form_data=request.form
                    )

            success = book_service.actualizar_libro(id, request.form)
            if success:
                flash("Libro actualizado exitosamente.", "success")
                return redirect(url_for("books.listar"))

            flash("No se pudo actualizar el libro.", "error")
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "error")

        return render_template(
            "libros/form.html", libro=libro, form_data=request.form
        )

    return render_template("libros/form.html", libro=libro, form_data=None)


# ── Delete ─────────────────────────────────────────────────────────────────


@books_bp.route("/<id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    """Delete a book via POST (CSRF-safe — no GET delete)."""
    libro = book_service.obtener_libro(id)
    if not libro:
        flash("Libro no encontrado.", "error")
        return redirect(url_for("books.listar"))

    # Extra safety check before calling service
    active_loans = mongo.db.prestamos.count_documents(
        {"libro_id": ObjectId(id), "estado": "activo"}
    )
    if active_loans > 0:
        flash(
            "No se puede eliminar el libro porque tiene préstamos activos.",
            "error",
        )
        return redirect(url_for("books.detalle", id=id))

    success = book_service.eliminar_libro(id)
    if success:
        flash("Libro eliminado exitosamente.", "success")
    else:
        flash("No se pudo eliminar el libro.", "error")

    return redirect(url_for("books.listar"))


@books_bp.route("/<id>/confirmar-eliminar")
@login_required
def confirmar_eliminar(id):
    """Show delete confirmation page (GET)."""
    libro = book_service.obtener_libro(id)
    if not libro:
        flash("Libro no encontrado.", "error")
        return redirect(url_for("books.listar"))

    active_loans = mongo.db.prestamos.count_documents(
        {"libro_id": ObjectId(id), "estado": "activo"}
    )

    return render_template(
        "libros/confirmar_eliminar.html",
        libro=libro,
        active_loans=active_loans,
    )


# ── Detail ─────────────────────────────────────────────────────────────────


@books_bp.route("/<id>")
@login_required
def detalle(id):
    """Show book detail with loan history."""
    libro = book_service.obtener_libro(id)
    if not libro:
        flash("Libro no encontrado.", "error")
        return redirect(url_for("books.listar"))

    # Fetch loan history, most recent first
    prestamos = list(
        mongo.db.prestamos.find({"libro_id": ObjectId(id)}).sort(
            "fecha_prestamo", -1
        )
    )

    # Resolve borrower names for display
    for prestamo in prestamos:
        user = mongo.db.usuarios.find_one(
            {"_id": prestamo["usuario_id"]}, {"nombre": 1}
        )
        prestamo["usuario_nombre"] = user["nombre"] if user else "—"

    return render_template(
        "libros/detalle.html",
        libro=libro,
        prestamos=prestamos,
    )
