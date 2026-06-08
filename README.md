# Biblioteca ManguitoDB

Sistema de gestión de préstamos bibliotecarios con Flask y MongoDB. Permite administrar libros, realizar préstamos con control atómico de stock y consultar el historial de devoluciones.

## Entidades

- **Libro**: Almacena título, autor, ISBN, género, editorial, año de publicación y cantidad de ejemplares. Se utiliza `ObjectId` como clave primaria para mantener referencias normalizadas.
- **Préstamo**: Registra cada préstamo de un libro a un usuario. Contiene `libro_id` y `usuario_id` como referencias `ObjectId` a las colecciones `libros` y `usuarios`, permitiendo un ciclo de vida independiente (estado activo/devuelto, fechas de préstamo y devolución).

## Stack Tecnológico

- **Lenguaje**: Python 3.12+
- **Framework**: Flask 3.x
- **Base de datos**: MongoDB 7.0.x (Atlas M0)
- **ODM**: PyMongo 4.5+
- **Autenticación**: Flask-Login + Flask-Bcrypt
- **Frontend**: Bootstrap 5.3
- **Servidor producción**: Gunicorn

## Requisitos

- Python 3.12 o superior
- MongoDB 7.0.x (local o Atlas)
- Conexión a Internet (para CDN de Bootstrap)

## Configuración

1. Clonar el repositorio e ingresar al directorio:

```bash
cd biblioteca
```

2. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Configurar variables de entorno. Crear un archivo `.env` en `biblioteca/` con:

```env
MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/biblioteca
SECRET_KEY=una-clave-segura-aleatoria
```

4. Poblar la base de datos con datos de demostración:

```bash
cd biblioteca
pip install -r requirements.txt
python seed.py
```

5. Iniciar la aplicación:

```bash
flask --app biblioteca.app:create_app run
```

## Usuario de Demostración

| Campo    | Valor            |
|----------|------------------|
| Email    | demo@demo.com    |
| Contraseña | Demo1234       |

## Despliegue

La aplicación está preparada para desplegarse en [Render](https://render.com) usando el archivo `render.yaml` incluido.

Variables de entorno requeridas en producción:
- `MONGODB_URI`: Cadena de conexión a MongoDB Atlas
- `SECRET_KEY`: Clave secreta para las sesiones de Flask

---

Proyecto universitario — Sistema de Gestión Bibliotecaria con MongoDB.
