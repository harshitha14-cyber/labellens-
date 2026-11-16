import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import AuthUser, current_user
from app.db.models import User
from app.db.session import db_for_user


class Ctx:
    def __init__(self, db: Session, user: AuthUser) -> None:
        self.db, self.user = db, user
        self.uid = uuid.UUID(user.id)


def ctx(db: Annotated[Session, Depends(db_for_user)], user: Annotated[AuthUser, Depends(current_user)]) -> Ctx:
    """Authenticated request context. Creates the profile row on first use; refuses accounts pending deletion."""
    try:
        uid = uuid.UUID(user.id)
    except ValueError:
        raise ApiError(401, "UNAUTHENTICATED", "Invalid subject") from None
    row = db.execute(select(User).where(User.id == uid)).scalar_one_or_none()
    if row is None:
        db.execute(pg_insert(User).values(id=uid).on_conflict_do_nothing())
        db.commit()
    elif row.deleted_at is not None:
        raise ApiError(403, "FORBIDDEN", "Account is scheduled for deletion")
    return Ctx(db, user)


C = Annotated[Ctx, Depends(ctx)]
