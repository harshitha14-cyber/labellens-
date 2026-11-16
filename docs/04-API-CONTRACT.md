# 04 · Backend API Contract (v1)

Base: `/api/v1` · JSON · UTC ISO-8601 timestamps · UUID ids · `Authorization: Bearer <Supabase JWT>` on everything except `/health` and `/meta`.

## Conventions
**Errors** (RFC 7807-style):
```json
{ "error": { "code": "IMAGE_TOO_SMALL", "message": "Short side must be ≥ 600 px", "details": {}, "request_id": "..." } }
```
Codes: `UNAUTHENTICATED` 401, `FORBIDDEN` 403, `NOT_FOUND` 404, `VALIDATION_ERROR` 422, `UNSUPPORTED_MEDIA` 415, `PAYLOAD_TOO_LARGE` 413, `IMAGE_TOO_SMALL` 422, `INVALID_STATE` 409, `RATE_LIMITED` 429, `INTERNAL` 500.
**Pagination:** `?limit=20&cursor=<opaque>` → `{ "items": [], "next_cursor": null }`.
**Idempotency:** `POST /scans` accepts `Idempotency-Key`.
**Rate limits (proposal):** 30 uploads/hour/user, 120 req/min/user.
**Versioning:** breaking change → `/api/v2`. OpenAPI served at `/openapi.json` (FastAPI) and is the machine-readable source once code exists.

## Endpoints
### System
| Method | Path | Notes |
|---|---|---|
| GET | `/health` | liveness |
| GET | `/meta` | `{api_version, ruleset_version, data_snapshot, ocr_languages:["en"]}` |

### Reference
| Method | Path | Notes |
|---|---|---|
| GET | `/categories` | active categories (cosmetics only in MVP), with `domain`, `usage_type` |
| GET | `/ingredients/search?q=&limit=` | trigram/synonym search |
| GET | `/ingredients/{id}` | full ingredient record (see "Ingredient record" at end) |

### Scans
| Method | Path | Purpose | Success |
|---|---|---|---|
| POST | `/scans` | `{category_id, language:"en"}` | 201 scan |
| POST | `/scans/{id}/images` | multipart `file` (repeat up to 5) | 201 image meta incl. `blur_warning` |
| DELETE | `/scans/{id}/images/{image_id}` | remove an image | 204 |
| POST | `/scans/{id}/process` | start OCR+parse | 202 `{status:"processing"}` |
| GET | `/scans/{id}` | state + results so far | 200 |
| PUT | `/scans/{id}/ingredients` | replace with user-confirmed list | 200 |
| POST | `/scans/{id}/ingredients/parse-text` | manual paste fallback: `{text}` → tokens+matches | 200 |
| POST | `/scans/{id}/analyse` | run rules engine | 200 report (idempotent per list hash) |
| GET | `/scans/{id}/report` | stored report | 200 |
| GET | `/scans/{id}/alternatives` | ranked alternatives (M6) | 200 |
| PATCH | `/scans/{id}` | `{saved, note, product_id}` | 200 |
| GET | `/scans` | history (`saved`, `category_id` filters) | 200 list |
| DELETE | `/scans/{id}` | deletes row + images | 204 |

`GET /scans/{id}` example (status `needs_confirmation`):
```json
{
  "id": "…", "status": "needs_confirmation", "category": {"id":"…","slug":"sunscreen"},
  "images": [{"id":"…","blur_warning":false}],
  "extraction": {
    "section_found": true, "section_complete": true, "mean_confidence": 0.93,
    "raw_section_text": "Aqua, Zinc Oxide, Glycerin, Parfum, …"
  },
  "ingredients": [
    {"position":1,"raw_token":"Aqua","ingredient":{"id":"…","canonical_name":"Water","inci_name":"Aqua"},
     "match_method":"synonym","match_score":1.0,"ocr_confidence":0.97,"user_status":"pending"},
    {"position":2,"raw_token":"Zinc 0xide","ingredient":null,
     "suggestions":[{"ingredient_id":"…","name":"Zinc Oxide","score":0.93}],
     "match_method":"fuzzy","ocr_confidence":0.71,"user_status":"pending"}
  ],
  "warnings": ["BLUR_DETECTED"]
}
```
`PUT /scans/{id}/ingredients` body:
```json
{ "ingredients": [
  {"position":1,"raw_token":"Aqua","ingredient_id":"…"},
  {"position":2,"raw_token":"Zinc 0xide","ingredient_id":"…","user_status":"edited"},
  {"position":3,"raw_token":"Madhuca longifolia seed oil","ingredient_id":null}
]}
```
Unmatched stays `ingredient_id:null` → class 6 in report.

### Report (`GET /scans/{id}/report`)
```json
{
  "scan_id":"…","ruleset_version":"cosmetics-2026.1","data_snapshot":"2026-11-01",
  "list_complete": true,
  "summary": {"class_counts":{"1":12,"2":1,"3":0,"4":3,"5":2,"6":1}, "notes":["Ingredient order does not indicate concentration."]},
  "items": [{
    "position":4,"raw_token":"Parfum",
    "ingredient":{"id":"…","canonical_name":"Fragrance","inci_name":"Parfum"},
    "functions":["fragrance"],
    "classification":{"class":5,"label":"Context dependent",
       "reasons":[{"code":"USER_PREFERENCE_AVOID","text":"You marked fragrance as an ingredient to avoid."}]},
    "regulations":[{"jurisdiction":"IN","regulation_name":"IS 4707 (Part 2):2025","provision":"Annex B","status":"restricted",
       "conditions":"…","last_checked_on":"2026-08-31","source_url":"…"}],
    "citations":[{"source_id":"…","organisation":"…","title":"…","url":"…","last_checked_on":"…"}],
    "confidence":0.7
  }],
  "disclaimer_id":"informational-v1"
}
```

### Products & catalogue
| Method | Path | Notes |
|---|---|---|
| GET | `/products?q=&category_id=&verification=` | search |
| GET | `/products/{id}` | includes ingredient list, `verification_status`, `ingredient_list_source`, `source_date` |
| POST | `/products` | community submission → `COMMUNITY_SUBMITTED` (links a scan's confirmed list) |
| GET | `/products/lookup?barcode=` | optional convenience; never required for analysis |

### Comparison
| Method | Path | Notes |
|---|---|---|
| POST | `/comparisons` | `{left_scan_id, right_scan_id? , right_product_id?}` → result |
| GET | `/comparisons/{id}` | stored |
Result: `{shared:[…], only_left:[…], only_right:[…], by_function:{…}, class_diff:{…}, completeness:{left,right}}` — shows differences; no "winner".

### Me / preferences / favourites
| Method | Path | Notes |
|---|---|---|
| GET/PATCH | `/me` | profile |
| GET/PUT | `/me/preferences` | `{include_community_products, items:[{kind:"avoid"|"prefer", ingredient_id? , tag?}]}` |
| GET/POST/DELETE | `/me/favourites` | `{product_id | scan_id}` |
| GET | `/me/export` | async JSON export (DPDP access right) |
| DELETE | `/me` | schedules erasure (30-day grace) |

### Admin (service role only, not exposed to mobile)
`POST /admin/products/{id}/verify`, `POST /admin/imports/*` — implemented as CLI scripts first; HTTP admin deferred.

## Contract tests
Every endpoint: schema test (Pydantic ↔ OpenAPI), authz test (other user's id → 404), state-machine test (`INVALID_STATE`). Defined in M2; pass/fail reported honestly in TEST_REPORT.md.

## Ingredient record (`GET /ingredients/{id}`)
```json
{
  "id":"…","canonical_name":"Zinc Oxide","inci_name":"Zinc Oxide","synonyms":["ZnO"],
  "cas_number":"1314-13-2","pubchem_cid":"…","category":"mineral UV filter",
  "functions":["uv_filter","skin_protectant"],"description":"…",
  "assessments":[{"classification":1,"context":"sun","summary":"…","confidence":0.8,"assessed_on":"2026-10-12",
                  "source":{"organisation":"…","title":"…","url":"…","last_checked_on":"…"}}],
  "regulations":[{"jurisdiction":"IN","regulation_name":"IS 4707 (Part 4)","provision":"…","status":"conditional","conditions":"…","last_checked_on":"…"}],
  "reference_regulations":[{"jurisdiction":"EU","label":"Reference only — not Indian status", "…":"…"}]
}
```
(Values above are format illustrations, **not** real assessments.)

## Implementation status (updated Milestone 2)
**Implemented and tested:** `/health`, `/meta`, `/categories`, `/ingredients/search`, `/ingredients/{id}`, `/scans` (POST, GET list, GET one, PATCH, DELETE), `/scans/{id}/images` (POST, DELETE), `/scans/{id}/images/{image_id}/url` (signed URL), `/me` (GET, PATCH, DELETE), `/me/preferences` (GET, PUT), `/me/favourites` (GET, POST, DELETE), `/products` (GET list), `/products/{id}` (GET).
**Deviation from the original contract:** `/scans/{id}/images/{image_id}/url` and `/files/{path}` were added (signed-URL image access); `POST /products` is deferred to Milestone 5 with the catalogue; `GET /me/export` to Milestone 7.
**Not yet implemented:** `/scans/{id}/process`, `/ingredients` confirm/parse-text, `/analyse`, `/report` (M3-M4); `/alternatives`, `/comparisons` (M6); `/products/lookup`; rate limits (M8). `HEIC` uploads are rejected (needs `pillow-heif`).
