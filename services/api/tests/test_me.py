import uuid

from sqlalchemy import text


def test_profile_created_on_first_request(alice, db):
    r = alice.get("/me")
    assert r.status_code == 200 and r.json()["id"] == alice.uid and r.json()["email"].endswith("@example.com")
    with db.connect() as c:
        assert c.execute(text("select count(*) from users where id=:i"), {"i": alice.uid}).scalar_one() == 1
    alice.get("/me"); alice.get("/me")  # idempotent
    with db.connect() as c:
        assert c.execute(text("select count(*) from users")).scalar_one() == 1


def test_patch_me(alice):
    r = alice.patch("/me", json={"display_name": "Harsha"})
    assert r.status_code == 200 and r.json()["display_name"] == "Harsha"
    assert alice.patch("/me", json={"display_name": "x" * 121}).status_code == 422
    assert alice.patch("/me", json={"locale": "fr"}).status_code == 422


def test_delete_me_schedules_deletion_and_blocks_further_use(alice, db):
    r = alice.delete("/me")
    assert r.status_code == 202 and r.json()["status"] == "deletion_scheduled"
    assert alice.get("/me").status_code == 403 and alice.get("/scans").status_code == 403
    with db.connect() as c:
        assert c.execute(text("select deleted_at is not null from users where id=:i"), {"i": alice.uid}).scalar_one()


def seed_ingredient(db, name="Glycerin"):
    with db.begin() as c:
        return str(c.execute(text("insert into ingredients (canonical_name) values (:n) returning id"), {"n": name}).scalar_one())


def test_preferences_roundtrip(alice, db):
    ing = seed_ingredient(db)
    body = {"include_community_products": True, "items": [{"kind": "avoid", "ingredient_id": ing}, {"kind": "prefer", "tag": "fragrance-free"}]}
    assert alice.put("/me/preferences", json=body).status_code == 200
    got = alice.get("/me/preferences").json()
    assert got["include_community_products"] is True and len(got["items"]) == 2
    # PUT replaces, never appends
    alice.put("/me/preferences", json={"include_community_products": False, "items": []})
    assert alice.get("/me/preferences").json() == {"include_community_products": False, "items": []}


def test_preferences_validation(alice, db):
    assert alice.put("/me/preferences", json={"items": [{"kind": "avoid"}]}).status_code == 422
    assert alice.put("/me/preferences", json={"items": [{"kind": "avoid", "tag": "a", "ingredient_id": str(uuid.uuid4())}]}).status_code == 422
    assert alice.put("/me/preferences", json={"items": [{"kind": "hate", "tag": "a"}]}).status_code == 422
    r = alice.put("/me/preferences", json={"items": [{"kind": "avoid", "ingredient_id": str(uuid.uuid4())}]})
    assert r.status_code == 422 and "unknown" in r.json()["error"]["details"]


def test_favourites_crud_and_duplicates(alice, scan):
    r = alice.post("/me/favourites", json={"scan_id": scan["id"]})
    assert r.status_code == 201
    fid = r.json()["id"]
    assert alice.post("/me/favourites", json={"scan_id": scan["id"]}).status_code == 409
    assert [f["id"] for f in alice.get("/me/favourites").json()] == [fid]
    assert alice.delete(f"/me/favourites/{fid}").status_code == 204
    assert alice.delete(f"/me/favourites/{fid}").status_code == 404
    assert alice.get("/me/favourites").json() == []


def test_favourite_needs_exactly_one_target(alice, scan):
    assert alice.post("/me/favourites", json={}).status_code == 422
    assert alice.post("/me/favourites", json={"scan_id": scan["id"], "product_id": str(uuid.uuid4())}).status_code == 422
    assert alice.post("/me/favourites", json={"product_id": str(uuid.uuid4())}).status_code == 404


def test_cannot_delete_another_users_favourite(alice, bob, scan):
    fid = alice.post("/me/favourites", json={"scan_id": scan["id"]}).json()["id"]
    assert bob.delete(f"/me/favourites/{fid}").status_code == 404
    assert len(alice.get("/me/favourites").json()) == 1
