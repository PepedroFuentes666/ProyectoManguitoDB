# Exploration: Biblioteca App — Flask + PyMongo + MongoDB 7

## Current State

The project is **empty** — no code exists. The `openspec/` directory has been initialized with a config.yaml but the stack was listed as "none detected." The university assignment is "Aplicación Web con Persistencia en MongoDB 7" — a library book lending system with two core entities (Libro, Préstamo) and authentication.

## Affected Areas

This is a greenfield project. There are no existing files to modify. The entire application will be created from scratch.

## Findings

### 1. Data Model

#### Colección: `libros`

| Campo | Tipo | Detalles |
|-------|------|----------|
| `_id` | ObjectId | Auto-generado por MongoDB |
| `titulo` | string | REQUERIDO, indexado para búsqueda |
| `autor` | string | REQUERIDO |
| `isbn` | string | ÚNICO (clave natural), REQUERIDO |
| `anio_publicacion` | int | Opcional |
| `genero` | string | Opcional |
| `ejemplares_disponibles` | int | Entero >= 0, default 1 |
| `ejemplares_totales` | int | Entero >= ejemplares_disponibles |
| `created_at` | datetime | Auto-set |
| `updated_at` | datetime | Auto-update |

#### Colección: `prestamos`

| Campo | Tipo | Detalles |
|-------|------|----------|
| `_id` | ObjectId | Auto-generado |
| `libro_id` | ObjectId | REFERENCIA al `_id` de `libros` |
| `usuario_nombre` | string | Nombre de quien retira |
| `usuario_email` | string | Opcional, para contacto |
| `fecha_prestamo` | datetime | Fecha de retiro |
| `fecha_devolucion` | datetime | Null mientras esté activo |
| `fecha_limite` | datetime | Fecha tope de devolución |
| `estado` | string | `activo` | `devuelto` | `vencido` |
| `created_at` | datetime | Auto-set |

#### Relationship Strategy: **Referencia por ObjectId**

- `prestamos.libro_id` → `libros._id` (manual JOIN via application code — MongoDB does not have foreign keys)
- Embedded documents are **not** appropriate here: a book can have many loans over time, and loans are queried independently
- When a loan is created with status `activo`, decrement `libros.ejemplares_disponibles`
- When a loan is returned, increment `libros.ejemplares_disponibles`
- This logic must be in a **transaction or atomic operation** to prevent race conditions

#### Indexes Required

```javascript
// Unique ISBN — natural key for books
db.libros.createIndex({ isbn: 1 }, { unique: true })

// Text search on title and author
db.libros.createIndex({ titulo: "text", autor: "text" })

// Loan lookup by book (for listing loans per book)
db.prestamos.createIndex({ libro_id: 1 })

// Loan lookup by status (for dashboard — active loans)
db.prestamos.createIndex({ estado: 1 })

// Compound: find active loans for a specific book
db.prestamos.createIndex({ libro_id: 1, estado: 1 })
```

### 2. Authentication

#### Colección: `usuarios`

| Campo | Tipo | Detalles |
|-------|------|----------|
| `_id` | ObjectId | Auto-generado |
| `email` | string | ÚNICO, REQUERIDO |
| `password_hash` | string | bcrypt hash, REQUERIDO |
| `nombre` | string | REQUERIDO |
| `rol` | string | `admin` (único rol para MVP) |
| `created_at` | datetime | Auto-set |

Index: `db.usuarios.createIndex({ email: 1 }, { unique: true })`

#### Session Management: **Flask-Login** (recommended over raw sessions)

- Flask-Login provides `login_required` decorator, `current_user` proxy, and session management out of the box
- Much less boilerplate than raw `flask.session`
- Stores user ID in signed session cookie (secure by default with `SECRET_KEY`)

#### Seed User

- Email: `demo@demo.com`
- Password: `Demo1234`
- Must be inserted via a CLI command (`flask seed` or a one-time startup check)

### 3. Features

#### CRUD Libros
| Operación | Ruta | Método | Auth |
|-----------|------|--------|------|
| Listar | `/libros` | GET | Sí |
| Ver detalle | `/libros/<id>` | GET | Sí |
| Crear | `/libros/crear` | GET/POST | Sí |
| Editar | `/libros/<id>/editar` | GET/POST | Sí |
| Eliminar | `/libros/<id>/eliminar` | POST | Sí |
| Buscar | `/libros?q=...` | GET | Sí |

#### CRUD Préstamos
| Operación | Ruta | Método | Auth |
|-----------|------|--------|------|
| Listar | `/prestamos` | GET | Sí |
| Ver detalle | `/prestamos/<id>` | GET | Sí |
| Crear | `/prestamos/crear` | GET/POST | Sí |
| Registrar devolución | `/prestamos/<id>/devolver` | POST | Sí |
| Eliminar | `/prestamos/<id>/eliminar` | POST | Sí |

#### Relationship Feature
- When creating a loan, the user selects a book from a dropdown (populated from `libros` where `ejemplares_disponibles > 0`)
- Validation: cannot create loan if no copies available
- After loan creation: decrement `ejemplares_disponibles`
- After return: increment `ejemplares_disponibles`, set `fecha_devolucion`
- Dashboard: count of active loans, overdue loans

### 4. Project Structure

```
biblioteca/
├── app.py                  # Flask app factory + entry point
├── config.py               # Configuration (MONGODB_URI, SECRET_KEY)
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore
│
├── extensions.py           # Flask extensions init (login_manager, bcrypt)
├── models/
│   ├── __init__.py
│   ├── libro.py            # Libro model class (PyMongo helpers)
│   ├── prestamo.py         # Prestamo model class
│   └── usuario.py          # Usuario model class (UserMixin for Flask-Login)
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Login/logout routes (Blueprint)
│   ├── libros.py           # Libro CRUD routes (Blueprint)
│   └── prestamos.py        # Prestamo CRUD routes (Blueprint)
│
├── services/
│   ├── __init__.py
│   ├── libro_service.py    # Business logic for books
│   └── prestamo_service.py # Business logic for loans + stock management
│
├── templates/
│   ├── base.html           # Base layout (Bootstrap 5)
│   ├── auth/
│   │   ├── login.html
│   ├── libros/
│   │   ├── list.html
│   │   ├── form.html       # Shared create/edit
│   │   └── detail.html
│   ├── prestamos/
│   │   ├── list.html
│   │   ├── form.html
│   │   └── detail.html
│   └── index.html          # Dashboard
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

**Decision: Blueprints over flat routes.** Blueprints provide modularity — each domain (`auth`, `libros`, `prestamos`) is self-contained. For a small project this is the right balance between organization and simplicity.

**Decision: Jinja2 templates over SPA.** This is a university project focused on MongoDB persistence. Adding a JS SPA framework would add complexity without pedagogical value. Bootstrap 5 CDN for styling keeps it simple.

**Decision: Service layer.** Models handle data access (PyMongo calls), services handle business logic (loan/return stock management). This keeps routes thin and testable.

### 5. Deployment Considerations

#### MongoDB Atlas Free Tier
- **Cluster**: M0 Sandbox (512 MB storage, shared RAM)
- **Connection**: `mongodb+srv://<user>:<password>@cluster.mongodb.net/biblioteca?retryWrites=true&w=majority`
- **IP Whitelist**: Must allow all IPs (`0.0.0.0/0`) for cloud deployments or whitelist specific IPs
- **Set up**: Create cluster → Database Access user → Network Access → get connection string
- **Database name**: `biblioteca` (embedded in the URI or set via code)

#### Flask Hosting Options
| Platform | Estimated Cost | Ease | Notes |
|----------|---------------|------|-------|
| **Render** | Free tier (web service + PostgreSQL — not needed here) | Easy | Spin down after inactivity (cold start ~30s) |
| **Railway** | Free tier (limited hours) | Easy | $5 credit, no sleep on paid |
| **Fly.io** | Free tier (3 shared VMs) | Medium | Requires `flyctl`, `Dockerfile` |
| **PythonAnywhere** | Free tier | Easy | No MongoDB support on free tier |

**Recommendation: Render (free tier)** — simplest deployment for Flask. The `render.yaml` or manual setup via dashboard. Add `gunicorn` as WSGI server.

#### Environment Variables
```
FLASK_SECRET_KEY=<random-secret>
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/biblioteca?retryWrites=true&w=majority
FLASK_ENV=production
```

## Approaches

### Approach A: Flat Structure (No Blueprints)

Everything in `app.py` with route functions. Simpler for a small project.

- **Pros**: Fastest to write, no imports to manage
- **Cons**: Unmaintainable as features grow, no separation of concerns
- **Effort**: Low

### Approach B: Blueprint-based Modular Structure (RECOMMENDED)

Separate `routes/` directory with domain-specific Blueprints.

- **Pros**: Clean separation, easy to extend, professional structure, matches real-world Flask apps
- **Cons**: Slightly more boilerplate upfront
- **Effort**: Low-Medium

### Approach C: API + React SPA

Backend Flask API + frontend React SPA.

- **Pros**: Modern stack, separates concerns
- **Cons**: **Overkill for this project.** Adds complexity that distracts from the MongoDB focus. University assignment is about persistence, not frontend frameworks.
- **Effort**: High

### Approach D: Database Relation Strategy — Embedded Documents

Store loan history directly inside the book document as an array.

- **Pros**: One query to get book + all loans
- **Cons**: Document size grows unbounded, difficult to query across loans independently, violates 16MB document limit with many loans
- **Effort**: Low (wrong approach)

## Recommendation

**Go with Approach B** (Blueprint-based structure) with these specifics:

1. **Project structure**: Blueprints for auth, libros, prestamos with a thin service layer
2. **Data model**: Reference by ObjectId between prestamos and libros (not embedded)
3. **Auth**: Flask-Login with `usuarios` collection and bcrypt passwords
4. **Templates**: Jinja2 with Bootstrap 5 CDN — no SPA
5. **Stock management**: Application-level atomic operations for decrement/increment on loan create/return
6. **Deployment**: Render free tier with gunicorn

The config.yaml in `openspec/config.yaml` should be updated to reflect the chosen stack (Flask + PyMongo + MongoDB 7).

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Race condition on stock** | Two users loan the last copy simultaneously | Use `find_one_and_update` with atomic `$inc` or a transaction |
| **MongoDB Atlas free tier cold start** | First query is slow (shared cluster) | Acceptable — this is a university project, not production |
| **Render free tier sleep** | App takes 30s to wake up after inactivity | Acceptable — demo will be pre-warmed or user informed |
| **Password security** | Plaintext passwords in code | Must use bcrypt (via `flask-bcrypt`) — never store raw passwords |
| **No tests** | Regressions during feature additions | At minimum add a smoke test for the Flask app existence |
| **ISBN uniqueness** | User enters duplicate ISBN | Handle `pymongo.errors.DuplicateKeyError` gracefully with flash message |

## Ready for Proposal

**Yes.** The exploration is complete. The orchestrator should launch `/sdd-propose` with the change name `biblioteca-app` to formalize the scope and approach into a proposal document.

**Config update needed**: Before proposal, the orchestrator should update `openspec/config.yaml` to reflect:
- Stack: Python 3.12 + Flask + PyMongo + MongoDB 7
- Architecture: Monolithic Flask with Blueprints
- Testing: None initially (university project)
