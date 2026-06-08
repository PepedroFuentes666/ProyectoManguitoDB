"""Helpers for prestamo document structure and status management."""

from datetime import datetime
from bson.objectid import ObjectId


class Loan:
    """Static helpers for creating and querying loan documents.

    Expected document fields:
        _id, usuario_id (ObjectId), libro_id (ObjectId),
        fecha_prestamo, fecha_devolucion (None | datetime),
        estado ("activo" | "devuelto")
    """

    @staticmethod
    def from_dict(data: dict, usuario_id, libro_id) -> dict:
        """Build a new prestamo document dict.

        Args:
            data: Optional form data (currently unused, reserved for future fields).
            usuario_id: User _id (str or ObjectId).
            libro_id: Book _id (str or ObjectId).

        Returns:
            A dict ready for ``prestamos.insert_one()``.
        """
        return {
            "usuario_id": (
                ObjectId(usuario_id) if isinstance(usuario_id, str) else usuario_id
            ),
            "libro_id": (
                ObjectId(libro_id) if isinstance(libro_id, str) else libro_id
            ),
            "fecha_prestamo": datetime.utcnow(),
            "fecha_devolucion": None,
            "estado": "activo",
            "fecha_creacion": datetime.utcnow(),
        }
