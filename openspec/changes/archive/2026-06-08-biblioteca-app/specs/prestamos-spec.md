# Préstamos Specification

## Purpose

Loan management: create and return loans with atomic stock tracking via MongoDB `$inc` and ObjectId references to `libros`.

## Requirements

### Requirement: Create Loan

The system MUST accept POST to `/prestamos/crear` with `usuario_id` and `libro_id`, atomically decrement `ejemplares_disponibles` via `$inc`, and insert a loan document.

#### Scenario: Successful loan creation

- GIVEN a book exists with `ejemplares_disponibles=3`
- WHEN the user POSTs to `/prestamos/crear` with `libro_id=...`
- THEN a `prestamos` document is created with `fecha_prestamo` set to today and `estado=activo`
- AND `ejemplares_disponibles` is atomically decremented to 2
- AND the user is redirected with a success flash message

#### Scenario: Loan on unavailable book

- GIVEN a book exists with `ejemplares_disponibles=0`
- WHEN the user POSTs to `/prestamos/crear` with that `libro_id`
- THEN the system rejects the loan with an error flash message ("No hay ejemplares disponibles")
- AND no `prestamos` document is created

#### Scenario: Loan with non-existent book

- GIVEN no book exists with `libro_id=invalid_id`
- WHEN the user POSTs to `/prestamos/crear` with that `libro_id`
- THEN the system returns the form with an error flash message
- AND no loan is created

### Requirement: Return Book

The system MUST accept POST to `/prestamos/<id>/devolver`, set `fecha_devolucion` and `estado=devuelto`, and atomically increment `ejemplares_disponibles` via `$inc` on the associated `libro`.

#### Scenario: Successful return

- GIVEN an active loan exists for a book with `ejemplares_disponibles=2`
- WHEN the user POSTs to `/prestamos/<id>/devolver`
- THEN `fecha_devolucion` is set to today, `estado` changes to `devuelto`
- AND `ejemplares_disponibles` is atomically incremented to 3
- AND the user is redirected with a success flash message

#### Scenario: Return already-returned book

- GIVEN a loan with `estado=devuelto`
- WHEN the user POSTs to `/prestamos/<id>/devolver`
- THEN the system rejects with an error flash message ("Este préstamo ya fue devuelto")
- AND `ejemplares_disponibles` is NOT incremented again

### Requirement: List Loans

The system MUST render all loans at GET `/prestamos/` with book title (resolved from `libro_id`) and loan status.

#### Scenario: View loan list

- GIVEN 3 loans exist (some active, some returned)
- WHEN the authenticated user GETs `/prestamos/`
- THEN the page shows all loans with book title, loan date, return date (or "Pendiente"), and status badge

### Requirement: Atomic Stock Operations

All stock changes SHALL use MongoDB `find_one_and_update` with `$inc` in a single atomic operation. The system MUST NOT use read-then-write patterns for stock management.

#### Scenario: Concurrent loan does not overshoot stock

- GIVEN `ejemplares_disponibles=1`
- WHEN two concurrent loan requests arrive for that book
- THEN exactly one succeeds and the other receives a "No hay ejemplares disponibles" error
- AND `ejemplares_disponibles` does not go below 0
