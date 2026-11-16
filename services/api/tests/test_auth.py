import time
import uuid

import jwt
import pytest

from tests.conftest import make_token


def get_with(client, token):
    return client.get("/api/v1/categories", headers={"Authorization": f"Bearer {token}"} if token else {})


def test_health_and_meta_are_public(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    meta = client.get("/api/v1/meta").json()
    assert meta["ocr_languages"] == ["en"] and "api_version" in meta


def test_missing_token_401_with_error_envelope(client):
    r = get_with(client, None)
    assert r.status_code == 401
    err = r.json()["error"]
    assert err["code"] == "UNAUTHENTICATED" and err["request_id"]
    assert r.headers["x-request-id"] == err["request_id"]


@pytest.mark.parametrize("bad", ["garbage", "a.b.c", ""])
def test_malformed_token_401(client, bad):
    assert get_with(client, bad).status_code == 401


def test_valid_token_ok(client, db):
    assert get_with(client, make_token(str(uuid.uuid4()))).status_code == 200


def test_expired_token_401(client, db):
    r = get_with(client, make_token(str(uuid.uuid4()), ttl=-60))
    assert r.status_code == 401 and r.json()["error"]["message"] == "Token expired"


def test_forged_signature_401(client, db):
    assert get_with(client, make_token(str(uuid.uuid4()), secret="x" * 40)).status_code == 401


def test_wrong_audience_401(client, db):
    assert get_with(client, make_token(str(uuid.uuid4()), aud="someone-else")).status_code == 401


def test_alg_none_rejected(client, db):
    tok = jwt.encode({"sub": str(uuid.uuid4()), "aud": "authenticated", "exp": int(time.time()) + 600}, key=None, algorithm="none")
    assert get_with(client, tok).status_code == 401


def test_other_hmac_algorithm_rejected(client, db):
    assert get_with(client, make_token(str(uuid.uuid4()), alg="HS512")).status_code == 401


def test_missing_sub_rejected(client, db):
    assert get_with(client, make_token(None)).status_code == 401


def test_service_role_token_not_accepted_as_user(client, db):
    assert get_with(client, make_token(str(uuid.uuid4()), role="service_role")).status_code == 401


def test_non_uuid_subject_rejected(client, db):
    assert get_with(client, make_token("not-a-uuid")).status_code == 401


def test_every_non_public_route_requires_auth(client, db):
    paths = client.get("/openapi.json").json()["paths"]
    checked = 0
    for path, ops in paths.items():
        if path.endswith(("/health", "/meta")):
            continue
        for method in ops:
            url = path.replace("{scan_id}", str(uuid.uuid4())).replace("{image_id}", str(uuid.uuid4())) \
                      .replace("{ingredient_id}", str(uuid.uuid4())).replace("{product_id}", str(uuid.uuid4())) \
                      .replace("{fav_id}", str(uuid.uuid4()))
            r = client.request(method.upper(), url)
            assert r.status_code == 401, f"{method.upper()} {path} -> {r.status_code}"
            checked += 1
    assert checked >= 18
