# Auth Specification

## Purpose

Authentication and session management for the Biblioteca app. Handles login, logout, password hashing, and route protection via Flask-Login.

## Requirements

### Requirement: User Login

The system MUST authenticate users against the `usuarios` collection using email + bcrypt-hashed password, and MUST create a Flask-Login session on success.

#### Scenario: Successful login with valid credentials

- GIVEN a user exists in `usuarios` with email `demo@demo.com` and a bcrypt hash matching `Demo1234`
- WHEN the user POSTs to `/auth/login` with email=`demo@demo.com` and password=`Demo1234`
- THEN the system creates a Flask-Login session
- AND redirects to `/libros/` with a success flash message

#### Scenario: Failed login with wrong password

- GIVEN the user `demo@demo.com` exists with password `Demo1234`
- WHEN the user POSTs to `/auth/login` with email=`demo@demo.com` and password=`wrongpass`
- THEN the system returns the login page with an error flash message
- AND does NOT create a session

#### Scenario: Login with non-existent email

- GIVEN no user exists with email `unknown@test.com`
- WHEN the user POSTs to `/auth/login` with email=`unknown@test.com` and any password
- THEN the system returns the login page with an error flash message
- AND does NOT create a session

### Requirement: Logout

The system MUST clear the Flask-Login session on GET `/auth/logout` and redirect to the login page.

#### Scenario: Logout clears session

- GIVEN an authenticated user session
- WHEN the user GETs `/auth/logout`
- THEN the session is cleared
- AND the user is redirected to `/auth/login` with a logout flash message

### Requirement: Route Protection

Routes decorated with `@login_required` MUST redirect unauthenticated requests to `/auth/login`.

#### Scenario: Accessing protected route without session

- GIVEN no active Flask-Login session
- WHEN the user GETs `/libros/`
- THEN the system redirects to `/auth/login?next=/libros/`

### Requirement: Password Storage

The system MUST store passwords as bcrypt hashes in `usuarios.password_hash` and MUST NOT store plaintext passwords.

#### Scenario: Verify password is hashed

- GIVEN a seed user is inserted into `usuarios`
- WHEN querying the user's document
- THEN `password_hash` contains a bcrypt hash string starting with `$2b$`
- AND `password_hash` does NOT equal the original password

### Requirement: Demo Seed User

The system SHALL provide a seed script that creates a demo user (`demo@demo.com` / `Demo1234`) if the `usuarios` collection is empty on first run.

#### Scenario: Seed user created on empty database

- GIVEN the `usuarios` collection is empty
- WHEN the app starts or seed script runs
- THEN a document is inserted with email=`demo@demo.com` and a valid bcrypt hash of `Demo1234`
