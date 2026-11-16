"""Upload validation + sanitising.

Decodes the image with Pillow and RE-ENCODES it as a new JPEG. That drops all EXIF/GPS/XMP
metadata and any trailing/polyglot bytes. HEIC is not supported yet (needs pillow-heif).
"""
import io
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings
from app.core.errors import ApiError

ALLOWED = {"JPEG", "PNG", "WEBP"}
Image.MAX_IMAGE_PIXELS = 60_000_000  # decompression-bomb guard


@dataclass
class ProcessedImage:
    data: bytes
    width: int
    height: int


def process_upload(raw: bytes, settings: Settings) -> ProcessedImage:
    if len(raw) > settings.max_upload_bytes:
        raise ApiError(413, "PAYLOAD_TOO_LARGE", f"Image exceeds {settings.max_upload_bytes // (1024 * 1024)} MB")
    if not raw:
        raise ApiError(422, "VALIDATION_ERROR", "Empty file")
    try:
        probe = Image.open(io.BytesIO(raw))
        fmt = probe.format
        probe.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ApiError(415, "UNSUPPORTED_MEDIA", "Not a readable JPEG, PNG or WEBP image") from None
    if fmt not in ALLOWED:
        raise ApiError(415, "UNSUPPORTED_MEDIA", f"{fmt} is not supported (use JPEG, PNG or WEBP)")
    try:
        opened = Image.open(io.BytesIO(raw))
        img: Image.Image = ImageOps.exif_transpose(opened)  # apply camera rotation BEFORE metadata is dropped
        img = img.convert("RGB")
    except (OSError, Image.DecompressionBombError):
        raise ApiError(415, "UNSUPPORTED_MEDIA", "Image could not be decoded") from None
    w, h = img.size
    if min(w, h) < settings.min_short_side_px:
        raise ApiError(422, "IMAGE_TOO_SMALL", f"Short side must be at least {settings.min_short_side_px} px",
                       {"width": w, "height": h})
    longest = max(w, h)
    if longest > settings.max_long_side_px:
        scale = settings.max_long_side_px / longest
        img = img.resize((round(w * scale), round(h * scale)), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85, optimize=True)  # no exif= argument -> metadata stripped
    return ProcessedImage(out.getvalue(), img.width, img.height)
