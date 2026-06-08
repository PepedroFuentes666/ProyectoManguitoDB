# UI Specification

## Purpose

Jinja2 + Bootstrap 5 templates for the Biblioteca app: pages, navigation, forms, and flash messages.

## Requirements

### Requirement: Layout and Navigation

The system MUST render a base layout (`base.html`) with a Bootstrap 5 responsive navbar.

#### Scenario: Authenticated user sees nav

- GIVEN the user is authenticated
- WHEN any page is rendered
- THEN the navbar shows links: Libros, Préstamos, Cerrar sesión
- AND the current user's email is displayed

#### Scenario: Unauthenticated user sees login

- GIVEN no session exists
- WHEN the login page is rendered
- THEN the page shows a centered login form with email, password fields, and "Iniciar sesión" button
- AND NO navbar links are shown

### Requirement: Page Inventory

The system MUST render the following pages via Flask templates:

| Route | Template | Description |
|-------|----------|-------------|
| `/` | `dashboard.html` | Stats: total books, total loans, active loans |
| `/auth/login` | `auth/login.html` | Login form |
| `/libros/` | `libros/listar.html` | Book list with search bar |
| `/libros/crear` | `libros/form.html` | Create book form |
| `/libros/<id>` | `libros/detalle.html` | Book detail + loan history |
| `/libros/<id>/editar` | `libros/form.html` | Edit book form (pre-filled) |
| `/libros/<id>/eliminar` | `libros/confirmar_eliminar.html` | Delete confirmation |
| `/prestamos/` | `prestamos/listar.html` | Loan list with status badges |
| `/prestamos/crear` | `prestamos/form.html` | Create loan (book dropdown) |

### Requirement: Flash Messages

The system MUST display Bootstrap 5 dismissible alerts for flash messages categorized by type: `success` (green), `error` (red), `warning` (yellow).

#### Scenario: Flash message after action

- GIVEN a user creates a book successfully
- WHEN redirected to `/libros/`
- THEN a green success alert appears at the top of the page: "Libro creado exitosamente"
- AND the alert is dismissible via Bootstrap close button

### Requirement: Form Validation

Forms SHALL display inline field errors below the corresponding input using Bootstrap's `.is-invalid` class and `.invalid-feedback` div.

#### Scenario: Form with invalid data

- GIVEN the user submits a book form with `ejemplares_totales=""`
- WHEN the form is re-rendered with validation errors
- THEN the `ejemplares_totales` input has the `.is-invalid` CSS class
- AND an error message reads "Este campo es obligatorio"

### Requirement: Responsive Design

The UI MUST use Bootstrap 5's grid system and MUST be usable on mobile viewports (≥ 320px width).

#### Scenario: Mobile layout

- GIVEN the viewport is 375px wide
- WHEN the book list page is rendered
- THEN the table collapses into a card layout per book (responsive table via `.table-responsive`)
- AND the search bar spans full width
