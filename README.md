# Diario IA

Sistema multiagente para generación automática de noticias.

## Flujo

sources → ingestion → stories → reporter → editor → control → publisher → community

## Requisitos

- Python 3.10+ (recomendado usar un entorno virtual)
- Paquetes Python: `fastapi`, `uvicorn`, `sqlalchemy`, `jinja2`

## Setup rápido (venv)

Desde la raíz del repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi "uvicorn[standard]" sqlalchemy jinja2
```

Tip: si te aparecen errores de imports (por ejemplo `No module named app`), ejecuta siempre con `python3 -m ...` desde la raíz del repo.

## Ejecutar

```bash
python3 -m uvicorn app.main:app --reload
```

Luego abre:

- API: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:8000/ui`

## Base de datos (SQLite)

Por defecto usa SQLite en archivo:

- URL hardcodeada: `sqlite:///./diario_ia.db` (`app/db/session.py`)
- Archivo generado: `diario_ia.db` en el directorio desde donde levantas el server (normalmente la raíz del repo)

Puedes abrir `diario_ia.db` con DBeaver (driver SQLite). Si el server está corriendo, puede aparecer “database is locked”; detén el server o abre en modo read-only.

## Datos de prueba (seed)

La ingesta actual es **mock** y solo crea artículos si existen `sources` activas en la base de datos.

- Seed por script:
  - `python3 app/db/seed.py`
- Seed por API (con el server corriendo):
  - `POST /debug/seed-sources`

## Disparar la cadena completa

- `POST /orchestrator/run`

## Flujo recomendado para “ver que funciona”

1) Seed de fuentes:
- `POST /debug/seed-sources`

2) Ingesta (mock) para crear `raw_articles`:
- `POST /pipeline/run`

3) Pipeline completo:
- `POST /orchestrator/run`

4) Ver datos creados:
- `GET /sources`
- `GET /articles`
- `GET /stories`
- `GET /publisher/posts`
- `GET /community/posts`

5) Reset (opcional, para empezar limpio):
- `DELETE /debug/reset`

## UI mínima (HTML/CSS)

Hay una UI simple para disparar acciones y ver JSON sin usar curl:

- `GET /ui` (template en `app/templates/index.html`, estilos en `app/static/style.css`)
- Botones: seed, ingesta, pipeline completo, reset y listados

## Debug (VS Code)

Hay una configuración lista para debuggear Uvicorn:

- `/.vscode/launch.json`
- Run and Debug → **FastAPI (uvicorn)**
- Pon breakpoints y dispara endpoints desde `/docs` o `/ui`

## Notas sobre `.env`

Existe `.env.example`, pero actualmente el proyecto **no lee variables de entorno** para configurar la DB u otros servicios (no hay `dotenv` y la `DATABASE_URL` está hardcodeada). Si quieres que soporte Postgres/MySQL por `DATABASE_URL`, lo puedo dejar listo.
