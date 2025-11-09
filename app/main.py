from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
import yaml

app = FastAPI(title="FastAPI Template", version="1.0.0")

# Importar tus routers
from app.api.v1.routes import users
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# Ruta raíz (/) que muestra un mensaje de bienvenida
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
        <head>
            <title>FastAPI Template</title>
        </head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>🚀 Bienvenido a la API de FastAPI Template</h1>
            <p>Explora la documentación:</p>
            <ul style="list-style: none;">
                <li><a href="/docs" target="_blank">Swagger UI</a></li>
                <li><a href="/redoc" target="_blank">ReDoc</a></li>
                <li><a href="/openapi.yaml" target="_blank">Esquema OpenAPI (YAML)</a></li>
            </ul>
        </body>
    </html>
    """

# Endpoint para devolver el esquema en YAML
@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    """Devuelve el esquema OpenAPI en formato YAML"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    yaml_schema = yaml.dump(openapi_schema, sort_keys=False)
    return Response(content=yaml_schema, media_type="application/x-yaml")
