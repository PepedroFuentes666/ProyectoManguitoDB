"""Book CRUD service — business logic for libro operations.

Contracts:
    crear_libro(data) -> tuple[ObjectId | None, str | None]
    obtener_libro(libro_id) -> dict | None
    buscar_libros(q="") -> list[dict]
    actualizar_libro(libro_id, data) -> bool
    eliminar_libro(libro_id) -> bool
"""

from datetime import datetime

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

from ..extensions import mongo
from ..models.book import Book


def _validar_isbn(isbn: str) -> tuple[str | None, str | None]:
    """Validate ISBN format: must be 10 or 13 digits (ignoring dashes/spaces).

    Returns:
        Tuple of (normalized_isbn, None) on success, or (None, error_message)
        on failure — consistent with the (result, error) pattern used elsewhere.
    """
    cleaned = isbn.replace("-", "").replace(" ", "")
    if not cleaned.isdigit():
        return (None, "El ISBN debe contener solo dígitos (guiones y espacios permitidos).")
    if len(cleaned) not in (10, 13):
        return (None, "El ISBN debe tener 10 o 13 dígitos.")
    return (cleaned, None)


def crear_libro(data: dict) -> tuple[ObjectId | None, str | None]:
    """Create a new libro document.

    Validates required fields, ISBN format, year range, then inserts.
    Catches DuplicateKeyError for ISBN and ValueError from Book.from_dict.

    Returns:
        Tuple of (libro_id, None) on success, or (None, error_message) on failure.
    """
    # --- Validate required fields ---
    titulo = data.get("titulo", "").strip()
    autor = data.get("autor", "").strip()
    isbn_raw = data.get("isbn", "").strip()

    if not titulo:
        return (None, "El título es obligatorio.")
    if not autor:
        return (None, "El autor es obligatorio.")
    if not isbn_raw:
        return (None, "El ISBN es obligatorio.")

    # --- Validate ISBN format ---
    isbn, error = _validar_isbn(isbn_raw)
    if error:
        return (None, error)

    data = dict(data)
    data["isbn"] = isbn  # use normalized ISBN for the insert

    # --- Validate anio_publicacion range ---
    anio_str = data.get("anio_publicacion", "").strip()
    if anio_str:
        try:
            anio = int(anio_str)
            current_year = datetime.utcnow().year
            if anio < 1000 or anio > current_year:
                return (None, f"El año debe estar entre 1000 y {current_year}.")
        except ValueError:
            return (None, "El año de publicación debe ser un número válido.")

    # --- Build and insert document ---
    try:
        doc = Book.from_dict(data)
        result = mongo.db.libros.insert_one(doc)
        return (result.inserted_id, None)
    except DuplicateKeyError:
        return (None, "El ISBN ingresado ya existe en el sistema.")
    except ValueError as e:
        return (None, str(e))


def obtener_libro(libro_id: str) -> dict | None:
    """Find a libro by its ObjectId.

    Returns:
        The libro document dict, or None if not found.
    """
    return mongo.db.libros.find_one({"_id": ObjectId(libro_id)})


def buscar_libros(q: str = "") -> list[dict]:
    """Search libros by text query or return all books.

    If *q* is empty, returns all libros sorted by ``fecha_creacion`` desc.
    If *q* is non-empty, uses MongoDB ``$text`` search on ``titulo`` and
    ``autor``, sorted by text relevance.
    """
    if q:
        cursor = mongo.db.libros.find(
            {"$text": {"$search": q}},
            {"score": {"$meta": "textScore"}},
        ).sort([("score", {"$meta": "textScore"})])
    else:
        cursor = mongo.db.libros.find().sort("fecha_creacion", -1)

    return list(cursor)


def actualizar_libro(libro_id: str, data: dict) -> bool:
    """Update a libro document.

    Only writable fields are applied: titulo, autor, isbn, editorial,
    anio_publicacion, genero, ejemplares_totales.  The
    ``fecha_actualizacion`` is set to the current UTC datetime.

    Returns:
        True if a document was matched (and potentially modified),
        False otherwise.
    """
    update_fields: dict = {}

    # String fields — only set if non-empty
    for key in ("titulo", "autor", "editorial", "genero"):
        val = data.get(key, "").strip()
        if val:
            update_fields[key] = val

    # ISBN — validate format before storing
    isbn_raw = data.get("isbn", "").strip()
    if isbn_raw:
        isbn_val, error = _validar_isbn(isbn_raw)
        if error:
            raise ValueError(error)
        update_fields["isbn"] = isbn_val

    # anio_publicacion — validate range
    anio_str = data.get("anio_publicacion", "").strip()
    if anio_str:
        try:
            anio = int(anio_str)
            current_year = datetime.utcnow().year
            if anio < 1000 or anio > current_year:
                raise ValueError(
                    f"El año debe estar entre 1000 y {current_year}."
                )
            update_fields["anio_publicacion"] = anio_str
        except ValueError as e:
            # Re-raise our own validation message so the route can catch it
            if "debe estar entre" in str(e):
                raise
            raise ValueError("El año de publicación debe ser un número válido.")

    # ejemplares_totales — validate minimum
    ejemplares_str = data.get("ejemplares_totales", "").strip()
    if ejemplares_str:
        try:
            total = int(ejemplares_str)
            if total < 1:
                raise ValueError("ejemplares_totales debe ser al menos 1.")
            update_fields["ejemplares_totales"] = total
        except ValueError as e:
            if "ejemplares_totales" in str(e):
                raise
            raise ValueError("ejemplares_totales debe ser un número válido.")

    if not update_fields:
        return False

    update_fields["fecha_actualizacion"] = datetime.utcnow()

    result = mongo.db.libros.update_one(
        {"_id": ObjectId(libro_id)},
        {"$set": update_fields},
    )
    return result.matched_count > 0


def eliminar_libro(libro_id: str) -> bool:
    """Delete a libro document.

    Only allows deletion if **no active loans** reference this book.

    Returns:
        True if the document was deleted.
        False if the document was not found or has active loans.
    """
    active_loans = mongo.db.prestamos.count_documents(
        {"libro_id": ObjectId(libro_id), "estado": "activo"}
    )
    if active_loans > 0:
        return False

    result = mongo.db.libros.delete_one({"_id": ObjectId(libro_id)})
    return result.deleted_count > 0
