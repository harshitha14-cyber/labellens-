# TEST REPORT
## Milestone 1 (2026-11-15) — all results below are from commands actually run
| Check | Command / method | Result |
|---|---|---|
| Strict typecheck | `npx tsc --noEmit` | ✅ exit 0 |
| Lint | `npx eslint .` | ✅ exit 0 (after fixing 12 real issues) |
| Unit/component tests | `npx jest` | ✅ 2 suites, **19 tests passed** |
| Web bundle | `npx expo export --platform web` | ✅ |
| Android bundle (Hermes) | `npx expo export --platform android` | ✅ 4.5 MB .hbc |
| Browser behaviour | Playwright + headless Chromium, 390×844 mobile viewport, fake camera | ✅ **17/17 checks**, 0 console/page errors |
| Contrast | WCAG ratio script on 16 colour pairs | ✅ all ≥ 4.5:1 after darkening placeholder |
| expo-doctor | `npx expo-doctor` | ⚠️ 19/21; 2 need Expo servers (network blocked) |
| npm audit | `npm audit --omit=dev` | ⚠️ findings present, **untriaged** |

### Browser checks (what they prove)
Splash→onboarding; guest login; camera screen renders; read button disabled with 0 photos; confirm shows 5 simulated lines; low-confidence flag; accepting "Did you mean Zinc Oxide" works; add/remove ingredient; draft report shows incomplete-list warning and an Unmatched item; avoid-list flag; EU shown as reference only; community alternatives hidden by default; no ₹/price text.

### Logic tests (19) include
counts sum to token count; unmatched = class 6; deterministic; order-independent; class-1 always cited; EU/US reference-only; no fuzzy guessing in `matchLocal`; image cap 5; preference toggles; ClassBadge text for all six classes; Button enabled/disabled.

### NOT tested
Real device/emulator, shutter capture, gallery picker, image rotate, VoiceOver/TalkBack, iOS, large font scaling, offline behaviour, performance.
