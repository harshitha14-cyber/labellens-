import base64
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, Header, Query, Response, UploadFile
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.errors import ApiError
from app.db.models import ProductCategory, Scan, ScanImage
from app.routers.deps import C
from app.schemas import ScanCreate, ScanImageOut, ScanList, ScanOut, ScanPatch, SignedUrlOut
from app.services.images import process_upload
from app.storage import get_storage

router = APIRouter(prefix="/scans", tags=["scans"])
UPLOADABLE = {"created", "images_uploaded"}  # after processing starts, images are frozen


def _out(s: Scan, cat: ProductCategory) -> ScanOut:
    return ScanOut(id=s.id, status=s.status, language=s.language, saved=s.saved, note=s.note, category=cat,
                   images=[ScanImageOut.model_validate(i) for i in s.images], created_at=s.created_at)


def _get(c: C, scan_id: uuid.UUID) -> tuple[Scan, ProductCategory]:
    # RLS makes other users' scans invisible -> 404 (never 403, which would confirm existence).
    row = c.db.execute(select(Scan, ProductCategory).join(ProductCategory, ProductCategory.id == Scan.category_id)
                       .where(Scan.id == scan_id, Scan.deleted_at.is_(None))).first()
    if row is None:
        raise ApiError(404, "NOT_FOUND", "Scan not found")
    return row[0], row[1]


@router.post("", status_code=201, response_model=ScanOut)
def create_scan(body: ScanCreate, c: C, response: Response,
                idempotency_key: Annotated[str | None, Header(max_length=80)] = None) -> ScanOut:
    cat = c.db.get(ProductCategory, body.category_id)
    if cat is None or not cat.active:
        raise ApiError(422, "VALIDATION_ERROR", "Unknown category", {"category_id": str(body.category_id)})
    if idempotency_key:
        existing = c.db.scalar(select(Scan).where(Scan.idempotency_key == idempotency_key))
        if existing:
            response.status_code = 200
            return _out(existing, cat)
    scan = Scan(user_id=c.uid, category_id=cat.id, language=body.language, idempotency_key=idempotency_key)
    c.db.add(scan)
    try:
        c.db.commit()
    except IntegrityError:  # concurrent duplicate Idempotency-Key
        c.db.rollback()
        raise ApiError(409, "INVALID_STATE", "Duplicate request") from None
    c.db.refresh(scan)
    return _out(scan, cat)


@router.get("", response_model=ScanList)
def list_scans(c: C, saved: bool | None = None, category_id: uuid.UUID | None = None,
               limit: int = Query(20, ge=1, le=100), cursor: str | None = None) -> ScanList:
    q = select(Scan, ProductCategory).join(ProductCategory, ProductCategory.id == Scan.category_id).where(Scan.deleted_at.is_(None))
    if saved is not None:
        q = q.where(Scan.saved == saved)
    if category_id:
        q = q.where(Scan.category_id == category_id)
    if cursor:
        try:
            ts, sid = base64.urlsafe_b64decode(cursor.encode()).decode().split("|")
            ts_dt, sid_u = datetime.fromisoformat(ts), uuid.UUID(sid)
        except (ValueError, UnicodeDecodeError):
            raise ApiError(422, "VALIDATION_ERROR", "Invalid cursor") from None
        q = q.where(or_(Scan.created_at < ts_dt, and_(Scan.created_at == ts_dt, Scan.id < sid_u)))
    rows = c.db.execute(q.order_by(Scan.created_at.desc(), Scan.id.desc()).limit(limit + 1)).all()
    page, more = rows[:limit], len(rows) > limit
    nxt = None
    if more and page:
        last = page[-1][0]
        nxt = base64.urlsafe_b64encode(f"{last.created_at.isoformat()}|{last.id}".encode()).decode()
    return ScanList(items=[_out(s, cat) for s, cat in page], next_cursor=nxt)


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: uuid.UUID, c: C) -> ScanOut:
    return _out(*_get(c, scan_id))


@router.patch("/{scan_id}", response_model=ScanOut)
def patch_scan(scan_id: uuid.UUID, body: ScanPatch, c: C) -> ScanOut:
    scan, cat = _get(c, scan_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(scan, k, v)
    c.db.commit()
    return _out(scan, cat)


@router.delete("/{scan_id}", status_code=204)
def delete_scan(scan_id: uuid.UUID, c: C) -> Response:
    scan, _ = _get(c, scan_id)
    storage = get_storage()
    for img in scan.images:
        storage.delete(img.storage_path)
    c.db.delete(scan)
    c.db.commit()
    return Response(status_code=204)


@router.post("/{scan_id}/images", status_code=201, response_model=ScanImageOut)
def upload_image(scan_id: uuid.UUID, c: C, file: UploadFile = File(...)) -> ScanImage:
    settings = get_settings()
    scan, _ = _get(c, scan_id)
    if scan.status not in UPLOADABLE:
        raise ApiError(409, "INVALID_STATE", f"Images cannot be added when scan is '{scan.status}'")
    if len(scan.images) >= settings.max_images_per_scan:
        raise ApiError(409, "INVALID_STATE", f"A scan can have at most {settings.max_images_per_scan} images")
    raw = file.file.read(settings.max_upload_bytes + 1)  # bounded read: never buffers more than the cap
    processed = process_upload(raw, settings)
    seq = (max((i.seq for i in scan.images), default=0)) + 1
    path = f"{c.uid}/{scan.id}/{uuid.uuid4().hex}.jpg"
    get_storage().put(path, processed.data, "image/jpeg")
    img = ScanImage(scan_id=scan.id, storage_path=path, width=processed.width, height=processed.height,
                    bytes=len(processed.data), seq=seq)
    c.db.add(img)
    scan.status = "images_uploaded"
    try:
        c.db.commit()
    except Exception:
        c.db.rollback()
        get_storage().delete(path)  # don't orphan the file if the DB write fails
        raise
    return img


def _get_image(c: C, scan_id: uuid.UUID, image_id: uuid.UUID) -> tuple[Scan, ScanImage]:
    scan, _ = _get(c, scan_id)
    img = next((i for i in scan.images if i.id == image_id), None)
    if img is None:
        raise ApiError(404, "NOT_FOUND", "Image not found")
    return scan, img


@router.delete("/{scan_id}/images/{image_id}", status_code=204)
def delete_image(scan_id: uuid.UUID, image_id: uuid.UUID, c: C) -> Response:
    scan, img = _get_image(c, scan_id, image_id)
    if scan.status not in UPLOADABLE:
        raise ApiError(409, "INVALID_STATE", f"Images cannot be removed when scan is '{scan.status}'")
    get_storage().delete(img.storage_path)
    c.db.delete(img)
    c.db.flush()
    remaining = c.db.scalar(select(func.count()).select_from(ScanImage).where(ScanImage.scan_id == scan.id))
    if not remaining:
        scan.status = "created"
    c.db.commit()
    return Response(status_code=204)


@router.get("/{scan_id}/images/{image_id}/url", response_model=SignedUrlOut)
def image_url(scan_id: uuid.UUID, image_id: uuid.UUID, c: C) -> SignedUrlOut:
    _, img = _get_image(c, scan_id, image_id)
    ttl = get_settings().signed_url_ttl_seconds
    return SignedUrlOut(url=get_storage().signed_url(img.storage_path, ttl), expires_in=ttl)
