# Proposal: Biblioteca App — Library Book Lending System

## Intent

Greenfield Flask web app for a university MongoDB assignment. Build a library lending system with auth, book CRUD, and loan management demonstrating MongoDB 7 persistence with ObjectId references between `prestamos` and `libros`.

## Scope

### In Scope
- Flask Blueprint modular structure with app factory
- Auth: Flask-Login + bcrypt, `usuarios` collection, seed user
- CRUD libros: full REST routes with search and stock fields
- CRUD prestamos: create/return/list with `libro_id` ObjectId reference
- Stock management: atomic `$inc` on loan create/return
- UI: Jinja2 + Bootstrap 5 templates, responsive layout
- MongoDB indexes: ISBN unique, text search, loan lookups
- Deployment config for Render free tier

### Out of Scope
- SPA frontend (React/Vue)
- REST API (JSON endpoints)
- User registration (public signup)
- Email notifications for overdue loans
- Reporting/analytics dashboard
- Testing framework setup

## Capabilities

### New Capabilities
- `user-auth`: Login/logout, session management, bcrypt password hashing, `login_required` route protection
- `libro-crud`: Book CRUD with search, stock tracking, ISBN uniqueness enforcement
- `prestamo-crud`: Loan CRUD with `libro_id` ObjectId reference, atomic stock management, date tracking
- `web-ui`: Jinja2 templates + Bootstrap 5, base layout, shared form patterns, responsive dashboard

### Modified Capabilities

None — greenfield project, no existing specs.

## Approach

Flask app factory with 3 Blueprints (`auth`, `libros`, `prestamos`). PyMongo direct driver connecting to MongoDB Atlas. Service layer between routes and models for stock management logic (atomic `$inc` via `find_one_and_update`). Flask-Login for session auth with bcrypt hashing. Jinja2 templates with Bootstrap 5 CDN for UI. Reference by ObjectId (`prestamos.libro_id` → `libros._id`), resolved at query time via application-level join.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `biblioteca/` (entire project tree) | New | Full app: `app.py`, `config.py`, `extensions.py`, `models/`, `routes/`, `services/`, `templates/`, `static/`, `requirements.txt`, `.env` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Race condition on stock | Low | Atomic `find_one_and_update` with `$inc` — avoids read-then-write pitfall |
| Render free tier sleep | High | Acceptable for university demo; pre-warm before presentation |
| Duplicate ISBN crash | Low | Catch `pymongo.errors.DuplicateKeyError` gracefully with flash message |
| Plaintext passwords | Low | bcrypt via Flask-Bcrypt — never store raw passwords |

## Rollback Plan

- **Flask app**: delete `biblioteca/` directory — reverts to empty state
- **MongoDB**: drop `biblioteca` database via Atlas UI or `db.dropDatabase()`
- **Config**: restore `openspec/config.yaml` from git if config.yaml was modified
- **Seed data**: re-run seed script after redeploy

## Dependencies

- Python 3.12+, pip
- MongoDB 7 Atlas cluster (M0 free tier)
- Render account (for deployment)

## Success Criteria

- [ ] Flask app starts with `flask run`, shows login page
- [ ] Seed user authenticates (demo@demo.com / Demo1234)
- [ ] Full CRUD for libros (create, read, update, delete, search)
- [ ] Full CRUD for prestamos with stock tracking
- [ ] Loan creation decrements `ejemplares_disponibles`; return increments it
- [ ] No plaintext passwords in `usuarios` collection
