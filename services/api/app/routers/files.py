"""Serves locally stored images, only for valid, unexpired signed URLs (dev/test backend)."""
import hmac
import time

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.core.config import get_settings
from app.core.errors import ApiError
from app.storage import get_storage
from app.storage.local import LocalStorage, sign

router = APIRouter(tags=["files"])


@router.get("/files/{path:path}", include_in_schema=False)
def serve(path: str, exp: int = Query(...), sig: str = Query(...)) -> Response:
    storage = get_storage()
    if not isinstance(storage, LocalStorage):
        raise ApiError(404, "NOT_FOUND", "Not found")
    if exp < time.time():
        raise ApiError(403, "FORBIDDEN", "Link expired")
    if not hmac.compare_digest(sig, sign(get_settings().storage_signing_secret, path, exp)):
        raise ApiError(403, "FORBIDDEN", "Invalid signature")
    try:
        if not storage.exists(path):
            raise ApiError(404, "NOT_FOUND", "Not found")
        data = storage.read(path)
    except ValueError:
        raise ApiError(404, "NOT_FOUND", "Not found") from None
    return Response(data, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=60"})
