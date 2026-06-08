# Data Model Specification

## Purpose

MongoDB 7 collection schemas, indexes, and relationship design for the Biblioteca app.

## Collections

### `usuarios`

| Field | Type | Constraints | Default |
|-------|------|-------------|---------|
| `_id` | ObjectId | auto-generated | — |
| `email` | string | unique, required | — |
| `nombre` | string | required | — |
| `password_hash` | string | required, bcrypt hash | — |
| `fecha_creacion` | datetime | — | `datetime.utcnow()` |

### `libros`

| Field | Type | Constraints | Default |
|-------|------|-------------|---------|
| `_id` | ObjectId | auto-generated | — |
| `titulo` | string | required | — |
| `autor` | string | required | — |
| `isbn` | string | unique, required | — |
| `editorial` | string | optional | `""` |
| `anio_publicacion` | int | optional | `None` |
| `genero` | string | optional | `""` |
| `ejemplares_totales` | int | required, >= 1 | — |
| `ejemplares_disponibles` | int | required, >= 0 | `ejemplares_totales` |

### `prestamos`

| Field | Type | Constraints | Default |
|-------|------|-------------|---------|
| `_id` | ObjectId | auto-generated | — |
| `usuario_id` | ObjectId | required, ref `usuarios` | — |
| `libro_id` | ObjectId | required, ref `libros` | — |
| `fecha_prestamo` | datetime | required | `datetime.utcnow()` |
| `fecha_devolucion` | datetime | nullable | `None` |
| `estado` | string | `"activo"` \| `"devuelto"` \| `"cancelado"` | `"activo"` |

## Indexes

The system MUST declare the following MongoDB indexes:

| Collection | Index Key | Options | Rationale |
|------------|-----------|---------|-----------|
| `usuarios` | `email` | `unique=True` | Prevents duplicate accounts, speeds login lookups |
| `libros` | `isbn` | `unique=True` | ISBN uniqueness enforcement |
| `libros` | `titulo`, `autor` | `text=True` | Full-text search across book names |
| `prestamos` | `libro_id` | — | Speeds loan lookup by book |
| `prestamos` | `estado`, `fecha_prestamo` | — | Query active loans |

## Relationship Design

**Reference by ObjectId** (not embedded). `prestamos.libro_id` stores the `_id` from `libros`. The application resolves the book title/author at query time with a second query (application-level join).

**Justification**: Books and loans are independent entities with their own lifecycle. Embedding would duplicate book data across many loan documents and require multi-document updates for book edits. Reference keeps each collection normalized and edits single-source.

## Validation Rules

- `ejemplares_disponibles` MUST be ≤ `ejemplares_totales` at all times
- `fecha_devolucion` MUST be `None` when `estado=activo`
- `fecha_devolucion` MUST be set when `estado=devuelto`
- `isbn` MUST contain at least 10 characters (ISBN-10 or ISBN-13 format)
