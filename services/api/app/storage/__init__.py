from functools import lru_cache

from app.core.config import get_settings
from app.storage.base import Storage
from app.storage.local import LocalStorage
from app.storage.supabase import SupabaseStorage


@lru_cache
def get_storage() -> Storage:
    s = get_settings()
    if s.storage_backend == "supabase":
        return SupabaseStorage(s.supabase_url, s.supabase_service_role_key, s.storage_bucket)
    return LocalStorage(s.local_storage_dir, s.storage_signing_secret)
