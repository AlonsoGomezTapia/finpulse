# FinPulse Engine
[![FinPulse CI/CD Pipeline](https://github.com/AlonsoGomezTapia/finpulse/actions/workflows/ci.yml/badge.svg)](https://github.com/AlonsoGomezTapia/finpulse/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Coverage](https://img.shields.io/badge/Coverage-81%25-brightgreen.svg)]()
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**FinPulse** es un motor asíncrono y orientado a eventos de monitoreo financiero y evaluación de reglas en tiempo real. Diseñado siguiendo estándares de producción, arquitectura limpia, tipado estricto y separación modular de capas.

---

## Arquitectura y Stack Tecnológico

- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) con OpenAPI 3.1 y manejo de errores RFC 7807 (Problem Details).
- **ORM & Persistencia:** [SQLAlchemy 2.0 (Async)](https://docs.sqlalchemy.org/) con PostgreSQL 16 y driver `asyncpg`.
- **Validación & Settings:** [Pydantic v2](https://docs.pydantic.dev/) y Pydantic Settings para configuración tipada.
- **Migraciones:** [Alembic](https://alembic.sqlalchemy.org/) con soporte asíncrono nativo.
- **Worker Concurrente:** Procesamiento asíncrono en background orquestado mediante el lifespan context manager de FastAPI.
- **Calidad de Código & Tipado:** [Ruff](https://docs.astral.sh/ruff/) (linter y formateador ultrarrápido) y [Mypy](https://mypy.readthedocs.io/) con `strict = true`.
- **Seguridad:** [Bandit](https://bandit.readthedocs.io/) para análisis de vulnerabilidades SAST.
- **Testing:** [Pytest](https://docs.pytest.org/), `pytest-asyncio`, `httpx` (ASGITransport en memoria) y SQLite en memoria con >80% de cobertura.

---

## Puesta en Marcha Local

### 1. Clonar el repositorio y configurar variables de entorno
bash
git clone https://github.com/AlonsoGomezTapia/finpulse.git
cd finpulse
cp .env.example .env

### 2. Levantar la infraestructura con Docker
bash
docker compose up -d

### 3. Instalar dependencias y ejecutar migraciones
bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head

### 4. Iniciar el servidor de desarrollo
bash
uvicorn app.main:app --reload
- **Swagger UI interactivo:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Healthcheck:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Ejecución de Tests y Linters
bash
# Ejecutar suite de pruebas con cobertura
pytest --cov=app --cov-report=term-missing
# Validaciones estáticas de formato y tipado
ruff check app/ tests/
mypy app/
bandit -r app/ -c pyproject.toml
