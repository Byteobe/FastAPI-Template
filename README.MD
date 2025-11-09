

# project_name

FastAPI + PostgreSQL + Docker Compose (Production Ready)



## 📁 Estructura del Proyecto

```
.
├── .env                        # Variables de entorno
├── .gitignore                  # Archivos y carpetas ignoradas por Git
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes/
│   │   │   │   ├── users.py           # Rutas de usuarios
│   │   │   │   ├── items.py           # Rutas de items
│   │   │   │   └── __init__.py
│   │   │   ├── schemas/               # Esquemas Pydantic
│   │   │   │   ├── users.py
│   │   │   │   ├── items.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py                  # Configuración principal (CORS, Base settings, etc.)
│   │   ├── security.py                # Seguridad / JWT
│   │   ├── logging_config.py          # Configuración de logging
│   │   └── __init__.py
│   ├── db/
│   │   ├── base.py                    # Declaración de modelos base SQLAlchemy
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   │   └── __init__.py
│   │   ├── session.py                 # Conexión y sesión de base de datos
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py            # Lógica de autenticación
│   │   └── __init__.py
│   ├── utils/
│   │   ├── helpers.py                 # Funciones auxiliares
│   │   └── __init__.py
│   ├── main.py                        # Punto de entrada de la aplicación
│   └── __init__.py
│
├── docker-compose.yml                 # Configuración del entorno Docker
├── Dockerfile                         # Imagen base para FastAPI
├── requirements.txt                   # Dependencias del proyecto
├── README.md                          # Documentación principal
└── tests/
    ├── test_users.py                  # Pruebas de endpoints de usuario
    ├── test_items.py                  # Pruebas de endpoints de items
    └── conftest.py                    # Configuración de pruebas
```



## 🛠️ Instalación

Clona el repositorio y entra al proyecto:

```bash
git clone https://github.com/Byteobe/fastapi-template.git
cd project_name
```

[text](../../../../../Users/gomez/Downloads/Django-template/Makefile)

## 🐳 Entorno de Desarrollo con Docker

Levanta la aplicación con:

```bash
docker-compose up
```

> Si es la primera vez, puede que la base de datos no esté lista al iniciar. Vuelve a ejecutar `docker-compose up` si falla la primera vez.

Accede a tu proyecto en [http://localhost:8000](http://localhost:8000)
Swagger UI en [http://localhost:8000/docs](http://localhost:8000/docs)
Redoc en [http://localhost:8000/redoc](http://localhost:8000/redoc)
Esquema YAML en [http://localhost:8000/openapi.yaml](http://localhost:8000/openapi.yaml)

---

### 🔁 Comandos útiles

* Reconstruir imágenes después de instalar nuevas dependencias:

```bash
docker-compose up --build
```

* Eliminar contenedores y la base de datos (útil si hay errores de migración):

```bash
docker-compose down
```

* Ejecutar migraciones:

```bash
docker-compose exec app alembic upgrade head
```

---

## 🔐 Creación de superusuario

Para crear un usuario administrador:

```bash
docker-compose exec app python
>>> from app.db.models.user import User
>>> from app.db.session import SessionLocal
>>> db = SessionLocal()
>>> admin = User(username="admin", email="admin@example.com", is_superuser=True)
>>> admin.set_password("admin")
>>> db.add(admin)
>>> db.commit()
>>> exit()
```

Accede al admin personalizado o endpoints de gestión según tu implementación.

---

## 🚀 Despliegue en Producción (Docker)

1. Construye y sube la imagen al servidor:

```bash
docker build -t project_name .
docker tag project_name your_registry/project_name:latest
docker push your_registry/project_name:latest
```

2. Corre la app en producción usando docker-compose o Kubernetes según tu setup.

---

## 🔒 SSL (HTTPS) Opcional

Si usas un proxy inverso como Nginx, habilita SSL con Let’s Encrypt.

---

## 📚 Más información

* FastAPI: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* Docker: [https://www.docker.com](https://www.docker.com)
* PostgreSQL: [https://www.postgresql.org](https://www.postgresql.org)

---

🎉 ¡Proyecto listo para desarrollo y producción!

---

Si quieres, puedo hacer **una versión aún más limpia** que incluya **comentarios de qué va en cada carpeta y archivos más detallado**, muy al estilo Django que tenías, lista para que tus compañeros lo entiendan al instante.

¿Quieres que haga eso?
# FastAPI-Template
