# Architecture & Workflow Guide

Este documento explica el flujo recomendado para trabajar en este template de FastAPI.
La idea es mantener una arquitectura simple y escalable: **Route -> Service (opcional) -> CRUD -> DB/Model**.

## Objetivo del template

Este template está pensado para que cada nuevo módulo (por ejemplo: `users`, `items`, `orders`) siga la misma estructura:

- `models/`: define cómo se guarda la data en la base de datos.
- `schemas/`: define cómo entra/sale la data por la API (validación).
- `crud/`: operaciones directas a base de datos (create, read, update, delete).
- `services/` (opcional): reglas de negocio.
- `api/v1/routes/`: endpoints HTTP.
- `tests/`: pruebas del comportamiento.

---

## Flujo a seguir para crear una nueva funcionalidad

### 1) Definir el requerimiento
Primero define claramente qué necesitas:

- Qué entidad vas a crear (ej: `Product`).
- Qué campos tendrá.
- Qué operaciones soportará (CRUD completo o parcial).
- Qué validaciones/reglas de negocio tiene.

Ejemplo de definición inicial (contrato funcional):

```python
FEATURE = {
	"entity": "Product",
	"fields": ["name:str", "description:str|None", "price:float", "is_active:bool"],
	"operations": ["create", "read_one", "read_many", "update", "delete"],
	"rules": ["price > 0", "name único por negocio"],
}
```

### 2) Crear/actualizar el modelo en `app/models/`
Crea la tabla SQLAlchemy para persistencia.

Ejemplo conceptual:

- `id`, `name`, `price`, `created_at`, etc.

Este modelo representa la estructura real en DB.

Ejemplo (`app/models/product.py`):

```python
from sqlalchemy import Boolean, Column, Float, Integer, String
from app.database import Base


class Product(Base):
	__tablename__ = "products"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, index=True, nullable=False)
	description = Column(String, nullable=True)
	price = Column(Float, nullable=False)
	is_active = Column(Boolean, default=True)
```

### 3) Crear schemas en `app/schemas/`
Crea esquemas Pydantic para separar entrada/salida:

- `ProductCreate`: para crear.
- `ProductUpdate`: para actualizar.
- `ProductOut`: para respuestas.

Regla práctica: **no reutilizar el mismo schema para todo**; separa intención por caso de uso.

Ejemplo (`app/schemas/products.py`):

```python
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
	name: str = Field(min_length=2, max_length=120)
	description: str | None = None
	price: float = Field(gt=0)
	is_active: bool = True


class ProductCreate(ProductBase):
	pass


class ProductUpdate(BaseModel):
	name: str | None = Field(default=None, min_length=2, max_length=120)
	description: str | None = None
	price: float | None = Field(default=None, gt=0)
	is_active: bool | None = None


class ProductOut(ProductBase):
	id: int

	class Config:
		orm_mode = True
```

### 4) Crear CRUD en `app/crud/`
Implementa funciones de acceso a datos. Aquí va SQLAlchemy, no lógica HTTP.

Ejemplo de funciones esperadas:

- `get_product(db, product_id)`
- `get_products(db, skip, limit)`
- `create_product(db, product)`
- `update_product(db, product_id, product_update)`
- `delete_product(db, product_id)`

El CRUD sirve para encapsular la capa de persistencia y mantener rutas limpias.

Ejemplo (`app/crud/product.py`):

```python
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int):
	return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 20):
	return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate):
	db_product = Product(**product.dict())
	db.add(db_product)
	db.commit()
	db.refresh(db_product)
	return db_product


def update_product(db: Session, product_id: int, product_update: ProductUpdate):
	db_product = get_product(db, product_id)
	if not db_product:
		return None

	for key, value in product_update.dict(exclude_unset=True).items():
		setattr(db_product, key, value)

	db.commit()
	db.refresh(db_product)
	return db_product


def delete_product(db: Session, product_id: int):
	db_product = get_product(db, product_id)
	if not db_product:
		return None
	db.delete(db_product)
	db.commit()
	return db_product
```

### 5) Crear Service en `app/services/` (si aplica)
Si hay lógica de negocio (reglas, cálculos, validaciones complejas, integración externa), colócala aquí.

Usa `services` cuando:

- La lógica no es solo “guardar/consultar”.
- La misma regla se reutiliza en varios endpoints.
- Quieres mantener `routes` y `crud` simples.

Ejemplo (`app/services/product_service.py`):

```python
from app.schemas.products import ProductCreate


def validate_product_rules(product: ProductCreate):
	if product.price <= 0:
		raise ValueError("El precio debe ser mayor a 0")

	if "test" in product.name.lower():
		raise ValueError("El nombre no puede contener la palabra 'test'")
```

### 6) Crear rutas en `app/api/v1/routes/`
Define endpoints FastAPI y conecta dependencias (`Depends(get_db)`).

En rutas debes:

- Validar errores de negocio básicos (ej: recurso no existe).
- Llamar a `crud` o `service`.
- Retornar `response_model` correcto.
- Manejar códigos HTTP adecuados.

Ejemplo (`app/api/v1/routes/products.py`):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import product as crud_product
from app.db.session import get_db
from app.schemas.products import ProductCreate, ProductOut
from app.services.product_service import validate_product_rules

router = APIRouter()


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
	try:
		validate_product_rules(product)
	except ValueError as error:
		raise HTTPException(status_code=400, detail=str(error))

	return crud_product.create_product(db, product)
```

### 7) Registrar el router en `app/main.py`
Incluye el router nuevo para exponer endpoints:

- `app.include_router(..., prefix="/api/v1/<modulo>", tags=["<modulo>"])`

Si no registras el router, el módulo no aparece en la API.

Ejemplo (`app/main.py`):

```python
from app.api.v1.routes import products

app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
```

### 8) Probar en `tests/`
Crea pruebas para casos felices y errores esperados:

- Creación válida.
- Duplicados / conflictos.
- Recurso inexistente.
- Actualización y borrado.

Objetivo: asegurar que cada endpoint cumple contrato y reglas.

Ejemplo (`tests/test_products.py`):

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_product_ok():
	payload = {
		"name": "Mouse Gamer",
		"description": "RGB",
		"price": 49.99,
		"is_active": True,
	}
	response = client.post("/api/v1/products/", json=payload)
	assert response.status_code == 201
	assert response.json()["name"] == payload["name"]


def test_create_product_invalid_price():
	payload = {
		"name": "Mouse",
		"description": "RGB",
		"price": -1,
		"is_active": True,
	}
	response = client.post("/api/v1/products/", json=payload)
	assert response.status_code in (400, 422)
```

### 9) Validar documentación automática
Revisa:

- `/docs`
- `/redoc`
- `/openapi.yaml`

Confirma que schemas y respuestas se vean correctos.

Ejemplo de validación rápida:

```bash
curl -s http://localhost:8000/openapi.yaml | head -n 40
```

---

## Flujo resumido (checklist rápido)

1. Definir requerimiento y reglas.
2. Crear `model`.
3. Crear `schemas` (Create/Update/Out).
4. Implementar `crud`.
5. Agregar `service` si hay lógica de negocio.
6. Exponer endpoints en `routes`.
7. Registrar router en `main.py`.
8. Escribir y correr tests.
9. Verificar OpenAPI en docs.

---

## Ejemplo mental completo

"Quiero crear módulo de productos"

- Modelo: `Product` en `app/models/product.py`
- Schemas: `ProductCreate`, `ProductUpdate`, `ProductOut` en `app/schemas/products.py`
- CRUD: funciones de producto en `app/crud/product.py`
- Service (opcional): reglas de precio/impuestos en `app/services/product_service.py`
- Routes: endpoints REST en `app/api/v1/routes/products.py`
- Registro: `include_router` en `app/main.py`
- Tests: `tests/test_products.py`

Así, el equipo mantiene una forma única de trabajo y el proyecto crece sin desorden.
