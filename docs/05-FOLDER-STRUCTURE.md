# 05 · Folder Structure (monorepo)

```
labellens-india/
├── CLAUDE.md                     # working rules for AI sessions
├── PROJECT_STATUS.md  CHANGELOG.md  DECISIONS.md  TEST_REPORT.md
├── README.md
├── .github/workflows/            # ci-api.yml  ci-mobile.yml  secrets-scan.yml
├── docs/                         # these Milestone 0 documents + disclaimers + data-licence register
├── docker-compose.yml            # api + (optional) local postgres
├── .env.example
├── apps/
│   └── mobile/                   # Expo app
│       ├── app/                  # Expo Router routes
│       │   ├── (auth)/           # login, register, onboarding
│       │   ├── (tabs)/           # home, history, saved, profile
│       │   ├── scan/             # category, camera, preview, processing, confirm
│       │   ├── report/[scanId].tsx
│       │   ├── ingredient/[id].tsx
│       │   ├── compare/  alternatives/
│       │   └── settings/  preferences/
│       ├── src/
│       │   ├── components/       # ui primitives + domain components
│       │   ├── features/         # scan, report, compare, prefs (hooks + queries per feature)
│       │   ├── api/              # typed client generated from OpenAPI
│       │   ├── store/            # zustand slices (session, scan draft, ui)
│       │   ├── theme/            # tokens: warm white, forest green, spacing, type
│       │   ├── mocks/            # realistic mock data (M1 only)
│       │   └── lib/
│       ├── assets/  __tests__/
│       └── app.json  tsconfig.json  (strict)  package.json
├── services/
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── core/             # config, security (JWT), logging, errors
│       │   ├── db/               # session, models/ (SQLAlchemy), rls helpers
│       │   ├── schemas/          # Pydantic
│       │   ├── routers/          # scans, ingredients, products, comparisons, me, system
│       │   ├── services/
│       │   │   ├── images/       # validation, exif strip, preprocess (OpenCV/Pillow)
│       │   │   ├── ocr/          # OcrEngine interface + paddle_engine.py
│       │   │   ├── parsing/      # section_detect, clean, split
│       │   │   ├── normalise/    # candidate index + RapidFuzz matcher
│       │   │   ├── rules/        # cosmetics engine (pure functions), registry per domain
│       │   │   ├── compare/      # diff + recommender
│       │   │   └── explain/      # template explainer, optional LLM plug-in
│       │   └── storage/          # supabase storage adapter
│       ├── alembic/ + alembic.ini
│       ├── data_pipeline/        # importers: open_beauty_facts, regulatory_in, pubchem, cir_links
│       ├── tests/                # unit/ integration/ contract/ fixtures/label_images/
│       ├── pyproject.toml
│       └── Dockerfile
├── supabase/                     # config.toml for local stack ONLY (migrations live in Alembic)
└── scripts/                      # dev helpers (seed, lint, make targets)
```

Conventions: Python 3.11, `ruff` + `mypy --strict` on `app/`; TypeScript `strict: true`, ESLint + Prettier; Conventional Commits; one PR per milestone sub-task; no secrets in repo.
