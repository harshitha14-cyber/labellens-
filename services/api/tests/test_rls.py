"""Row Level Security. Part 1 hits Postgres directly as the API role; part 2 goes through the HTTP API."""
import json
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError, ProgrammingError

from tests.conftest import APP_URL, jpeg_bytes


@pytest.fixture()
def app_conn(db):
    eng = create_engine(APP_URL)
    with eng.connect() as conn:
        yield conn
    eng.dispose()


def as_user(conn, uid):
    conn.execute(text("select set_config('request.jwt.claims', :c, true)"), {"c": json.dumps({"sub": uid}) if uid else ""})


@pytest.fixture()
def two_users_with_scans(db, category_id):
    a, b = str(uuid.uuid4()), str(uuid.uuid4())
    with db.begin() as c:  # owner inserts fixtures
        for u in (a, b):
            c.execute(text("insert into users (id) values (:u)"), {"u": u})
            c.execute(text("insert into scans (user_id, category_id) values (:u, :c)"), {"u": u, "c": category_id})
    return a, b


def test_api_role_cannot_bypass_rls(db):
    with db.connect() as c:
        row = c.execute(text("select rolbypassrls, rolsuper from pg_roles where rolname='ll_app'")).one()
    assert tuple(row) == (False, False)


def test_every_app_table_has_rls_enabled(db):
    with db.connect() as c:
        off = c.execute(text("""select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace
                                where n.nspname='public' and c.relkind='r' and not c.relrowsecurity
                                and relname <> 'alembic_version'""")).scalars().all()
    assert off == []


def test_user_sees_only_own_rows(app_conn, two_users_with_scans):
    a, b = two_users_with_scans
    as_user(app_conn, a)
    rows = app_conn.execute(text("select user_id::text from scans")).scalars().all()
    assert rows == [a]
    as_user(app_conn, b)
    assert app_conn.execute(text("select user_id::text from scans")).scalars().all() == [b]


def test_no_claims_means_no_rows_fail_closed(app_conn, two_users_with_scans):
    as_user(app_conn, None)
    assert app_conn.execute(text("select count(*) from scans")).scalar_one() == 0
    assert app_conn.execute(text("select count(*) from users")).scalar_one() == 0


def test_cannot_insert_row_for_another_user(app_conn, two_users_with_scans, category_id):
    a, b = two_users_with_scans
    as_user(app_conn, a)
    with pytest.raises(DBAPIError, match="row-level security"):
        app_conn.execute(text("insert into scans (user_id, category_id) values (:u, :c)"), {"u": b, "c": category_id})


def test_cannot_update_or_delete_others_rows(app_conn, two_users_with_scans):
    a, b = two_users_with_scans
    as_user(app_conn, a)
    assert app_conn.execute(text("update scans set note='x' where user_id=:b"), {"b": b}).rowcount == 0
    assert app_conn.execute(text("delete from scans where user_id=:b"), {"b": b}).rowcount == 0


def test_cannot_reassign_row_to_another_user(app_conn, two_users_with_scans):
    a, b = two_users_with_scans
    as_user(app_conn, a)
    with pytest.raises(DBAPIError, match="row-level security"):
        app_conn.execute(text("update scans set user_id=:b where user_id=:a"), {"a": a, "b": b})


def test_child_tables_inherit_scan_ownership(db, app_conn, two_users_with_scans):
    a, b = two_users_with_scans
    with db.begin() as c:
        sid_b = c.execute(text("select id from scans where user_id=:b"), {"b": b}).scalar_one()
        c.execute(text("insert into scan_images (scan_id, storage_path, width, height, bytes, seq) values (:s,'p',1,1,1,1)"), {"s": sid_b})
    as_user(app_conn, a)
    assert app_conn.execute(text("select count(*) from scan_images")).scalar_one() == 0
    with pytest.raises(DBAPIError, match="row-level security"):
        app_conn.execute(text("insert into scan_images (scan_id, storage_path, width, height, bytes, seq) values (:s,'x',1,1,1,2)"), {"s": sid_b})


def test_reference_tables_read_only_for_api_role(db, app_conn):
    as_user(app_conn, str(uuid.uuid4()))
    assert app_conn.execute(text("select count(*) from product_categories")).scalar_one() == 8
    with pytest.raises(ProgrammingError, match="permission denied"):
        app_conn.execute(text("insert into ingredients (canonical_name) values ('Evil')"))


def test_data_imports_invisible_to_api_role(app_conn):
    with pytest.raises(ProgrammingError, match="permission denied"):
        app_conn.execute(text("select * from data_imports"))


def test_user_cannot_create_verified_product(db, app_conn, category_id):
    uid = str(uuid.uuid4())
    with db.begin() as c:
        c.execute(text("insert into users (id) values (:u)"), {"u": uid})
    as_user(app_conn, uid)
    with pytest.raises(DBAPIError, match="row-level security"):
        app_conn.execute(text("insert into products (name, brand, category_id, verification_status, submitted_by) "
                              "values ('P','B',:c,'VERIFIED',:u)"), {"c": category_id, "u": uid})


def test_user_can_add_community_product_but_not_promote_it(db, app_conn, category_id):
    uid = str(uuid.uuid4())
    with db.begin() as c:
        c.execute(text("insert into users (id) values (:u)"), {"u": uid})
    as_user(app_conn, uid)
    app_conn.execute(text("insert into products (name, brand, category_id, verification_status, submitted_by) "
                          "values ('P','B',:c,'COMMUNITY_SUBMITTED',:u)"), {"c": category_id, "u": uid})
    with pytest.raises(DBAPIError, match="row-level security"):
        app_conn.execute(text("update products set verification_status='VERIFIED' where submitted_by=:u"), {"u": uid})


def test_class1_assessment_requires_a_citation(db):
    with db.begin() as c:
        ing = c.execute(text("insert into ingredients (canonical_name) values ('TestIng') returning id")).scalar_one()
    with pytest.raises(DBAPIError, match="class1_requires_source"):
        with db.begin() as c:
            c.execute(text("insert into ingredient_assessments (ingredient_id, classification, context, summary, confidence, assessed_on) "
                           "values (:i, 1, 'ctx', 's', 0.5, now())"), {"i": ing})


def test_regulation_cannot_be_stored_without_citation(db):
    with db.begin() as c:
        ing = c.execute(text("insert into ingredients (canonical_name) values ('TestIng2') returning id")).scalar_one()
    with pytest.raises(DBAPIError, match="not-null|null value"):
        with db.begin() as c:
            c.execute(text("insert into ingredient_regulations (ingredient_id, jurisdiction, regulation_name, provision, status, last_checked_on, version) "
                           "values (:i,'IN','R','P','restricted', now(), '1')"), {"i": ing})


# ---------------------------------------------------------------- through the HTTP API
def test_api_user_cannot_read_modify_or_delete_another_users_scan(alice, bob, scan):
    sid = scan["id"]
    assert bob.get(f"/scans/{sid}").status_code == 404
    assert bob.patch(f"/scans/{sid}", json={"saved": True}).status_code == 404
    assert bob.delete(f"/scans/{sid}").status_code == 404
    assert bob.get("/scans").json()["items"] == []
    assert alice.get(f"/scans/{sid}").status_code == 200  # still intact


def test_api_user_cannot_upload_to_or_sign_urls_for_another_users_scan(alice, bob, scan):
    sid = scan["id"]
    img = alice.post(f"/scans/{sid}/images", files={"file": ("a.jpg", jpeg_bytes(), "image/jpeg")}).json()
    r = bob.post(f"/scans/{sid}/images", files={"file": ("b.jpg", jpeg_bytes(), "image/jpeg")})
    assert r.status_code == 404
    assert bob.get(f"/scans/{sid}/images/{img['id']}/url").status_code == 404
    assert bob.delete(f"/scans/{sid}/images/{img['id']}").status_code == 404


def test_api_user_cannot_favourite_another_users_scan(alice, bob, scan):
    assert bob.post("/me/favourites", json={"scan_id": scan["id"]}).status_code == 404


def test_api_users_have_separate_preferences(alice, bob):
    alice.put("/me/preferences", json={"include_community_products": True, "items": [{"kind": "avoid", "tag": "fragrance"}]})
    assert bob.get("/me/preferences").json() == {"include_community_products": False, "items": []}
