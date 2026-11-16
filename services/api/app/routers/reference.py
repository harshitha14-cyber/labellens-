import uuid

from fastapi import APIRouter, Query
from sqlalchemy import func, or_, select

from app.core.errors import ApiError
from app.db.models import Ingredient, IngredientAssessment, IngredientRegulation, IngredientSource, IngredientSynonym, ProductCategory
from app.routers.deps import C
from app.schemas import AssessmentOut, CategoryOut, IngredientBrief, IngredientOut, RegulationOut, SourceOut

router = APIRouter(tags=["reference"])


@router.get("/categories", response_model=list[CategoryOut])
def categories(c: C) -> list[ProductCategory]:
    q = select(ProductCategory).where(ProductCategory.active, ProductCategory.domain == "cosmetics").order_by(ProductCategory.name)
    return list(c.db.scalars(q))


@router.get("/ingredients/search", response_model=list[IngredientBrief])
def search_ingredients(c: C, q: str = Query(min_length=2, max_length=100), limit: int = Query(20, ge=1, le=50)) -> list[Ingredient]:
    term = q.strip().lower()
    syn_ids = select(IngredientSynonym.ingredient_id).where(IngredientSynonym.synonym_normalised.ilike(f"%{term}%"))
    stmt = (select(Ingredient)
            .where(or_(func.lower(Ingredient.canonical_name).like(f"%{term}%"),
                       func.lower(func.coalesce(Ingredient.inci_name, "")).like(f"%{term}%"),
                       Ingredient.id.in_(syn_ids)))
            .order_by(func.similarity(func.lower(Ingredient.canonical_name), term).desc(), Ingredient.canonical_name)
            .limit(limit))
    return list(c.db.scalars(stmt))


def _src(s: IngredientSource) -> SourceOut:
    return SourceOut(organisation=s.organisation, title=s.title, url=s.url, last_checked_on=s.last_checked_on)


@router.get("/ingredients/{ingredient_id}", response_model=IngredientOut)
def get_ingredient(ingredient_id: uuid.UUID, c: C) -> IngredientOut:
    ing = c.db.get(Ingredient, ingredient_id)
    if ing is None:
        raise ApiError(404, "NOT_FOUND", "Ingredient not found")
    assess = c.db.execute(select(IngredientAssessment, IngredientSource)
                          .join(IngredientSource, IngredientSource.id == IngredientAssessment.source_id, isouter=True)
                          .where(IngredientAssessment.ingredient_id == ing.id)
                          .order_by(IngredientAssessment.assessed_on.desc())).all()
    regs = c.db.execute(select(IngredientRegulation, IngredientSource)
                        .join(IngredientSource, IngredientSource.id == IngredientRegulation.source_id)
                        .where(IngredientRegulation.ingredient_id == ing.id, IngredientRegulation.superseded_on.is_(None))).all()
    def reg(r: IngredientRegulation, s: IngredientSource) -> RegulationOut:
        return RegulationOut(jurisdiction=r.jurisdiction, regulation_name=r.regulation_name, provision=r.provision,
                             status=r.status, match_scope=r.match_scope, conditions=r.conditions, warnings=r.warnings,
                             effective_from=r.effective_from, last_checked_on=r.last_checked_on, version=r.version,
                             binding=r.binding, source=_src(s), reference_only=r.jurisdiction != "IN")
    all_regs = [reg(r, s) for r, s in regs]
    return IngredientOut(
        id=ing.id, canonical_name=ing.canonical_name, inci_name=ing.inci_name, cas_number=ing.cas_number,
        pubchem_cid=ing.pubchem_cid, category=ing.category, description=ing.description,
        synonyms=sorted(s.synonym for s in ing.synonyms), functions=sorted(f.slug for f in ing.functions),
        assessments=[AssessmentOut(classification=a.classification, context=a.context, summary=a.summary,
                                   confidence=float(a.confidence), assessed_on=a.assessed_on,
                                   source=_src(s) if s else None) for a, s in assess],
        regulations=[r for r in all_regs if not r.reference_only],
        reference_regulations=[r for r in all_regs if r.reference_only])
