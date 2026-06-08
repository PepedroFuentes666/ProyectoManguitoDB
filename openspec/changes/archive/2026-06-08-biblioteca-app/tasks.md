# Tasks: Biblioteca App

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~970 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Scaffold+Auth) → PR 2 (Books) → PR 3 (Loans+Dash+Deploy) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Scaffold + Models + Auth + Seed | PR 1 | ~310 lines. Base: feature/tracker branch. Login working. |
| 2 | Book CRUD (service, routes, 4 templates) | PR 2 | ~250 lines. Base: PR 1 branch. |
| 3 | Loan CRUD + Dashboard + Deploy | PR 3 | ~410 lines. Base: PR 2 branch. May need sub-split. |

## Phase 1: Project Scaffolding

- [x] 1.1 Create `biblioteca/app.py` — app factory, blueprint registration, index creation
- [x] 1.2 Create `biblioteca/config.py` — Config class from env vars (MONGODB_URI, SECRET_KEY)
- [x] 1.3 Create `biblioteca/extensions.py` — LoginManager, Bcrypt, PyMongo wrapper, index creation
- [x] 1.4 Write `biblioteca/requirements.txt` — Flask, PyMongo, Flask-Login, Flask-Bcrypt, python-dotenv, gunicorn
- [x] 1.5 Create `biblioteca/.env` template with placeholder MONGODB_URI, SECRET_KEY
- [x] 1.6 Create `biblioteca/.gitignore` — Python/Flask (venv, __pycache__, .env)

## Phase 2: MongoDB Connection & Models

- [x] 2.1 Add PyMongo connect in extensions.py: `_MongoWrapper`, `init_db(app)`, `mongo.db` accessor
- [x] 2.2 Create `biblioteca/models/user.py` — User(UserMixin), `get_id()` str(_id), `get_by_id()`, `get_by_email()`
- [x] 2.3 Create `biblioteca/models/book.py` — Book helper: `from_dict()`, ejemplares_totales >= 1 validation
- [x] 2.4 Create `biblioteca/models/loan.py` — Loan helper: `from_dict()`, ObjectId conversion
- [x] 2.5 Add indexes in extensions.py `init_db()`: email unique, ISBN unique, text(titulo+autor), libro_id, estado+fecha_prestamo

## Phase 3: Authentication

- [x] 3.1 Create `biblioteca/services/auth_service.py` — `autenticar(email, pw)` → User or None, bcrypt
- [x] 3.2 Create `biblioteca/routes/auth.py` — GET/POST /auth/login, GET /logout, @login_required, flash, minimal POST /register
- [x] 3.3 Create `biblioteca/templates/auth/login.html` — centered Bootstrap 5 form extending base.html
- [x] 3.4 Create `biblioteca/seed.py` — demo user (demo@demo.com / Demo1234) + 6 sample books, idempotent upsert

## Phase 4: Book CRUD

- [x] 4.1 Create `biblioteca/services/book_service.py` — crear_libro, buscar_libros, actualizar_libro, eliminar_libro
- [x] 4.2 Create `biblioteca/routes/books.py` — list, create, edit, delete, detail + ?q= search
- [x] 4.3 Create `biblioteca/templates/libros/listar.html` — book table, search bar, .table-responsive
- [x] 4.4 Create `biblioteca/templates/libros/form.html` — shared create/edit, year validation
- [x] 4.5 Create `biblioteca/templates/libros/detalle.html` — book detail + loan history section
- [x] 4.6 Create `biblioteca/templates/libros/confirmar_eliminar.html` — delete confirmation

## Phase 5: Loan CRUD

- [x] 5.1 Create `biblioteca/services/loan_service.py` — crear_prestamo (atomic $inc), devolver_prestamo
- [x] 5.2 Create `biblioteca/routes/loans.py` — list, create (libro dropdown), return routes
- [x] 5.3 Create `biblioteca/templates/prestamos/listar.html` — loan table, status badges
- [x] 5.4 Create `biblioteca/templates/prestamos/form.html` — loan form, libro dropdown

## Phase 6: Dashboard & UI Polish

- [x] 6.1 Create `biblioteca/templates/dashboard.html` — stats cards (total books, loans, active)
- [x] 6.2 Update `biblioteca/app.py` — root route renders dashboard with stats; update `biblioteca/templates/base.html` — navbar with Dashboard, Libros, Préstamos links
- [x] 6.3 Update `biblioteca/templates/base.html` — active state, user email, navbar links
- [x] 6.4 Add form validation: ISBN 10/13 digit validation in `book_service.py`, required fields, year range

## Phase 7: Final Setup

- [x] 7.1 Verify seed: demo user + 6 books, idempotent, bcrypt hashes (verified — seed.py is correct)
- [x] 7.2 Create deploy config: `biblioteca/render.yaml` with gunicorn entry
- [x] 7.3 Create `README.md` at project root with full documentation in Spanish
