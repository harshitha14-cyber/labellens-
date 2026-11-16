import uuid

from sqlalchemy import text

from app.storage import get_storage
from tests.conftest import jpeg_bytes


def up(user, sid, data=None, name="l.jpg"):
    return user.post(f"/scans/{sid}/images", files={"file": (name, data or jpeg_bytes(), "image/jpeg")})


def test_create_scan_matches_contract(alice, category_id):
    r = alice.post("/scans", json={"category_id": category_id})
    assert r.status_code == 201
    body = r.json()
    assert set(body) >= {"id", "status", "category", "images", "ingredients", "extraction", "warnings", "saved", "created_at"}
    assert body["status"] == "created" and body["images"] == [] and body["ingredients"] == [] and body["extraction"] is None
    assert body["category"]["slug"] == "sunscreen" and body["language"] == "en"


def test_create_scan_validation(alice):
    assert alice.post("/scans", json={}).status_code == 422
    assert alice.post("/scans", json={"category_id": "nope"}).status_code == 422
    r = alice.post("/scans", json={"category_id": str(uuid.uuid4())})
    assert r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_unsupported_language_rejected(alice, category_id):
    assert alice.post("/scans", json={"category_id": category_id, "language": "hi"}).status_code == 422


def test_idempotency_key_returns_same_scan(alice, category_id):
    h = {"Idempotency-Key": "abc-123"}
    first = alice.post("/scans", json={"category_id": category_id}, headers=h)
    second = alice.post("/scans", json={"category_id": category_id}, headers=h)
    assert first.status_code == 201 and second.status_code == 200 and first.json()["id"] == second.json()["id"]
    assert len(alice.get("/scans").json()["items"]) == 1


def test_idempotency_keys_are_per_user(alice, bob, category_id):
    h = {"Idempotency-Key": "same"}
    a = alice.post("/scans", json={"category_id": category_id}, headers=h).json()
    b = bob.post("/scans", json={"category_id": category_id}, headers=h).json()
    assert a["id"] != b["id"]


def test_get_unknown_scan_404_and_bad_uuid_422(alice):
    assert alice.get(f"/scans/{uuid.uuid4()}").status_code == 404
    assert alice.get("/scans/not-a-uuid").status_code == 422


def test_list_pagination_is_stable_and_complete(alice, category_id):
    ids = [alice.post("/scans", json={"category_id": category_id}).json()["id"] for _ in range(5)]
    seen, cursor = [], None
    for _ in range(5):
        r = alice.get("/scans", params={"limit": 2, **({"cursor": cursor} if cursor else {})}).json()
        seen += [s["id"] for s in r["items"]]
        cursor = r["next_cursor"]
        if not cursor:
            break
    assert sorted(seen) == sorted(ids) and len(seen) == len(set(seen)) == 5
    assert alice.get("/scans", params={"cursor": "garbage"}).status_code == 422
    assert alice.get("/scans", params={"limit": 0}).status_code == 422


def test_list_filters(alice, category_id):
    a = alice.post("/scans", json={"category_id": category_id}).json()["id"]
    alice.post("/scans", json={"category_id": category_id})
    alice.patch(f"/scans/{a}", json={"saved": True})
    assert [s["id"] for s in alice.get("/scans", params={"saved": True}).json()["items"]] == [a]
    assert len(alice.get("/scans", params={"saved": False}).json()["items"]) == 1


def test_patch_scan(alice, scan):
    r = alice.patch(f"/scans/{scan['id']}", json={"saved": True, "note": "bought in Chennai"})
    assert r.status_code == 200 and r.json()["saved"] is True and r.json()["note"] == "bought in Chennai"
    assert alice.patch(f"/scans/{scan['id']}", json={"note": "x" * 2001}).status_code == 422


def test_upload_moves_status_and_returns_image_meta(alice, scan):
    r = up(alice, scan["id"])
    assert r.status_code == 201
    assert set(r.json()) >= {"id", "seq", "width", "height"} and r.json()["seq"] == 1
    assert alice.get(f"/scans/{scan['id']}").json()["status"] == "images_uploaded"
    assert up(alice, scan["id"]).json()["seq"] == 2


def test_max_five_images(alice, scan):
    for _ in range(5):
        assert up(alice, scan["id"]).status_code == 201
    r = up(alice, scan["id"])
    assert r.status_code == 409 and r.json()["error"]["code"] == "INVALID_STATE"


def test_cannot_add_or_remove_images_after_processing_starts(alice, db, scan):
    img = up(alice, scan["id"]).json()
    with db.begin() as c:
        c.execute(text("update scans set status='processing' where id=:i"), {"i": scan["id"]})
    assert up(alice, scan["id"]).status_code == 409
    assert alice.delete(f"/scans/{scan['id']}/images/{img['id']}").status_code == 409


def test_deleting_last_image_resets_status(alice, scan):
    img = up(alice, scan["id"]).json()
    assert alice.delete(f"/scans/{scan['id']}/images/{img['id']}").status_code == 204
    assert alice.get(f"/scans/{scan['id']}").json()["status"] == "created"
    assert alice.delete(f"/scans/{scan['id']}/images/{img['id']}").status_code == 404


def test_delete_scan_removes_rows_and_stored_files(alice, db, scan):
    img = up(alice, scan["id"]).json()
    with db.connect() as c:
        path = c.execute(text("select storage_path from scan_images where id=:i"), {"i": img["id"]}).scalar_one()
    assert get_storage().exists(path)
    assert alice.delete(f"/scans/{scan['id']}").status_code == 204
    assert not get_storage().exists(path)
    assert alice.get(f"/scans/{scan['id']}").status_code == 404
    with db.connect() as c:
        assert c.execute(text("select count(*) from scan_images")).scalar_one() == 0
