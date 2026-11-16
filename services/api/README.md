# LabelLens API (Milestone 2)

FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL (>= 15). Auth = Supabase-style JWTs. Storage = local signed-URL backend (dev/test) or Supabase Storage.

## What works (tested)
Auth (JWT verify), 23 REST operations, Row Level Security on every table, scan lifecycle + image upload (EXIF stripped), signed URLs, profile/preferences/favourites, reference + product read endpoints.
## Not built yet
OCR (M3), ingredient analysis/reports (M4), real data (M5), alternatives/comparison (M6), data export + purge job (M7), rate limiting (M8). Supabase Storage adapter is **untested against a real Supabase**.

## Run it (Windows PowerShell / macOS / Linux)
1. Start PostgreSQL 16 **with the roles** (pick one)
   - Docker: from repo root `docker compose up -d db`
   - Native install: `psql -U postgres -f services/api/scripts/dev_db_setup.sql`
2. `cd services/api`
3. `python -m venv .venv` then activate (`.venv\Scripts\Activate.ps1` on Windows, `source .venv/bin/activate` elsewhere)
4. `pip install -e ".[dev]"`
5. `alembic upgrade head`
6. `python -m data_pipeline.seed_dev`
7. `uvicorn app.main:app --reload --port 8000` then open http://localhost:8000/docs
8. Get a dev token: `python scripts/make_dev_token.py` and click "Authorize" in /docs (paste the token), or use `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/categories`

Defaults match `.env.example`; copy it to `services/api/.env` only if you change something.
## Tests / quality
`pytest -q` · `ruff check .` · `mypy app`  (tests need the Postgres from step 1; they create their own `labellens_test` data)
