"""Run on a throwaway database so it cannot disturb the shared test DB."""

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text

from app.db import models  # noqa: F401
from app.db.base import Base
from tests.conftest import OWNER_URL, alembic

MIG_DB = "labellens_migtest"


@pytest.fixture()
def mig_url(owner_engine):
    admin = create_engine(OWNER_URL.rsplit("/", 1)[0] + "/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f"drop database if exists {MIG_DB}"))
        c.execute(text(f"create database {MIG_DB}"))
    url = OWNER_URL.rsplit("/", 1)[0] + "/" + MIG_DB
    yield url
    with admin.connect() as c:
        c.execute(text(f"drop database if exists {MIG_DB}"))
    admin.dispose()


def tables(url):
    eng = create_engine(url)
    with eng.connect() as c:
        t = set(c.execute(text("select tablename from pg_tables where schemaname='public'")).scalars())
    eng.dispose()
    return t


def test_upgrade_downgrade_upgrade_roundtrip(mig_url):
    alembic("upgrade", "head", url=mig_url)
    assert len(tables(mig_url) - {"alembic_version"}) == 22
    alembic("downgrade", "base", url=mig_url)
    assert tables(mig_url) == {"alembic_version"}
    alembic("upgrade", "head", url=mig_url)
    assert len(tables(mig_url) - {"alembic_version"}) == 22


def test_models_and_migrations_have_not_drifted(mig_url):
    alembic("upgrade", "head", url=mig_url)
    eng = create_engine(mig_url)
    with eng.connect() as c:
        diff = compare_metadata(MigrationContext.configure(c, opts={"compare_type": True}), Base.metadata)
    eng.dispose()
    assert diff == [], f"schema drift: {diff}"


def test_all_requested_tables_exist(mig_url):
    alembic("upgrade", "head", url=mig_url)
    required = {"users", "user_preferences", "products", "product_categories", "ingredients", "ingredient_synonyms",
                "product_ingredients", "ingredient_functions", "ingredient_assessments", "ingredient_sources",
                "ingredient_regulations", "scans", "scan_images", "extracted_text", "scan_ingredients", "scan_reports",
                "alternative_products", "product_comparisons", "user_favourites"}
    added = {"data_imports", "user_preference_items", "ingredient_function_map"}
    assert required | added <= tables(mig_url)
