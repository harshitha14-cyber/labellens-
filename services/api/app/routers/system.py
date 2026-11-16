from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/meta")
def meta() -> dict[str, object]:
    s = get_settings()
    return {"api_version": s.api_version, "ruleset_version": s.ruleset_version,
            "data_snapshot": None, "ocr_languages": ["en"]}
