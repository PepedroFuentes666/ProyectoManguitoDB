"""WSGI entry point for Render / Gunicorn.

Avoids the bash parsing issues with parentheses in the start command
and decouples gunicorn's WSGI call detection from the app factory.

Usage:
    gunicorn wsgi:app
"""

from biblioteca.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
