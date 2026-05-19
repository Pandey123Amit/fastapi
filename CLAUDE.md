# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI + SQLAlchemy + Alembic + PostgreSQL project with JWT authentication. Provides Student and Course APIs with standard CRUD, all protected by JWT Bearer tokens.

## Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# PostgreSQL via Docker (dev database)
docker compose up -d

# Apply migrations once the DB is healthy
alembic upgrade head

# Run the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Stop the database container (data kept in Docker volume fastapi_pgdata)
docker compose down

# Nuclear reset: remove container + volume, then recreate a fresh DB
docker compose down -v && docker compose up -d && alembic upgrade head

# Create a new migration (after model changes)
alembic revision --autogenerate -m "migration name"
```

Default connection string (`DATABASE_URL`): `postgresql://postgres:postgres@localhost:5434/fastapi`. Host port **5434** avoids colliding with a local PostgreSQL install on **5432**. Copy `.env.example` to `.env` or set `DATABASE_URL` there if you customize credentials.

## Architecture

### Layered Structure
- `app/models/` - SQLAlchemy ORM models (declarative base)
- `app/schemas/` - Pydantic schemas (request/response validation)
- `app/crud/` - Database operations (get, create, update, delete)
- `app/api/v1/endpoints/` - FastAPI route handlers
- `app/core/config.py` - Settings via pydantic-settings (reads `.env`)

### API Routing
- Health checks at root: `/health`, `/health/db`
- Auth endpoints: `/api/v1/auth/register`, `/api/v1/auth/login`
- Protected API v1: `/api/v1/students`, `/api/v1/courses` (require `Authorization: Bearer <token>`)
- Router is in `app/api/v1/router.py`

### Authentication
- JWT Bearer token authentication
- `app/core/security.py` - password hashing (bcrypt), JWT encode/decode
- `app/api/deps.py` - `get_current_user` dependency validates token and returns User
- Protected endpoints use `Depends(get_current_user)` parameter
- Login returns `access_token` and `token_type: "bearer"`

### Database
- SQLAlchemy 2.0 with `Mapped` columns and `mapped_column()`
- Alembic for migrations (scripts in `alembic/versions/`)
- Connection via `app/db/session.py` - `get_db()` dependency for FastAPI routes
- Models must be imported in `alembic/env.py` for autogenerate to work
- The `include_object` function in `alembic/env.py` prevents autogenerate from dropping tables not declared in this app's models

### Configuration
- Settings in `app/core/config.py` using `pydantic_settings.BaseSettings`
- Database URL normalization: `?schema=...` query params are stripped and applied via `search_path` instead (psycopg2 limitation)
- Environment: `.env` file (gitignored), `.env.example` as template

### Schemas Pattern
Each resource has:
- `*Base` - shared fields
- `*Create` - creation payload (extends Base)
- `*Update` - partial update (all fields optional)
- `*Read` - response model with `from_attributes=True`
- `*List` - paginated list response
