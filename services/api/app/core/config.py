from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://ll_app:ll_app_dev@localhost:5432/labellens"
    migration_database_url: str = "postgresql+psycopg://ll_owner:ll_owner_dev@localhost:5432/labellens"

    supabase_jwt_secret: str = ""
    supabase_jwks_url: str = ""
    jwt_audience: str = "authenticated"

    storage_backend: str = "local"  # local | supabase
    local_storage_dir: str = "./.storage"
    storage_signing_secret: str = "dev-only-signing-secret"
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    storage_bucket: str = "scan-images"
    signed_url_ttl_seconds: int = 300

    max_upload_bytes: int = 10 * 1024 * 1024
    min_short_side_px: int = 600
    max_long_side_px: int = 2000
    max_images_per_scan: int = 5

    api_version: str = "0.2.0"
    ruleset_version: str = "none-yet"  # real ruleset arrives in Milestone 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
