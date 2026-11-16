"""DB engine + per-request session that carries the caller's JWT claims into Postgres.

Every transaction the API opens runs `set_config('request.jwt.claims', ..., true)`, so
`auth.uid()` (and therefore every RLS policy) sees the real caller. The API connects as
the `ll_app` role (NOBYPASSRLS): RLS protects data even if an endpoint has a bug.
"""
import json
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import AuthUser, current_user


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True, future=True)


@event.listens_for(Session, "after_begin")
def _apply_claims(session: Session, transaction, connection) -> None:  # type: ignore[no-untyped-def]
    claims = session.info.get("jwt_claims")
    # Always (re)set: an empty value means auth.uid() is NULL -> RLS denies user rows (fail closed).
    connection.execute(text("select set_config('request.jwt.claims', :c, true)"),
                       {"c": json.dumps(claims) if claims else ""})


def db_for_user(user: AuthUser = Depends(current_user)) -> Iterator[Session]:
    with Session(get_engine(), expire_on_commit=False) as session:
        session.info["jwt_claims"] = user.claims
        yield session


def db_anonymous() -> Iterator[Session]:
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session
