-- Run ONCE as a Postgres superuser (local dev only; passwords are dev-only).
--   psql -U postgres -f scripts/dev_db_setup.sql
-- ll_owner : owns the schema, runs Alembic + import scripts.
-- ll_app   : used by the API. NOBYPASSRLS, so Row Level Security is enforced.
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'll_owner') THEN
    CREATE ROLE ll_owner LOGIN PASSWORD 'll_owner_dev' CREATEDB;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'll_app') THEN
    CREATE ROLE ll_app LOGIN PASSWORD 'll_app_dev' NOSUPERUSER NOBYPASSRLS;
  END IF;
END $$;
SELECT 'CREATE DATABASE labellens OWNER ll_owner' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='labellens')\gexec
SELECT 'CREATE DATABASE labellens_test OWNER ll_owner' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='labellens_test')\gexec
