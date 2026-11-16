import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errors import ApiError
from app.db.models import Ingredient, Product, Scan, User, UserFavourite, UserPreference, UserPreferenceItem
from app.routers.deps import C
from app.schemas import FavouriteIn, FavouriteOut, MeOut, MePatch, PrefItem, PrefsIO

router = APIRouter(prefix="/me", tags=["me"])


def _me(c: C) -> MeOut:
    u = c.db.get(User, c.uid)
    assert u is not None
    return MeOut(id=u.id, display_name=u.display_name, locale=u.locale, email=c.user.email)


@router.get("", response_model=MeOut)
def get_me(c: C) -> MeOut:
    return _me(c)


@router.patch("", response_model=MeOut)
def patch_me(body: MePatch, c: C) -> MeOut:
    u = c.db.get(User, c.uid)
    assert u is not None
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(u, k, v)
    c.db.commit()
    return _me(c)


@router.delete("", status_code=202)
def delete_me(c: C) -> dict[str, str]:
    """Schedules erasure. Data is hard-purged by a later job after the grace window (Milestone 7)."""
    u = c.db.get(User, c.uid)
    assert u is not None
    u.deleted_at = datetime.now(UTC)
    c.db.commit()
    return {"status": "deletion_scheduled", "grace_days": "30"}


def _prefs_out(p: UserPreference | None) -> PrefsIO:
    if p is None:
        return PrefsIO()
    return PrefsIO(include_community_products=p.include_community_products,
                   items=[PrefItem(kind=i.kind, ingredient_id=i.ingredient_id, tag=i.tag) for i in p.items])


@router.get("/preferences", response_model=PrefsIO)
def get_prefs(c: C) -> PrefsIO:
    return _prefs_out(c.db.scalar(select(UserPreference).where(UserPreference.user_id == c.uid)))


@router.put("/preferences", response_model=PrefsIO)
def put_prefs(body: PrefsIO, c: C) -> PrefsIO:
    for it in body.items:
        if (it.ingredient_id is None) == (it.tag is None):
            raise ApiError(422, "VALIDATION_ERROR", "Each item needs exactly one of ingredient_id or tag")
    ids = {i.ingredient_id for i in body.items if i.ingredient_id}
    if ids:
        found = set(c.db.scalars(select(Ingredient.id).where(Ingredient.id.in_(ids))))
        if ids - found:
            raise ApiError(422, "VALIDATION_ERROR", "Unknown ingredient_id", {"unknown": [str(x) for x in ids - found]})
    p = c.db.scalar(select(UserPreference).where(UserPreference.user_id == c.uid))
    if p is None:
        p = UserPreference(user_id=c.uid)
        c.db.add(p)
    p.include_community_products = body.include_community_products
    p.items = [UserPreferenceItem(kind=i.kind, ingredient_id=i.ingredient_id, tag=i.tag) for i in body.items]
    c.db.commit()
    c.db.refresh(p)
    return _prefs_out(p)


@router.get("/favourites", response_model=list[FavouriteOut])
def list_favs(c: C) -> list[UserFavourite]:
    return list(c.db.scalars(select(UserFavourite).order_by(UserFavourite.created_at.desc())))


@router.post("/favourites", status_code=201, response_model=FavouriteOut)
def add_fav(body: FavouriteIn, c: C) -> UserFavourite:
    if (body.product_id is None) == (body.scan_id is None):
        raise ApiError(422, "VALIDATION_ERROR", "Provide exactly one of product_id or scan_id")
    if body.product_id and c.db.get(Product, body.product_id) is None:
        raise ApiError(404, "NOT_FOUND", "Product not found")
    if body.scan_id and c.db.get(Scan, body.scan_id) is None:  # RLS hides other users' scans
        raise ApiError(404, "NOT_FOUND", "Scan not found")
    fav = UserFavourite(user_id=c.uid, product_id=body.product_id, scan_id=body.scan_id)
    c.db.add(fav)
    try:
        c.db.commit()
    except IntegrityError:
        c.db.rollback()
        raise ApiError(409, "INVALID_STATE", "Already a favourite") from None
    return fav


@router.delete("/favourites/{fav_id}", status_code=204)
def del_fav(fav_id: uuid.UUID, c: C) -> Response:
    fav = c.db.get(UserFavourite, fav_id)
    if fav is None:
        raise ApiError(404, "NOT_FOUND", "Favourite not found")
    c.db.delete(fav)
    c.db.commit()
    return Response(status_code=204)
