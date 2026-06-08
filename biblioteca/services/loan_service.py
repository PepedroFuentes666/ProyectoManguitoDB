"""Loan CRUD service — business logic for prestamo operations.

Contracts:
    crear_prestamo(usuario_id, libro_id) -> tuple[ObjectId | None, str | None]
    devolver_prestamo(prestamo_id, libro_id) -> bool
    obtener_prestamo(prestamo_id) -> dict | None
    listar_prestamos(estado=None) -> list[dict]
    obtener_prestamos_por_libro(libro_id) -> list[dict]
"""

from datetime import datetime

from bson.objectid import ObjectId

from ..extensions import mongo


def crear_prestamo(usuario_id: str, libro_id: str) -> tuple:
    """Create a new loan with atomic stock decrement.

    Uses ``find_one_and_update`` to atomically check availability and
    decrement ``ejemplares_disponibles`` in a single operation. If the
    book has no available copies, no loan is created.

    Returns:
        Tuple of (prestamo_id, None) on success, or
        (None, error_message) on failure.
    """
    # --- Atomic stock decrement ---
    libro = mongo.db.libros.find_one_and_update(
        {"_id": ObjectId(libro_id), "ejemplares_disponibles": {"$gt": 0}},
        {"$inc": {"ejemplares_disponibles": -1}},
    )

    if libro is None:
        # Check if the book exists at all (for better error message)
        exists = mongo.db.libros.find_one({"_id": ObjectId(libro_id)})
        if exists is None:
            return (None, "El libro no existe.")
        return (None, "No hay ejemplares disponibles.")

    # --- Create loan document ---
    now = datetime.utcnow()
    prestamo_doc = {
        "usuario_id": ObjectId(usuario_id),
        "libro_id": ObjectId(libro_id),
        "fecha_prestamo": now,
        "fecha_devolucion": None,
        "estado": "activo",
    }

    result = mongo.db.prestamos.insert_one(prestamo_doc)
    return (result.inserted_id, None)


def devolver_prestamo(prestamo_id: str, libro_id: str) -> bool:
    """Return a book by updating the loan and incrementing stock.

    Sets the loan ``estado`` to ``"devuelto"`` and ``fecha_devolucion``
    to now, then atomically increments ``ejemplares_disponibles`` on the
    associated libro.

    Returns:
        True if the loan was updated, False if not found.
    """
    now = datetime.utcnow()

    result = mongo.db.prestamos.update_one(
        {"_id": ObjectId(prestamo_id)},
        {"$set": {"estado": "devuelto", "fecha_devolucion": now}},
    )

    if result.matched_count == 0:
        return False

    # Increment stock — always succeeds if loan was matched
    mongo.db.libros.update_one(
        {"_id": ObjectId(libro_id)},
        {"$inc": {"ejemplares_disponibles": 1}},
    )

    return True


def obtener_prestamo(prestamo_id: str) -> dict | None:
    """Find a prestamo by its ObjectId.

    Returns:
        The prestamo document dict, or None if not found.
    """
    return mongo.db.prestamos.find_one({"_id": ObjectId(prestamo_id)})


def listar_prestamos(estado: str | None = None) -> list[dict]:
    """List all prestamos, optionally filtered by estado.

    Results are sorted by ``fecha_creacion`` descending.
    For each loan, the libro title is resolved and set as
    ``libro_titulo``, and the user's name as ``usuario_nombre``.

    Args:
        estado: Optional filter — ``"activo"``, ``"devuelto"``, or
                ``None`` for all.

    Returns:
        List of enriched prestamo document dicts.
    """
    query = {}
    if estado and estado in ("activo", "devuelto"):
        query["estado"] = estado

    prestamos = list(
        mongo.db.prestamos.find(query).sort("fecha_creacion", -1)
    )

    # Resolve libro titles and user names
    for p in prestamos:
        libro = mongo.db.libros.find_one(
            {"_id": p.get("libro_id")}, {"titulo": 1}
        )
        p["libro_titulo"] = libro["titulo"] if libro else "—"

        user = mongo.db.usuarios.find_one(
            {"_id": p.get("usuario_id")}, {"nombre": 1, "email": 1}
        )
        if user:
            p["usuario_nombre"] = user.get("nombre", user.get("email", "—"))
        else:
            p["usuario_nombre"] = "—"

    return prestamos


def obtener_prestamos_por_libro(libro_id: str) -> list[dict]:
    """Return all prestamos for a specific book.

    Sorted by ``fecha_prestamo`` descending.
    """
    return list(
        mongo.db.prestamos.find({"libro_id": ObjectId(libro_id)})
        .sort("fecha_prestamo", -1)
    )
