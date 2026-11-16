import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CategoryOut(Out):
    id: uuid.UUID
    slug: str
    name: str
    domain: str
    usage_type: str


class ScanCreate(BaseModel):
    category_id: uuid.UUID
    language: Literal["en"] = "en"  # only English OCR until a later version


class ScanPatch(BaseModel):
    saved: bool | None = None
    note: str | None = Field(default=None, max_length=2000)
    product_id: uuid.UUID | None = None


class ScanImageOut(Out):
    id: uuid.UUID
    seq: int
    width: int
    height: int
    blur_score: float | None = None


class ScanOut(Out):
    id: uuid.UUID
    status: str
    language: str
    saved: bool
    note: str | None
    category: CategoryOut
    images: list[ScanImageOut]
    ingredients: list[dict[str, Any]] = []  # filled from Milestone 3 (OCR)
    extraction: dict[str, Any] | None = None
    warnings: list[str] = []
    created_at: datetime


class ScanList(BaseModel):
    items: list[ScanOut]
    next_cursor: str | None


class SignedUrlOut(BaseModel):
    url: str
    expires_in: int


class MeOut(Out):
    id: uuid.UUID
    display_name: str | None
    locale: str
    email: str | None = None


class MePatch(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    locale: Literal["en"] | None = None


class PrefItem(BaseModel):
    kind: Literal["avoid", "prefer"]
    ingredient_id: uuid.UUID | None = None
    tag: str | None = Field(default=None, max_length=60)


class PrefsIO(BaseModel):
    include_community_products: bool = False
    items: list[PrefItem] = []


class FavouriteIn(BaseModel):
    product_id: uuid.UUID | None = None
    scan_id: uuid.UUID | None = None


class FavouriteOut(Out):
    id: uuid.UUID
    product_id: uuid.UUID | None
    scan_id: uuid.UUID | None


class IngredientBrief(Out):
    id: uuid.UUID
    canonical_name: str
    inci_name: str | None
    cas_number: str | None


class SourceOut(Out):
    organisation: str
    title: str
    url: str
    last_checked_on: date


class AssessmentOut(BaseModel):
    classification: int
    context: str
    summary: str
    confidence: float
    assessed_on: date
    source: SourceOut | None


class RegulationOut(BaseModel):
    jurisdiction: str
    regulation_name: str
    provision: str
    status: str
    match_scope: str
    conditions: str | None
    warnings: str | None
    effective_from: date | None
    last_checked_on: date
    version: str
    binding: bool
    source: SourceOut
    reference_only: bool


class IngredientOut(BaseModel):
    id: uuid.UUID
    canonical_name: str
    inci_name: str | None
    synonyms: list[str]
    cas_number: str | None
    pubchem_cid: str | None
    category: str | None
    description: str | None
    functions: list[str]
    assessments: list[AssessmentOut]
    regulations: list[RegulationOut]  # jurisdiction IN (binding Indian status)
    reference_regulations: list[RegulationOut]  # other jurisdictions: reference only


class ProductIngredientOut(Out):
    position: int
    raw_name: str
    ingredient_id: uuid.UUID | None


class ProductOut(Out):
    id: uuid.UUID
    name: str
    brand: str | None
    category_id: uuid.UUID
    country_of_origin: str | None
    product_identifier: str | None
    ingredient_list_source: str | None
    source_date: date | None
    verification_status: str
    ingredient_list_complete: bool


class ProductDetail(ProductOut):
    ingredients: list[ProductIngredientOut]
