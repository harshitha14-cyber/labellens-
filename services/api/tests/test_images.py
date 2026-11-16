import io

from PIL import Image

from app.storage import get_storage
from tests.conftest import jpeg_bytes


def upload(user, sid, data, name="x.jpg", ctype="image/jpeg"):
    return user.post(f"/scans/{sid}/images", files={"file": (name, data, ctype)})


def stored(db, image_id):
    from sqlalchemy import text
    with db.connect() as c:
        path = c.execute(text("select storage_path from scan_images where id=:i"), {"i": image_id}).scalar_one()
    return get_storage().read(path)


def test_exif_gps_and_camera_make_are_stripped(alice, db, scan):
    raw = jpeg_bytes(exif_gps=True)
    assert Image.open(io.BytesIO(raw)).getexif().get(0x8825), "fixture must contain GPS"
    r = upload(alice, scan["id"], raw)
    assert r.status_code == 201
    out = Image.open(io.BytesIO(stored(db, r.json()["id"])))
    exif = out.getexif()
    assert len(exif) == 0 and not exif.get(0x8825) and not exif.get(0x010F)
    assert b"SecretPhoneMaker" not in stored(db, r.json()["id"])


def test_exif_orientation_applied_before_stripping(alice, db, scan):
    raw = jpeg_bytes(w=800, h=1000, orientation=6)  # 6 = rotate 90 CW
    r = upload(alice, scan["id"], raw).json()
    assert (r["width"], r["height"]) == (1000, 800)
    assert Image.open(io.BytesIO(stored(db, r["id"]))).size == (1000, 800)


def test_large_image_downscaled_to_max_long_side(alice, scan):
    r = upload(alice, scan["id"], jpeg_bytes(w=3000, h=2400)).json()
    assert max(r["width"], r["height"]) == 2000 and r["width"] / r["height"] == 2000 / 1600


def test_png_and_webp_accepted_and_stored_as_jpeg(alice, db, scan):
    for fmt in ("PNG", "WEBP"):
        r = upload(alice, scan["id"], jpeg_bytes(fmt=fmt), name=f"a.{fmt.lower()}", ctype=f"image/{fmt.lower()}")
        assert r.status_code == 201, fmt
        assert Image.open(io.BytesIO(stored(db, r.json()["id"]))).format == "JPEG"


def test_too_small_rejected(alice, scan):
    r = upload(alice, scan["id"], jpeg_bytes(w=500, h=900))
    assert r.status_code == 422 and r.json()["error"]["code"] == "IMAGE_TOO_SMALL"
    assert r.json()["error"]["details"] == {"width": 500, "height": 900}


def test_non_image_rejected_regardless_of_extension_and_content_type(alice, scan):
    r = upload(alice, scan["id"], b"<?php system($_GET['c']); ?>", name="shell.jpg")
    assert r.status_code == 415 and r.json()["error"]["code"] == "UNSUPPORTED_MEDIA"


def test_unsupported_formats_rejected(alice, scan):
    buf = io.BytesIO(); Image.new("RGB", (800, 800)).save(buf, "GIF")
    assert upload(alice, scan["id"], buf.getvalue(), "a.gif", "image/gif").status_code == 415
    buf = io.BytesIO(); Image.new("RGB", (800, 800)).save(buf, "BMP")
    assert upload(alice, scan["id"], buf.getvalue(), "a.bmp", "image/bmp").status_code == 415


def test_truncated_jpeg_rejected(alice, scan):
    assert upload(alice, scan["id"], jpeg_bytes()[:400]).status_code == 415


def test_empty_file_rejected(alice, scan):
    assert upload(alice, scan["id"], b"").status_code == 422


def test_oversize_rejected_with_413(alice, scan):
    assert upload(alice, scan["id"], b"\xff\xd8\xff" + b"0" * (10 * 1024 * 1024 + 10)).status_code == 413


def test_polyglot_trailing_payload_is_dropped(alice, db, scan):
    payload = b"<script>alert(1)</script>MALICIOUS_TRAILER"
    r = upload(alice, scan["id"], jpeg_bytes() + payload)
    assert r.status_code == 201
    assert b"MALICIOUS_TRAILER" not in stored(db, r.json()["id"])


def test_missing_file_field_422(alice, scan):
    assert alice.post(f"/scans/{scan['id']}/images").status_code == 422


def test_storage_path_is_namespaced_by_user_and_scan(alice, db, scan):
    from sqlalchemy import text
    r = upload(alice, scan["id"], jpeg_bytes()).json()
    with db.connect() as c:
        path = c.execute(text("select storage_path from scan_images where id=:i"), {"i": r["id"]}).scalar_one()
    assert path.startswith(f"{alice.uid}/{scan['id']}/") and path.endswith(".jpg")
