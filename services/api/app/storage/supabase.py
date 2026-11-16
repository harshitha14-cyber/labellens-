"""Supabase Storage adapter (REST). NOT exercised against a real Supabase project in Milestone 2:
there is no Docker/Supabase stack in the build environment. It is isolated behind the Storage
protocol and covered only by a mocked-transport unit test; verify on your machine (see docs)."""
import httpx


class SupabaseStorage:
    def __init__(self, url: str, service_key: str, bucket: str, client: httpx.Client | None = None) -> None:
        self.base = url.rstrip("/") + "/storage/v1"
        self.bucket = bucket
        headers = {"Authorization": f"Bearer {service_key}", "apikey": service_key}
        self.http = client or httpx.Client(timeout=20, headers=headers)

    def put(self, path: str, data: bytes, content_type: str) -> None:
        r = self.http.post(f"{self.base}/object/{self.bucket}/{path}", content=data,
                           headers={"Content-Type": content_type, "x-upsert": "true"})
        r.raise_for_status()

    def delete(self, path: str) -> None:
        r = self.http.request("DELETE", f"{self.base}/object/{self.bucket}", json={"prefixes": [path]})
        r.raise_for_status()

    def signed_url(self, path: str, ttl_seconds: int) -> str:
        r = self.http.post(f"{self.base}/object/sign/{self.bucket}/{path}", json={"expiresIn": ttl_seconds})
        r.raise_for_status()
        return str(self.base + r.json()["signedURL"])
