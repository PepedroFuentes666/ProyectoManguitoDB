#!/usr/bin/env python3
"""Seed script — idempotent demo data creation.

Usage:
    python biblioteca/seed.py

Creates a demo user and sample books if they don't already exist.
If documents are already present (matched by email / ISBN), they are
left untouched (``$setOnInsert`` + ``upsert=True``).
"""

import os
import sys
from datetime import datetime

import bcrypt as _bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/biblioteca")


def seed():
    """Run the seed: create demo user + sample books."""
    client = MongoClient(MONGODB_URI)
    db = client.get_database()

    print(f"Conectado a MongoDB ({MONGODB_URI[:40]}…)")

    # ------------------------------------------------------------------ #
    #  Demo user                                                         #
    # ------------------------------------------------------------------ #
    password_hash = _bcrypt.hashpw(
        b"Demo1234", _bcrypt.gensalt()
    ).decode("utf-8")

    user_result = db.usuarios.update_one(
        {"email": "demo@demo.com"},
        {
            "$setOnInsert": {
                "email": "demo@demo.com",
                "nombre": "Usuario Demo",
                "password_hash": password_hash,
                "fecha_creacion": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    if user_result.upserted_id:
        print("✓ Usuario demo creado: demo@demo.com / Demo1234")
    else:
        print("• Usuario demo ya existe (saltado)")

    # ------------------------------------------------------------------ #
    #  Sample books                                                      #
    # ------------------------------------------------------------------ #
    books = [
        {
            "titulo": "Cien Años de Soledad",
            "autor": "Gabriel García Márquez",
            "isbn": "978-0307474728",
            "editorial": "Diana",
            "anio_publicacion": 1967,
            "genero": "Realismo Mágico",
            "ejemplares_totales": 5,
            "ejemplares_disponibles": 5,
        },
        {
            "titulo": "Don Quijote de la Mancha",
            "autor": "Miguel de Cervantes",
            "isbn": "978-8423356841",
            "editorial": "Destino",
            "anio_publicacion": 1605,
            "genero": "Novela",
            "ejemplares_totales": 3,
            "ejemplares_disponibles": 3,
        },
        {
            "titulo": "La Sombra del Viento",
            "autor": "Carlos Ruiz Zafón",
            "isbn": "978-8408079545",
            "editorial": "Planeta",
            "anio_publicacion": 2001,
            "genero": "Misterio",
            "ejemplares_totales": 4,
            "ejemplares_disponibles": 4,
        },
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry",
            "isbn": "978-0156013987",
            "editorial": "Harcourt",
            "anio_publicacion": 1943,
            "genero": "Literatura Infantil",
            "ejemplares_totales": 6,
            "ejemplares_disponibles": 6,
        },
        {
            "titulo": "Ficciones",
            "autor": "Jorge Luis Borges",
            "isbn": "978-8420427548",
            "editorial": "Alianza",
            "anio_publicacion": 1944,
            "genero": "Cuentos",
            "ejemplares_totales": 2,
            "ejemplares_disponibles": 2,
        },
        {
            "titulo": "Rayuela",
            "autor": "Julio Cortázar",
            "isbn": "978-8437604573",
            "editorial": "Cátedra",
            "anio_publicacion": 1963,
            "genero": "Novela Experimental",
            "ejemplares_totales": 3,
            "ejemplares_disponibles": 3,
        },
    ]

    now = datetime.utcnow()
    for book in books:
        book["fecha_creacion"] = now
        book["fecha_actualizacion"] = now
        result = db.libros.update_one(
            {"isbn": book["isbn"]},
            {"$setOnInsert": book},
            upsert=True,
        )
        if result.upserted_id:
            print(f"✓ Libro creado: {book['titulo']} — {book['autor']}")
        else:
            print(f"• Libro ya existe: {book['titulo']} (saltado)")

    # ------------------------------------------------------------------ #
    #  Summary                                                            #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 48)
    print("  Resumen de la base de datos")
    print("=" * 48)
    print(f"    Usuarios:  {db.usuarios.count_documents({})}")
    print(f"    Libros:    {db.libros.count_documents({})}")
    print(f"    Préstamos: {db.prestamos.count_documents({})}")
    print("=" * 48)
    print("¡Seed completado!")
    client.close()


if __name__ == "__main__":
    seed()
