# 11 · Local Development Setup

**Mobile section (§4) was executed in Milestone 1 (Node v22, npm 10).** The API/Supabase sections are still untested until Milestone 2.

## Prerequisites
| Tool | Version guidance |
|---|---|
| Git | any recent |
| Node.js | current LTS that meets the chosen Expo SDK minimum (check `docs.expo.dev` SDK page) |
| Python | 3.11 |
| Docker Desktop / Docker Engine | recent; ≥ 8 GB RAM recommended for Supabase stack + OCR |
| Supabase CLI | for the local Postgres/Auth/Storage stack only |
| Android Studio (emulator) and/or Xcode (macOS only) | for development builds |

## 1. Clone and configure
```bash
git clone <your-repo-url> labellens-india && cd labellens-india
cp .env.example .env     # fill values printed by `supabase start`
```

## 2. Local database/auth/storage
```bash
supabase init            # once; keeps config.toml only (migrations are Alembic's)
supabase start           # prints API URL, anon key, service_role key, DB URL
```

## 3. API
```bash
cd services/api
python3.11 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"                                     # pyproject defined in M2
alembic upgrade head
python -m data_pipeline.seed_dev                            # tiny dev seed (M2+)
uvicorn app.main:app --reload --port 8000
pytest -q
```
OCR extra (M3): `pip install -e ".[ocr]"` — installs `paddlepaddle` (CPU) and `paddleocr`; first run downloads models (internet needed once).

## 4. Mobile
```bash
cd apps/mobile
npm install
npx expo install --check            # aligns package versions with the SDK
npm run typecheck && npm run lint && npm test   # verified in M1
npx expo start --web                # quickest way to see the app (verified)
npx expo export --platform android  # bundle-compile check (verified)
# Native run (NOT yet verified): npx expo run:android  or  npx expo run:ios
npm run typecheck && npm test
```
Physical device: install the dev build, set `EXPO_PUBLIC_API_URL` to your machine's LAN IP (e.g. `http://192.168.x.x:8000`); Android emulator uses `http://10.0.2.2:8000`.

## 5. Everything via Docker (API only)
```bash
docker compose up --build api
```

## 6. Quality gates (CI mirrors these)
```bash
ruff check . && mypy app && pytest          # services/api
npm run lint && npm run typecheck && npm test   # apps/mobile
```

## 7. Environment variables (`.env.example`)
`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `SUPABASE_ANON_KEY` (mobile), `SUPABASE_SERVICE_ROLE_KEY` (**scripts only, never shipped**), `STORAGE_BUCKET=scan-images`, `EXPO_PUBLIC_API_URL`, `LLM_EXPLAINER_ENABLED=false`.
