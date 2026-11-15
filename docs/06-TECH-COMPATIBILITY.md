# 06 · Technology Compatibility Report

Checked **2026-11-15** via web search. "Verified" = confirmed from a source found today. "Not verified" = I did not confirm; must be checked at install time (`npm view`, `pip index versions`) in the named milestone. **Nothing below has been installed or run.**

## 1. Mobile
| Item | Finding | Status |
|---|---|---|
| Expo SDK | **SDK 58 released 2026-10-21** (React Native 0.88, iOS 27 support). Previous: SDK 57 (RN 0.86), SDK 56 (May 2026, RN 0.85). Expo publishes ~3 SDKs/year. Since SDK 55 all Expo packages share the SDK's major version (e.g. `expo-camera@^58`). | Verified |
| NativeWind | **Stable is 4.2.7 (2026-09-14) and requires Tailwind CSS v3** (`tailwindcss@^3.4.17`); installing Tailwind v4 with it fails at Metro start. **v5 (Tailwind v4) is at 5.0.0-rc.0 (2026-09-13)** and the maintainers say not for production. A third-party summary lists 4.2.7 as checked against Expo 57.x; **I found no confirmation for SDK 58.** | Verified (secondary source) |
| Reanimated 4 | Needs `react-native-worklets` alongside | Verified (secondary source) |
| Expo Router, Camera, Image Picker, Zustand, TanStack Query | Not individually checked; Expo packages follow the SDK via `npx expo install`; Zustand/TanStack to be pinned from npm at M1 | **Not verified** |
| Expo Go | Production-like features (camera + native modules) → use **development builds**, not Expo Go | Verified direction (Expo guidance) |

**Recommendation (D-003, needs your decision):** start on **Expo SDK 57 + NativeWind 4.2.7 + Tailwind 3.4.x** for a known-compatible styling stack, then move to SDK 58 + NativeWind 5 once v5 is stable. Alternative: SDK 58 now and accept NativeWind-on-58 risk. Alternative 2: SDK 58 + NativeWind v5 RC (not recommended for a product you intend to ship).

## 2. Backend
| Item | Finding | Status |
|---|---|---|
| PaddleOCR | **3.7.0 (2026-06-11) ships PP-OCRv6**: tiny/small/medium tiers (1.5M–34.5M params); one model for 50 languages (Chinese, English, Japanese, 46 Latin-script). 3.x has breaking API changes vs 2.x — ignore 2.x tutorials. | Verified |
| PaddlePaddle runtime | PaddleOCR needs the separate `paddlepaddle` package; exact compatible version and **Python 3.12 wheel availability not verified** | **Not verified** → M3 spike |
| Hindi / Tamil OCR | PP-OCRv6 announcement lists Latin-script languages, not Devanagari/Tamil. Separate models may exist; **not verified** | **Not verified** → future |
| Python | Target **3.11** for dependency safety; confirm 3.12 in M3 | Decision |
| FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, RapidFuzz, OpenCV (headless), Pillow, pytest | Versions **not checked today**; pin from PyPI at M2/M3 | **Not verified** |
| Image libs | `opencv-python-headless` (no GUI deps in containers) | Decision |

## 3. Platform & hosting limits (documented per your brief)
| Service | Free-tier facts found | Notes |
|---|---|---|
| Supabase Free | 500 MB database, 1 GB file storage, 5 GB egress/month, 50,000 MAU, 2 active projects, **auto-pause after 7 days inactivity**, no daily backups (several 2026 sources agree; confirm on supabase.com/pricing) | 1 GB storage ≈ ~3,000 images at ~300 KB each after resize; 500 MB DB is ample for ingredients but watch `report_json` and `boxes_json` growth |
| Supabase Pro (reference) | $25/mo; 8 GB DB, 100 GB storage | Not adopted; needs your approval if required |
| PaddleOCR cloud API | A free API with a daily page cap exists, but **sending user photos to a third party conflicts with the privacy stance** — not adopted | — |
| API hosting | **No free host verified** for a Paddle-sized container (RAM ≥ ~2 GB assumed) | Risk R-09; options in DECISIONS D-008 |
| EAS Build | Free tier exists with queue/limits; not verified | Verify at M8 |
| Expo/Play/App Store | Google Play one-time developer fee and Apple Developer annual fee are **paid** and unavoidable for store release (not for development) | Flag for M8 |

## 4. Compatibility matrix (planned pins)
| Layer | Plan |
|---|---|
| Node | current LTS that satisfies the chosen Expo SDK's minimum (check Expo SDK page) |
| Mobile | Expo SDK 57 (pending D-003), RN per SDK, TS strict |
| Styling | NativeWind 4.2.x + Tailwind 3.4.x |
| API | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic |
| OCR | paddleocr 3.7.x + matching paddlepaddle (CPU), PP-OCRv6 small/medium chosen by benchmark |
| DB | PostgreSQL 15/16-compatible (Supabase local stack) + `pg_trgm` |
