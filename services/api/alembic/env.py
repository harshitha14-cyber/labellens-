import os

from sqlalchemy import create_engine, pool

from alembic import context
from app.core.config import get_settings
from app.db import models  # noqa: F401  (register tables)
from app.db.base import Base

target_metadata = Base.metadata


def _url() -> str:
    # Migrations run as the schema owner (ll_owner), never as the API role.
    return os.environ.get("ALEMBIC_DATABASE_URL") or get_settings().migration_database_url


def run_migrations_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
