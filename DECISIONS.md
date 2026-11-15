# DECISIONS (ADR log)
| ID | Decision | Status | Rationale |
|---|---|---|---|
| D-001 | Cosmetics first; `domain` column keeps food extensible | Accepted (brief) | Scope control |
| D-002 | Photo-first; products table supplementary | Accepted (brief) | Core differentiator |
| D-003 | **Recommend Expo SDK 57 + NativeWind 4.2.x + Tailwind 3.4 now; move to SDK 58 + NativeWind 5 once v5 is stable** | **Needs your choice** | SDK 58 is current (2026-10-21) but NativeWind 5 is RC and I found no confirmation of 4.2.7 on SDK 58 |
| D-004 | No single overall product score in MVP; show class distribution + completeness | **Needs your confirmation** | Avoids false precision; supports claims policy |
| D-005 | Alembic owns schema; Supabase local used for Postgres/Auth/Storage only | Proposed | One migration history |
| D-006 | Add tables `data_imports`, `user_preference_items`, `ingredient_function_map` | **Needs approval** | Provenance/licensing, preference lists, M:N functions |
| D-007 | Add BIS IS 4707 (Parts 1–4) as primary Indian ingredient source alongside Cosmetics Rules 2020/CDSCO | **Needs approval** | Ingredient lists are in IS 4707, not the Rules text |
| D-008 | OCR hosting: develop locally; for hosted use choose later among (a) self-hosted on your own machine/VPS you already have, (b) a free-tier container host if one fits RAM, (c) approved paid small VPS. No free option verified | **Needs your input before M8, spike in M3** | Paddle container is the weakest ₹0 link |
| D-009 | RLS enforced via restricted DB role + per-request JWT claims | Proposed | Defence in depth |
| D-010 | PaddleOCR PP-OCRv6 behind `OcrEngine` interface | Proposed | Newer models; swap-ability; future Indian languages |
| D-011 | OCR async via background task + polling (no queue in MVP) | Proposed | Zero extra infra |
| D-012 | Python 3.11 target; 3.12 verified in M3 | Proposed | Wheel availability unverified |
| D-013 | Unsaved scan images deleted after 30 days (configurable) | Proposed | Privacy minimisation vs 1 GB storage |
| D-014 | Community products visible and labelled; excluded from recommendations unless user opts in | Proposed | Transparency without overstating reliability |

## Updates 2026-11-15 (Milestone 1)
| ID | Update |
|---|---|
| — | **M0 approved by the user ("ok continue building")** with my recommendations. This was an implied, not literal `APPROVE MILESTONE 0`; recorded so it can be reversed. |
| D-003 | **Resolved: Expo SDK 57 (57.0.33), RN 0.86.3, NativeWind 4.2.7, Tailwind 3.4.x.** Verified: typecheck, lint, web bundle and Android Hermes bundle all succeed. |
| D-004 | Accepted: no overall score. Implemented as class-distribution bar + completeness banner. |
| D-006 / D-007 | Accepted by the user's go-ahead (applies from M2 / M5). |
| D-008 | **Resolved: local-only, zero hosting.** User wants to build and learn, not host. Hosting deferred indefinitely; R-09 is parked, not solved. |
| D-015 | Home tab route is `/home` (splash owns `/`); avoids a route conflict found during testing. |
| D-016 | Mock data labelled "Demo data" on every screen; all assessments/sources/regulations in `mocks/data.ts` are placeholders. |
| D-017 | `expo-asset`, `babel-preset-expo` are explicit dependencies (required on SDK 57). |
