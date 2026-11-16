# CLAUDE.md — Working rules for LabelLens India

## Product in one line
India-first, photograph-first cosmetic ingredient intelligence. Works for products absent from any database.

## Non-negotiables
1. One milestone at a time. Never start milestone N+1 before the user writes `APPROVE MILESTONE N`. Stop after each milestone.
2. Inspect existing files before editing; preserve working code.
3. Never claim anything is tested unless it was run; record real output in TEST_REPORT.md.
4. Never invent ingredients, products, brands, prices, availability, evidence or regulations.
5. Never infer concentration from ingredient order. No unqualified "safe"/"toxic". No diagnosis.
6. Indian status comes only from Indian sources (Cosmetics Rules 2020, BIS IS 4707, CDSCO/Gazette). EU/US = labelled reference only.
7. Class 1 ("generally accepted for specified uses") requires a citation; unmatched = class 6 and is always shown.
8. Rules engine is deterministic. LLMs may only rephrase supplied structured fields; app must work with `LLM_EXPLAINER_ENABLED=false`.
9. No paid dependency without explanation and approval.
10. Alembic is the only migration system. RLS enforced for user data through the API.

## Stack
Expo SDK 57 (D-003 resolved) · TypeScript strict · Expo Router · NativeWind · Zustand · TanStack Query · FastAPI · Pydantic · SQLAlchemy · Alembic · PostgreSQL/Supabase · PaddleOCR (PP-OCRv6) · OpenCV · Pillow · RapidFuzz.

## Where things are
`docs/01…11` (M0 deliverables) · `DECISIONS.md` · `PROJECT_STATUS.md` · `CHANGELOG.md` · `TEST_REPORT.md`

## Milestone end checklist
Update CLAUDE.md, PROJECT_STATUS.md, CHANGELOG.md, DECISIONS.md, TEST_REPORT.md → give exact commands to test → list limitations → STOP.
- Local-only, zero-cost: no hosting work (D-008).
- Run `npx expo install <pkg>` (never plain npm add) for Expo packages. Never use pkill -f with a pattern that matches your own command.
- Backend facts: API connects as `ll_app` (RLS enforced); schema changes only via Alembic; every new table needs RLS policy + test; run tests with Postgres >= 15.
- Deliver only changed files each milestone (no zip); give git push steps; never commit screenshots, `.env`, `.venv`, `.storage`.
