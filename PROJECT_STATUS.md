# PROJECT STATUS
**Date:** 2026-11-15 · **Current milestone:** 1 — complete, awaiting approval

| Milestone | State |
|---|---|
| 0 Requirements & architecture | ✅ Approved (implied, see DECISIONS) |
| 1 Frontend with mock data | ✅ **Delivered, awaiting `APPROVE MILESTONE 1`** |
| 2–8 | Not started |

## M1 delivered
All 19 screens in `apps/mobile` (Expo SDK 57, TS strict, Expo Router, NativeWind 4, Zustand, TanStack Query, Reanimated 4). Typed mock API + demo data. Full flow works end to end in the browser: splash → onboarding → login/register → home → category → camera / gallery → preview → simulated processing → editable confirmation → report → ingredient detail → compare → alternatives → history / saved / preferences / profile / settings.

## Honest limitations
- **Not run on a real Android/iOS device or emulator.** Verified: web render in headless Chromium (24 screenshots, 17 behaviour checks) and a successful Android Hermes bundle compile. Native look/feel is unverified.
- Camera preview verified with a synthetic Chromium video feed; **shutter capture, gallery picker and image rotate were not exercised.**
- **Screen 8 cropping is partial:** rotate and remove only. Interactive crop is not built.
- OCR is **simulated**; auth is **mock**; all ingredient/regulatory content is **demo placeholder data**.
- Draft-line editing uses exact name/synonym matching only (real fuzzy normaliser is M4).
- `expo-doctor`: 19/21 pass; 2 checks need Expo servers (unreachable here), so unverified.
- `npm audit` reports vulnerabilities that are **not yet triaged**.
- Unpersisted state: restarting the app resets onboarding/preferences (persistence is M7).

## Next
On approval: Milestone 2 (FastAPI + Postgres/Supabase local + auth + storage) only.
