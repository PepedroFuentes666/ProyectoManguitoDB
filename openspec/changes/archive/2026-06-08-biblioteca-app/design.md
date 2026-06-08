# Design: Biblioteca App — Library Book Lending System

## Technical Approach

Greenfield Flask app with 3 Blueprints (auth, libros, prestamos), service layer for atomic stock via PyMongo `find_one_and_update` with `$inc`, Flask-Login session auth, and Jinja2 + Bootstrap 5 UI. ObjectId references between collections with application-level joins. Deployable on Render free tier with MongoDB Atlas M0.

## Architecture Decisions

### Decision: ObjectId References over Embedding

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Embed loans in libros | + Single query, − Bloated docs, − 16MB risk | ❌ Rejected |
| ObjectId refs (app-level join) | + Normalized, + Independent lifecycle, − Extra query per list view | ✅ **Chosen** |

Rationale: Loans have independent lifecycle (status transitions, return dates). Embedding would duplicate book metadata and grow the libro document with every loan. At expected university scale (<10K loans), the extra query for title resolution is negligible.

### Decision: Service Layer between Routes and PyMongo

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Logic in routes | + Simpler, − Untestable, − Mixed concerns | ❌ Rejected |
| Service layer | + Testable, + Thin routes, − More files | ✅ **Chosen** |

Rationale: Atomic stock operations are business-critical. Isolating them in `loan_service.py` enables unit testing without HTTP overhead. Routes handle only request parsing, flash messages, and redirects.

### Decision: Atomic `$inc` for Stock

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Read-check-write | − Race condition on concurrent loans | ❌ Rejected |
| `find_one_and_update` with `$inc` + filter | + Atomic, + No overshoot | ✅ **Chosen** |

Rationale: `find_one_and_update({_id, ejemplares_disponibles: {$gt: 0}}, {$inc: {ejemplares_disponibles: -1}})` is a single atomic operation. Two concurrent requests on the last copy cannot both succeed. Never overshoots below zero.

### Decision: Flask App Factory Pattern

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Global module-level app | − Testability, − Config coupling | ❌ Rejected |
| `create_app()` factory | + Testable, + Config injection | ✅ **Chosen** |

## Data Flow

**Loan Creation:**
```
POST /prestamos/crear
  → routes/loans.py validate form fields
  → loan_service.crear_prestamo(usuario_id, libro_id)
    → find_one_and_update({_id, ejemplares_disponibles: {$gt: 0}},
                          {$inc: {ejemplares_disponibles: -1}})
    → If None: return error, no loan created
    → prestamos.insert_one({libro_id, usuario_id, fecha_prestamo, estado: "activo"})
  → Flash success → redirect to /prestamos/
```

**Loan Return:**
```
POST /prestamos/<id>/devolver
  → routes/loans.py load loan → verify estado == "activo"
  → loan_service.devolver_prestamo(loan_id, libro_id)
    → prestamos.update_one({_id}, {$set: {estado: "devuelto", fecha_devolucion: now}})
    → libros.update_one({_id: libro_id}, {$inc: {ejemplares_disponibles: 1}})
  → Flash success → redirect to /prestamos/
```

**Auth:**
```
POST /auth/login
  → auth_service.autenticar(email, password)
    → usuarios.find_one({email})
    → check_password_hash(hash, password) → return User or None
  → If User: login_user(user), redirect to /libros/
  → If None: flash error, render login
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `biblioteca/app.py` | Create | Flask app factory, blueprint registration, index creation |
| `biblioteca/config.py` | Create | Config class from env vars |
| `biblioteca/extensions.py` | Create | LoginManager, Bcrypt instances |
| `biblioteca/models/user.py` | Create | UserMixin wrapper for usuarios docs |
| `biblioteca/models/book.py` | Create | Book schema validation helpers |
| `biblioteca/models/loan.py` | Create | Loan schema helpers |
| `biblioteca/routes/auth.py` | Create | Auth blueprint: login, logout |
| `biblioteca/routes/books.py` | Create | Libros blueprint: CRUD + text search |
| `biblioteca/routes/loans.py` | Create | Prestamos blueprint: create/return/list |
| `biblioteca/services/auth_service.py` | Create | Login validation, bcrypt verify |
| `biblioteca/services/book_service.py` | Create | Book CRUD, ISBN duplicate handling |
| `biblioteca/services/loan_service.py` | Create | Atomic loan create/return |
| `biblioteca/templates/base.html` | Create | Bootstrap 5 layout, navbar, flash alerts |
| `biblioteca/templates/dashboard.html` | Create | Stats cards: total books, total loans, active loans |
| `biblioteca/templates/auth/login.html` | Create | Login form (register template excluded — registration is out of scope per proposal) |
| `biblioteca/templates/libros/listar.html` | Create | Book list with search |
| `biblioteca/templates/libros/form.html` | Create | Shared create/edit form |
| `biblioteca/templates/libros/detalle.html` | Create | Book detail + loan history |
| `biblioteca/templates/libros/confirmar_eliminar.html` | Create | Delete confirmation |
| `biblioteca/templates/prestamos/listar.html` | Create | Loan list with status badges |
| `biblioteca/templates/prestamos/form.html` | Create | Loan form (book dropdown) |
| `biblioteca/static/style.css` | Create | Custom styles |
| `biblioteca/seed.py` | Create | Seed demo user + sample books |
| `biblioteca/requirements.txt` | Create | Flask, PyMongo, Flask-Login, Flask-Bcrypt, python-dotenv |
| `biblioteca/.env` | Create | MONGODB_URI, SECRET_KEY |
| `biblioteca/.gitignore` | Create | Python/Flask gitignore |

## Interfaces / Contracts

```python
# config.py
class Config:
    MONGODB_URI: str    # mongodb+srv://...
    SECRET_KEY: str     # Flask session key

# services/loan_service.py
def crear_prestamo(usuario_id, libro_id) -> dict | None
def devolver_prestamo(loan_id, libro_id) -> bool

# services/auth_service.py
def autenticar(email, password) -> User | None

# services/book_service.py
def crear_libro(data) -> tuple[ObjectId | None, str | None]
def buscar_libros(q="") -> list[dict]
def actualizar_libro(libro_id, data) -> bool
def eliminar_libro(libro_id) -> bool

# models/user.py
class User(UserMixin):
    def get_id(self) -> str: ...
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Service methods (crear_prestamo, devolver_prestamo) | Mock PyMongo collection, assert atomic calls |
| Unit | Auth service (hash verify, user lookup) | Mock bcrypt + usuarios collection |
| Integration | Route responses (status, redirect, flash) | Flask test client with test MongoDB |
| Integration | Atomic stock (concurrent loan scenario) | Sequential simulation of race condition |

## Migration / Rollout

No migration required — greenfield project. Deploy: (1) Atlas M0 cluster + connection string, (2) set env vars, (3) `pip install`, (4) `python seed.py`, (5) `flask run`. For Render: Web Service with `gunicorn biblioteca.app:create_app()`.

## Resolved Decisions

- **Register template**: Excluded — registration is out of scope per proposal. Only login.html in auth/.
- **Year validation**: `anio_publicacion` MUST be validated in range 1000–current year (dynamic via `datetime.now().year`).
- **Dashboard stats**: Show total books (`libros.count_documents({})`), total loans (`prestamos.count_documents({})`), and active loans (`prestamos.count_documents({estado: "activo"})`).
