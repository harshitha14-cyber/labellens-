import time
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app.storage.local import LocalStorage, sign
from app.storage.supabase import SupabaseStorage
from tests.conftest import jpeg_bytes


def signed(alice, scan):
    img = alice.post(f"/scans/{scan['id']}/images", files={"file": ("a.jpg", jpeg_bytes(), "image/jpeg")}).json()
    return alice.get(f"/scans/{scan['id']}/images/{img['id']}/url").json()


def test_signed_url_serves_image_without_auth_header(client, alice, scan):
    out = signed(alice, scan)
    assert out["expires_in"] == 300 and out["url"].startswith("/api/v1/files/")
    r = client.get(out["url"])  # no Authorization header: the signature is the credential
    assert r.status_code == 200 and r.headers["content-type"] == "image/jpeg" and r.content[:2] == b"\xff\xd8"


def test_tampered_signature_rejected(client, alice, scan):
    url = signed(alice, scan)["url"]
    assert client.get(url[:-4] + "0000").status_code == 403


def test_tampered_path_rejected(client, alice, scan):
    url = signed(alice, scan)["url"]
    assert client.get(url.replace(".jpg", ".png")).status_code == 403


def test_extended_expiry_rejected(client, alice, scan):
    url = signed(alice, scan)["url"]
    q = parse_qs(urlparse(url).query)
    forged = url.replace(f"exp={q['exp'][0]}", f"exp={int(q['exp'][0]) + 99999}")
    assert client.get(forged).status_code == 403


def test_expired_url_rejected(client, alice, db, scan):
    from sqlalchemy import text

    from app.storage import get_storage
    img = alice.post(f"/scans/{scan['id']}/images", files={"file": ("a.jpg", jpeg_bytes(), "image/jpeg")}).json()
    with db.connect() as c:
        path = c.execute(text("select storage_path from scan_images where id=:i"), {"i": img["id"]}).scalar_one()
    expired = get_storage().signed_url(path, -10)
    r = client.get(expired)
    assert r.status_code == 403 and r.json()["error"]["message"] == "Link expired"


def test_files_are_not_readable_unsigned(client, alice, scan):
    url = signed(alice, scan)["url"].split("?")[0]
    assert client.get(url).status_code == 422  # signature params required


def test_path_traversal_blocked(client, tmp_path):
    st = LocalStorage(str(tmp_path / "root"), "s")
    (tmp_path / "secret.txt").write_text("top secret")
    with pytest.raises(ValueError):
        st.put("../secret.txt", b"x", "text/plain")
    exp = int(time.time()) + 60
    r = client.get("/api/v1/files/../../etc/passwd", params={"exp": exp, "sig": sign("test-signing-secret", "../../etc/passwd", exp)})
    assert r.status_code in (403, 404)


def test_local_storage_roundtrip_and_delete(tmp_path):
    st = LocalStorage(str(tmp_path), "s")
    st.put("u/s/a.jpg", b"abc", "image/jpeg")
    assert st.exists("u/s/a.jpg") and st.read("u/s/a.jpg") == b"abc"
    st.delete("u/s/a.jpg"); st.delete("u/s/a.jpg")  # idempotent
    assert not st.exists("u/s/a.jpg")


def test_supabase_adapter_request_shapes_with_mocked_transport():
    """MOCK ONLY: proves we call the documented endpoints with the service key. It does NOT prove a real Supabase accepts them."""
    seen = []
    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.path, req.headers.get("authorization")))
        if "/object/sign/" in req.url.path:
            return httpx.Response(200, json={"signedURL": "/object/sign/scan-images/u/s/a.jpg?token=T"})
        return httpx.Response(200, json={})
    client = httpx.Client(transport=httpx.MockTransport(handler), headers={"Authorization": "Bearer KEY", "apikey": "KEY"})
    st = SupabaseStorage("https://x.supabase.co", "KEY", "scan-images", client=client)
    st.put("u/s/a.jpg", b"1", "image/jpeg"); st.delete("u/s/a.jpg")
    url = st.signed_url("u/s/a.jpg", 300)
    assert url == "https://x.supabase.co/storage/v1/object/sign/scan-images/u/s/a.jpg?token=T"
    assert [(m, p) for m, p, _ in seen] == [("POST", "/storage/v1/object/scan-images/u/s/a.jpg"),
                                             ("DELETE", "/storage/v1/object/scan-images"),
                                             ("POST", "/storage/v1/object/sign/scan-images/u/s/a.jpg")]
    assert all(a == "Bearer KEY" for _, _, a in seen)
