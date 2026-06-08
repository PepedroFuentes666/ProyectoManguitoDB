"""Helpers for libro document structure and validation."""

from datetime import datetime


class Book:
    """Static helpers for creating and validating book documents.

    Expected document fields:
        _id, titulo, autor, isbn, editorial, anio_publicacion,
        genero, ejemplares_totales, ejemplares_disponibles,
        fecha_creacion, fecha_actualizacion
    """

    @staticmethod
    def from_dict(data: dict) -> dict:
        """Build a cleaned libro document dict from user-supplied form data.

        Raises:
            ValueError: if ejemplares_totales < 1.
        """
        total = int(data.get("ejemplares_totales", 0))
        if total < 1:
            raise ValueError("ejemplares_totales debe ser al menos 1.")

        now = datetime.utcnow()
        return {
            "titulo": data.get("titulo", "").strip(),
            "autor": data.get("autor", "").strip(),
            "isbn": data.get("isbn", "").strip(),
            "editorial": data.get("editorial", "").strip(),
            "anio_publicacion": data.get("anio_publicacion"),
            "genero": data.get("genero", "").strip(),
            "ejemplares_totales": total,
            "ejemplares_disponibles": total,
            "fecha_creacion": now,
            "fecha_actualizacion": now,
        }
