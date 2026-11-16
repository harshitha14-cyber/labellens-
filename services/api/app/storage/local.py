"""Filesystem storage for dev/test. Files are private: the only way to read one is a
short-lived HMAC-signed URL served by /api/v1/files/{path}."""
import hashlib
import hmac
import time
from pathlib import Path
from urllib.parse import quote


def sign(secret: str, path: str, exp: int) -> str:
    return hmac.new(secret.encode(), f"{path}|{exp}".encode(), hashlib.sha256).hexdigest()


class LocalStorage:
    def __init__(self, root: str, secret: str, base_url: str = "/api/v1/files") -> None:
        self.root, self.secret, self.base_url = Path(root).resolve(), secret, base_url
        self.root.mkdir(parents=True, exist_ok=True)

    def _full(self, path: str) -> Path:
        full = (self.root / path).resolve()
        if self.root not in full.parents:  # blocks ../ traversal
            raise ValueError("invalid storage path")
        return full

    def put(self, path: str, data: bytes, content_type: str) -> None:
        full = self._full(path)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)

    def read(self, path: str) -> bytes:
        return self._full(path).read_bytes()

    def exists(self, path: str) -> bool:
        return self._full(path).is_file()

    def delete(self, path: str) -> None:
        self._full(path).unlink(missing_ok=True)

    def signed_url(self, path: str, ttl_seconds: int) -> str:
        exp = int(time.time()) + ttl_seconds
        return f"{self.base_url}/{quote(path)}?exp={exp}&sig={sign(self.secret, path, exp)}"
