from fastapi import FastAPI

from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.routers import files, me, products, reference, scans, system

app = FastAPI(title="LabelLens India API", version=get_settings().api_version)
install_error_handlers(app)
for r in (system.router, reference.router, scans.router, me.router, products.router, files.router):
    app.include_router(r, prefix="/api/v1")
