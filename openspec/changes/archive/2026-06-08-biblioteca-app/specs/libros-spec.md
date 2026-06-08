# Libros Specification

## Purpose

Full CRUD for book management: create, read, update, delete, and search books with stock tracking and ISBN uniqueness.

## Requirements

### Requirement: Create Book

The system MUST accept a POST to `/libros/crear` with valid book fields and insert a document into the `libros` collection.

- Fields: `titulo`, `autor`, `isbn`, `editorial`, `anio_publicacion`, `genero`, `ejemplares_totales`. `ejemplares_disponibles` defaults to `ejemplares_totales`.

#### Scenario: Successful book creation

- GIVEN the user is authenticated
- WHEN the user POSTs to `/libros/crear` with `titulo=Don Quijote`, `autor=Cervantes`, `isbn=9780060934347`, `editorial=Alfaguara`, `anio_publicacion=1605`, `genero=Novela`, `ejemplares_totales=3`
- THEN a new document is inserted into `libros` with `ejemplares_disponibles=3`
- AND the user is redirected to `/libros/` with a success flash message

#### Scenario: Duplicate ISBN rejected

- GIVEN a book with `isbn=9780060934347` already exists
- WHEN POSTing to `/libros/crear` with the same ISBN
- THEN the system catches `pymongo.errors.DuplicateKeyError` and returns the form with an ISBN error flash message
- AND no duplicate document is created

### Requirement: List Books

The system MUST render a paginated list of all books at GET `/libros/`.

#### Scenario: View book list

- GIVEN 5 books exist in `libros`
- WHEN the authenticated user GETs `/libros/`
- THEN a page is rendered showing all 5 books with title, author, ISBN, and available stock

### Requirement: Search Books

The system MUST support text search across `titulo` and `autor` at `/libros/?q={query}` using a MongoDB text index.

#### Scenario: Search finds matching books

- GIVEN books with titles containing "Quijote" exist
- WHEN the user GETs `/libros/?q=Quijote`
- THEN the page shows only books matching the search term

#### Scenario: Search with no results

- GIVEN no books match the query `zzzzz`
- WHEN the user GETs `/libros/?q=zzzzz`
- THEN the page shows an empty list with a "No results" message

### Requirement: Update Book

The system MUST accept POST to `/libros/<id>/editar` with updated fields and modify the existing document.

#### Scenario: Successful book update

- GIVEN a book with `_id=1` exists
- WHEN the user POSTs to `/libros/<id>/editar` with `titulo` changed to "Don Quijote de la Mancha"
- THEN the document's `titulo` is updated
- AND the user is redirected with a success flash message

#### Scenario: ISBN conflict on update

- GIVEN another book already has ISBN `1234567890`
- WHEN the user updates a book to use that same ISBN
- THEN the system returns the edit form with an ISBN error flash message
- AND the update is not applied

### Requirement: Delete Book

The system MUST accept POST to `/libros/<id>/eliminar` and remove the document from `libros`.

#### Scenario: Successful deletion

- GIVEN a book with `_id=1` exists and has no active loans
- WHEN the user POSTs to `/libros/<id>/eliminar`
- THEN the document is removed from `libros`
- AND the user is redirected with a success flash message
