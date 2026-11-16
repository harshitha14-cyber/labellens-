# PROJECT STATUS
**Date:** 2026-11-16 · **Current milestone:** 2 — complete, awaiting approval

| Milestone | State |
|---|---|
| 0 Requirements & architecture | ✅ Approved |
| 1 Frontend with mock data | ✅ Approved (+ small fixes in M2 turn, see CHANGELOG) |
| 2 Backend, DB, auth, storage | ✅ **Delivered, awaiting `APPROVE MILESTONE 2`** |
| 3–8 | Not started |

## M2 delivered (`services/api`)
- 22 tables (19 requested + 3 approved additions) via Alembic; 25 RLS policies; upgrade/downgrade round-trip verified; model/DB drift check passes.
- 23 REST operations (see docs/04 "Implementation status"), JWT auth, error envelope, request ids.
- Scan lifecycle + validated image upload (EXIF/GPS stripped) + signed-URL access.
- Profile, preferences, favourites, reference + product reads.
- Docker/compose/CI files written (**not executed**).

## Honest limitations
- The **mobile app is still on mock data**; it is not connected to this API yet (connection happens with real upload/OCR in M3).
- **No Supabase project, Docker or GitHub Actions run was possible here.** Supabase Auth/Storage and the Docker + CI files are unverified. Storage adapter has only a mocked-transport test.
- Tested on PostgreSQL 16.15 (Ubuntu) and Python 3.12; Windows and Python 3.11 are untested.
- No rate limiting yet (M8); no HEIC; `blur_score` empty until M3; no data export/purge (M7).
- Data tables are empty except 8 categories: ingredients, regulations and products arrive in M4-M5.

## Next
On approval: Milestone 3 (camera upload wired to the API + OCR pipeline). Needs PaddleOCR (large download).
