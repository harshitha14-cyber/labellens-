import io
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import jwt
import pytest
from PIL import Image
from sqlalchemy import create_engine, text

TEST_SECRET = "test-secret-test-secret-test-secret-12345"
OWNER_URL = os.environ.get("TEST_OWNER_URL", "postgresql+psycopg://ll_owner:ll_owner_dev@localhost:5432/labellens_test")
APP_URL = os.environ.get("TEST_APP_URL", "postgresql+psycopg://ll_app:ll_app_dev@localhost:5432/labellens_test")
STORAGE_DIR = tempfile.mkdtemp(prefix="ll-test-storage-")

# Must be set BEFORE the app (and its cached settings) are imported.
os.environ.update({
    "DATABASE_URL": APP_URL, "MIGRATION_DATABASE_URL": OWNER_URL, "SUPABASE_JWT_SECRET": TEST_SECRET,
    "SUPABASE_JWKS_URL": "", "JWT_AUDIENCE": "authenticated", "STORAGE_BACKEND": "local",
    "LOCAL_STORAGE_DIR": STORAGE_DIR, "STORAGE_SIGNING_SECRET": "test-signing-secret",
})

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from data_pipeline.seed_dev import seed_categories  # noqa: E402

API_DIR = Path(__file__).resolve().parent.parent
USER_TABLES = ("users", "scans", "products", "ingredients", "ingredient_sources", "data_imports",
               "ingredient_functions", "product_categories")


def alembic(*args: str, url: str = OWNER_URL) -> None:
    env = {**os.environ, "ALEMBIC_DATABASE_URL": url}
    subprocess.run([sys.executable, "-m", "alembic", *args], cwd=API_DIR, env=env, check=True, capture_output=True)


@pytest.fixture(scope="session")
def owner_engine():
    alembic("downgrade", "base")
    alembic("upgrade", "head")
    eng = create_engine(OWNER_URL)
    yield eng
    eng.dispose()


@pytest.fixture()
def db(owner_engine):
    """Clean, seeded database for every test (seeding runs as the schema owner)."""
    with owner_engine.begin() as c:
        c.execute(text("truncate " + ", ".join(USER_TABLES) + " restart identity cascade"))
        seed_categories(c)
    return owner_engine


def make_token(sub: str | None = None, *, secret: str = TEST_SECRET, aud: str = "authenticated", ttl: int = 3600,
               alg: str = "HS256", role: str | None = "authenticated", email: str | None = None, extra: dict | None = None) -> str:
    claims: dict = {"aud": aud, "exp": int(time.time()) + ttl, "iat": int(time.time()) - 5}
    if sub is not None:
        claims["sub"] = sub
    if role:
        claims["role"] = role
    if email:
        claims["email"] = email
    claims.update(extra or {})
    return jwt.encode(claims, secret, algorithm=alg)


class UserClient:
    def __init__(self, client: TestClient, uid: str) -> None:
        self.c, self.uid = client, uid
        self.h = {"Authorization": f"Bearer {make_token(uid, email=f'{uid[:6]}@example.com')}"}

    def get(self, url, **kw): return self.c.get("/api/v1" + url, headers=self.h, **kw)
    def post(self, url, **kw): return self.c.post("/api/v1" + url, headers={**self.h, **kw.pop("headers", {})}, **kw)
    def put(self, url, **kw): return self.c.put("/api/v1" + url, headers=self.h, **kw)
    def patch(self, url, **kw): return self.c.patch("/api/v1" + url, headers=self.h, **kw)
    def delete(self, url, **kw): return self.c.delete("/api/v1" + url, headers=self.h, **kw)


@pytest.fixture()
def client(db):
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def alice(client): return UserClient(client, str(uuid.uuid4()))


@pytest.fixture()
def bob(client): return UserClient(client, str(uuid.uuid4()))


def jpeg_bytes(w=800, h=1000, *, exif_gps=False, orientation=None, fmt="JPEG") -> bytes:
    img = Image.effect_noise((w, h), 60).convert("RGB")
    out = io.BytesIO()
    kwargs = {}
    if exif_gps or orientation:
        ex = Image.Exif()
        if orientation:
            ex[0x0112] = orientation
        if exif_gps:
            ex[0x010F] = "SecretPhoneMaker"  # Make
            ex[0x8825] = {1: "N", 2: (13.0, 4.0, 59.0), 3: "E", 4: (80.0, 16.0, 12.0)}  # GPS IFD (Chennai-ish)
        kwargs["exif"] = ex
    img.save(out, format=fmt, **kwargs)
    return out.getvalue()


@pytest.fixture()
def category_id(db):
    with db.connect() as c:
        return str(c.execute(text("select id from product_categories where slug='sunscreen'")).scalar_one())


@pytest.fixture()
def scan(alice, category_id):
    return alice.post("/scans", json={"category_id": category_id}).json()
