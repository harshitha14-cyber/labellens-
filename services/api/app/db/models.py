"""SQLAlchemy models. Source of truth for the schema (Alembic migrations are generated from here).

Design reference: docs/03-ER-DIAGRAM.md. Reference/regulatory tables carry citation columns as
NOT NULL so an untraceable rule cannot be stored.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin

Json = JSON().with_variant(JSONB(), "postgresql")

def FK(target: str, **kw: Any) -> ForeignKey:
    return ForeignKey(target, **kw)



# ---------------------------------------------------------------- users / preferences
class User(Base, TimestampMixin):
    """App profile. `id` equals the Supabase auth user id (auth.users.id)."""
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    locale: Mapped[str] = mapped_column(String(10), server_default="en", nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserPreference(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_preferences"
    user_id: Mapped[uuid.UUID] = mapped_column(FK("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    include_community_products: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    items: Mapped[list["UserPreferenceItem"]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class UserPreferenceItem(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_preference_items"
    preference_id: Mapped[uuid.UUID] = mapped_column(FK("user_preferences.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(FK("ingredients.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(10), nullable=False)
    tag: Mapped[str | None] = mapped_column(String(60))
    __table_args__ = (
        CheckConstraint("kind in ('avoid','prefer')", name="kind"),
        CheckConstraint("(ingredient_id is not null) <> (tag is not null)", name="ingredient_xor_tag"),
        Index("ix_user_pref_items_pref", "preference_id"),
    )


# ---------------------------------------------------------------- reference data
class ProductCategory(Base, IdMixin, TimestampMixin):
    __tablename__ = "product_categories"
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    domain: Mapped[str] = mapped_column(String(20), server_default="cosmetics", nullable=False)
    usage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    __table_args__ = (
        CheckConstraint("domain in ('cosmetics','food')", name="domain"),
        CheckConstraint("usage_type in ('leave_on','rinse_off','sun')", name="usage_type"),
    )


class Ingredient(Base, IdMixin, TimestampMixin):
    __tablename__ = "ingredients"
    canonical_name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    inci_name: Mapped[str | None] = mapped_column(String(300))
    cas_number: Mapped[str | None] = mapped_column(String(40))
    pubchem_cid: Mapped[str | None] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(120))
    domain: Mapped[str] = mapped_column(String(20), server_default="cosmetics", nullable=False)
    synonyms: Mapped[list["IngredientSynonym"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    functions: Mapped[list["IngredientFunction"]] = relationship(secondary="ingredient_function_map", lazy="selectin")
    __table_args__ = (
        Index("uq_ingredients_cas_number", "cas_number", unique=True, postgresql_where=text("cas_number is not null")),
        Index("ix_ingredients_name_trgm", "canonical_name", postgresql_using="gin",
              postgresql_ops={"canonical_name": "gin_trgm_ops"}),
    )


class IngredientSynonym(Base, IdMixin, TimestampMixin):
    __tablename__ = "ingredient_synonyms"
    ingredient_id: Mapped[uuid.UUID] = mapped_column(FK("ingredients.id", ondelete="CASCADE"), nullable=False)
    synonym: Mapped[str] = mapped_column(String(300), nullable=False)
    synonym_normalised: Mapped[str] = mapped_column(String(300), nullable=False)
    language: Mapped[str] = mapped_column(String(10), server_default="en", nullable=False)
    kind: Mapped[str] = mapped_column(String(20), server_default="common", nullable=False)
    __table_args__ = (
        UniqueConstraint("ingredient_id", "synonym_normalised", "language", name="uq_syn_ing_norm_lang"),
        CheckConstraint("kind in ('common','inci','trade','misspelling')", name="kind"),
        Index("ix_syn_norm_trgm", "synonym_normalised", postgresql_using="gin",
              postgresql_ops={"synonym_normalised": "gin_trgm_ops"}),
    )


class IngredientFunction(Base, IdMixin, TimestampMixin):
    __tablename__ = "ingredient_functions"
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class IngredientFunctionMap(Base):
    __tablename__ = "ingredient_function_map"
    ingredient_id: Mapped[uuid.UUID] = mapped_column(FK("ingredients.id", ondelete="CASCADE"), primary_key=True)
    function_id: Mapped[uuid.UUID] = mapped_column(FK("ingredient_functions.id", ondelete="CASCADE"), primary_key=True)


class DataImport(Base, IdMixin, TimestampMixin):
    """Provenance + licence of every dataset import run."""
    __tablename__ = "data_imports"
    dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    dataset_version: Mapped[str | None] = mapped_column(String(60))
    licence: Mapped[str | None] = mapped_column(String(200))
    source_url: Mapped[str | None] = mapped_column(Text)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128))


class IngredientSource(Base, IdMixin, TimestampMixin):
    __tablename__ = "ingredient_sources"
    organisation: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    licence: Mapped[str | None] = mapped_column(String(200))
    published_on: Mapped[date | None] = mapped_column(Date)
    last_checked_on: Mapped[date] = mapped_column(Date, nullable=False)


class IngredientAssessment(Base, IdMixin, TimestampMixin):
    __tablename__ = "ingredient_assessments"
    ingredient_id: Mapped[uuid.UUID] = mapped_column(FK("ingredients.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(FK("ingredient_sources.id"))
    classification: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    context: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    assessed_on: Mapped[date] = mapped_column(Date, nullable=False)
    ruleset_version: Mapped[str | None] = mapped_column(String(60))
    __table_args__ = (
        UniqueConstraint("ingredient_id", "source_id", "context", "assessed_on", name="uq_assess_key"),
        CheckConstraint("classification between 1 and 5", name="classification"),
        CheckConstraint("confidence between 0 and 1", name="confidence"),
        # "Never label an ingredient without evidence": class 1 requires a citation.
        CheckConstraint("classification <> 1 or source_id is not null", name="class1_requires_source"),
    )


class IngredientRegulation(Base, IdMixin, TimestampMixin):
    __tablename__ = "ingredient_regulations"
    ingredient_id: Mapped[uuid.UUID] = mapped_column(FK("ingredients.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(FK("ingredient_sources.id"), nullable=False)
    import_id: Mapped[uuid.UUID | None] = mapped_column(FK("data_imports.id"))
    jurisdiction: Mapped[str] = mapped_column(String(10), nullable=False)
    regulation_name: Mapped[str] = mapped_column(String(300), nullable=False)
    provision: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    match_scope: Mapped[str] = mapped_column(String(20), server_default="exact", nullable=False)
    conditions: Mapped[str | None] = mapped_column(Text)
    warnings: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[date | None] = mapped_column(Date)
    last_checked_on: Mapped[date] = mapped_column(Date, nullable=False)
    version: Mapped[str] = mapped_column(String(60), nullable=False)
    superseded_on: Mapped[date | None] = mapped_column(Date)
    binding: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    __table_args__ = (
        UniqueConstraint("ingredient_id", "jurisdiction", "regulation_name", "provision", "version", name="uq_reg_key"),
        CheckConstraint("status in ('prohibited','restricted','conditional','listed_permitted')", name="status"),
        CheckConstraint("match_scope in ('exact','group','salt_family')", name="match_scope"),
        Index("ix_reg_jurisdiction", "jurisdiction"),
    )


# ---------------------------------------------------------------- products
class Product(Base, IdMixin, TimestampMixin):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(200))
    category_id: Mapped[uuid.UUID] = mapped_column(FK("product_categories.id"), nullable=False)
    country_of_origin: Mapped[str | None] = mapped_column(String(60))
    product_identifier: Mapped[str | None] = mapped_column(String(80))
    ingredient_list_source: Mapped[str | None] = mapped_column(Text)
    source_date: Mapped[date | None] = mapped_column(Date)
    verification_status: Mapped[str] = mapped_column(String(30), server_default="UNVERIFIED", nullable=False)
    ingredient_list_complete: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    import_id: Mapped[uuid.UUID | None] = mapped_column(FK("data_imports.id"))
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(FK("users.id", ondelete="SET NULL"))
    ingredients: Mapped[list["ProductIngredient"]] = relationship(cascade="all, delete-orphan", lazy="selectin",
                                                                  order_by="ProductIngredient.position")
    __table_args__ = (
        CheckConstraint("verification_status in ('VERIFIED','COMMUNITY_SUBMITTED','UNVERIFIED')", name="verification"),
        Index("ix_products_category", "category_id"),
        Index("ix_products_verification", "verification_status"),
        Index("uq_products_brand_name_ident", "brand", "name", "product_identifier", unique=True,
              postgresql_nulls_not_distinct=True),
        Index("ix_products_name_trgm", "name", postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"}),
    )


class ProductIngredient(Base, IdMixin):
    __tablename__ = "product_ingredients"
    product_id: Mapped[uuid.UUID] = mapped_column(FK("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(FK("ingredients.id"))
    raw_name: Mapped[str] = mapped_column(String(300), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("product_id", "position", name="uq_prod_ing_pos"),
                      Index("ix_prod_ing_ingredient", "ingredient_id"))


# ---------------------------------------------------------------- scans
class Scan(Base, IdMixin, TimestampMixin):
    __tablename__ = "scans"
    user_id: Mapped[uuid.UUID] = mapped_column(FK("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(FK("product_categories.id"), nullable=False)
    product_id: Mapped[uuid.UUID | None] = mapped_column(FK("products.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(30), server_default="created", nullable=False)
    language: Mapped[str] = mapped_column(String(10), server_default="en", nullable=False)
    saved: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(80))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    images: Mapped[list["ScanImage"]] = relationship(cascade="all, delete-orphan", lazy="selectin", order_by="ScanImage.seq")
    __table_args__ = (
        CheckConstraint("status in ('created','images_uploaded','processing','needs_confirmation','confirmed',"
                        "'analysed','ocr_failed','no_ingredients_found')", name="status"),
        Index("ix_scans_user_created", "user_id", text("created_at desc")),
        Index("ix_scans_saved", "user_id", postgresql_where=text("saved")),
        Index("uq_scans_user_idem", "user_id", "idempotency_key", unique=True,
              postgresql_where=text("idempotency_key is not null")),
    )


class ScanImage(Base, IdMixin, TimestampMixin):
    __tablename__ = "scan_images"
    scan_id: Mapped[uuid.UUID] = mapped_column(FK("scans.id", ondelete="CASCADE"), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    blur_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # computed in Milestone 3
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("scan_id", "seq", name="uq_scan_images_seq"),)


class ExtractedText(Base, IdMixin, TimestampMixin):
    __tablename__ = "extracted_text"
    scan_image_id: Mapped[uuid.UUID] = mapped_column(FK("scan_images.id", ondelete="CASCADE"), unique=True, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str | None] = mapped_column(Text)
    boxes_json: Mapped[Any | None] = mapped_column(Json)
    mean_confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    engine: Mapped[str | None] = mapped_column(String(60))
    engine_version: Mapped[str | None] = mapped_column(String(60))
    section_text: Mapped[str | None] = mapped_column(Text)
    section_complete: Mapped[bool | None] = mapped_column(Boolean)


class ScanIngredient(Base, IdMixin, TimestampMixin):
    __tablename__ = "scan_ingredients"
    scan_id: Mapped[uuid.UUID] = mapped_column(FK("scans.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_token: Mapped[str] = mapped_column(String(300), nullable=False)
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(FK("ingredients.id"))
    ocr_confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    match_method: Mapped[str] = mapped_column(String(20), server_default="none", nullable=False)
    user_status: Mapped[str] = mapped_column(String(20), server_default="pending", nullable=False)
    __table_args__ = (
        UniqueConstraint("scan_id", "position", name="uq_scan_ing_pos"),
        CheckConstraint("match_method in ('exact','synonym','fuzzy','manual','none')", name="match_method"),
        CheckConstraint("user_status in ('pending','confirmed','edited','removed','added')", name="user_status"),
        Index("ix_scan_ing_ingredient", "ingredient_id"),
    )


class ScanReport(Base, IdMixin, TimestampMixin):
    __tablename__ = "scan_reports"
    scan_id: Mapped[uuid.UUID] = mapped_column(FK("scans.id", ondelete="CASCADE"), unique=True, nullable=False)
    report_json: Mapped[Any] = mapped_column(Json, nullable=False)
    ruleset_version: Mapped[str] = mapped_column(String(60), nullable=False)
    data_snapshot: Mapped[str | None] = mapped_column(String(60))
    class_counts: Mapped[Any | None] = mapped_column(Json)
    list_complete: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)


class AlternativeProduct(Base, IdMixin, TimestampMixin):
    __tablename__ = "alternative_products"
    scan_id: Mapped[uuid.UUID] = mapped_column(FK("scans.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(FK("products.id", ondelete="CASCADE"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    reasons_json: Mapped[Any] = mapped_column(Json, nullable=False)
    __table_args__ = (UniqueConstraint("scan_id", "product_id", name="uq_alt_scan_product"),)


class ProductComparison(Base, IdMixin, TimestampMixin):
    __tablename__ = "product_comparisons"
    user_id: Mapped[uuid.UUID] = mapped_column(FK("users.id", ondelete="CASCADE"), nullable=False)
    left_scan_id: Mapped[uuid.UUID] = mapped_column(FK("scans.id", ondelete="CASCADE"), nullable=False)
    right_scan_id: Mapped[uuid.UUID | None] = mapped_column(FK("scans.id", ondelete="CASCADE"))
    right_product_id: Mapped[uuid.UUID | None] = mapped_column(FK("products.id", ondelete="CASCADE"))
    result_json: Mapped[Any | None] = mapped_column(Json)
    __table_args__ = (CheckConstraint("(right_scan_id is not null) <> (right_product_id is not null)", name="one_right"),)


class UserFavourite(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_favourites"
    user_id: Mapped[uuid.UUID] = mapped_column(FK("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID | None] = mapped_column(FK("products.id", ondelete="CASCADE"))
    scan_id: Mapped[uuid.UUID | None] = mapped_column(FK("scans.id", ondelete="CASCADE"))
    __table_args__ = (
        CheckConstraint("(product_id is not null) <> (scan_id is not null)", name="one_target"),
        Index("uq_fav_user_product", "user_id", "product_id", unique=True, postgresql_where=text("product_id is not null")),
        Index("uq_fav_user_scan", "user_id", "scan_id", unique=True, postgresql_where=text("scan_id is not null")),
    )
