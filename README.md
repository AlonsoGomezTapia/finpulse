# FinPulse Engine

[![CI/CD Pipeline](https://github.com/TU_USUARIO/finpulse/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/finpulse/actions)
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