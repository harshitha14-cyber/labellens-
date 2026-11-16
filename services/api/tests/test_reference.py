"""Reference endpoints. Rows below are TEST FIXTURES with obviously fake citations, not real assessments."""
import pytest
from sqlalchemy import text


@pytest.fixture()
def fixtures(db, category_id):
    with db.begin() as c:
        src = c.execute(text("insert into ingredient_sources (organisation,title,url,last_checked_on) "
                             "values ('TEST ORG','TEST TITLE','https://example.org/test','2026-11-01') returning id")).scalar_one()
        ing = c.execute(text("insert into ingredients (canonical_name, inci_name, cas_number) values ('Test Zinc','Test Zinc Oxide','1314-13-2') returning id")).scalar_one()
        c.execute(text("insert into ingredient_synonyms (ingredient_id, synonym, synonym_normalised) values (:i,'TZ','tz')"), {"i": ing})
        fn = c.execute(text("insert into ingredient_functions (slug,name) values ('uv_filter','UV filter') returning id")).scalar_one()
        c.execute(text("insert into ingredient_function_map values (:i,:f)"), {"i": ing, "f": fn})
        c.execute(text("insert into ingredient_assessments (ingredient_id,source_id,classification,context,summary,confidence,assessed_on) "
                       "values (:i,:s,5,'sun','TEST summary',0.7,'2026-11-01')"), {"i": ing, "s": src})
        for j, name in (("IN", "TEST IN REGULATION"), ("EU", "TEST EU REGULATION")):
            c.execute(text("insert into ingredient_regulations (ingredient_id,source_id,jurisdiction,regulation_name,provision,status,last_checked_on,version) "
                           "values (:i,:s,:j,:n,'TEST PROVISION','conditional','2026-11-01','v1')"), {"i": ing, "s": src, "j": j, "n": name})
        prod = c.execute(text("insert into products (name,brand,category_id,verification_status) values ('Test Sunscreen','Test Brand',:c,'VERIFIED') returning id"), {"c": category_id}).scalar_one()
        c.execute(text("insert into product_ingredients (product_id, ingredient_id, raw_name, position) values (:p,:i,'Test Zinc',1)"), {"p": prod, "i": ing})
    return {"ing": str(ing), "prod": str(prod)}


def test_categories_returns_the_eight_cosmetic_categories(alice):
    cats = alice.get("/categories").json()
    assert len(cats) == 8 and {c["slug"] for c in cats} >= {"sunscreen", "shampoo", "makeup"}
    assert all(c["domain"] == "cosmetics" for c in cats)


def test_inactive_and_food_categories_hidden(alice, db):
    with db.begin() as c:
        c.execute(text("insert into product_categories (slug,name,domain,usage_type) values ('snacks','Snacks','food','leave_on')"))
        c.execute(text("update product_categories set active=false where slug='makeup'"))
    slugs = {c["slug"] for c in alice.get("/categories").json()}
    assert "snacks" not in slugs and "makeup" not in slugs and len(slugs) == 7


def test_ingredient_search_by_name_inci_and_synonym(alice, fixtures):
    for q in ("zinc", "ZINC OXIDE", "tz"):
        hits = alice.get("/ingredients/search", params={"q": q}).json()
        assert [h["id"] for h in hits] == [fixtures["ing"]], q
    assert alice.get("/ingredients/search", params={"q": "nothing-here"}).json() == []
    assert alice.get("/ingredients/search", params={"q": "z"}).status_code == 422


def test_ingredient_detail_separates_indian_from_reference_regulation(alice, fixtures):
    r = alice.get(f"/ingredients/{fixtures['ing']}").json()
    assert r["functions"] == ["uv_filter"] and r["synonyms"] == ["TZ"]
    assert [x["regulation_name"] for x in r["regulations"]] == ["TEST IN REGULATION"]
    assert [x["regulation_name"] for x in r["reference_regulations"]] == ["TEST EU REGULATION"]
    assert all(x["reference_only"] is False for x in r["regulations"])
    assert all(x["reference_only"] is True for x in r["reference_regulations"])
    # every regulation carries its citation
    assert all(x["source"]["url"] and x["last_checked_on"] and x["provision"] for x in r["regulations"] + r["reference_regulations"])
    assert r["assessments"][0]["source"]["organisation"] == "TEST ORG"


def test_superseded_regulations_are_not_returned(alice, db, fixtures):
    with db.begin() as c:
        c.execute(text("update ingredient_regulations set superseded_on='2026-11-02' where jurisdiction='IN'"))
    assert alice.get(f"/ingredients/{fixtures['ing']}").json()["regulations"] == []


def test_unknown_ingredient_404(alice, db):
    import uuid
    assert alice.get(f"/ingredients/{uuid.uuid4()}").status_code == 404


def test_products_list_filter_and_detail(alice, fixtures, category_id):
    assert [p["name"] for p in alice.get("/products", params={"q": "sunscreen"}).json()] == ["Test Sunscreen"]
    assert alice.get("/products", params={"verification": "UNVERIFIED"}).json() == []
    assert alice.get("/products", params={"verification": "BOGUS"}).status_code == 422
    d = alice.get(f"/products/{fixtures['prod']}").json()
    assert d["verification_status"] == "VERIFIED" and d["ingredients"][0]["raw_name"] == "Test Zinc"
