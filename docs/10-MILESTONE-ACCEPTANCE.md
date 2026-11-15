# 10 · Milestone Acceptance Criteria

A milestone is **done** only when every box is demonstrably true, evidence is attached (command output or screenshot) and TEST_REPORT.md states exactly what was and was not tested.

## M0 — Requirements & architecture (this milestone)
- [ ] 12 deliverables exist and are internally consistent (PRD, architecture + diagram, ER diagram, API contract, folder structure, compatibility report, dataset strategy, regulatory strategy, risk analysis, acceptance criteria, local setup).
- [ ] Every claim of version/limit is marked Verified or Not verified.
- [ ] Open decisions listed with a recommendation (DECISIONS.md).
- [ ] The 5 status files (CLAUDE.md, PROJECT_STATUS.md, CHANGELOG.md, DECISIONS.md, TEST_REPORT.md) created. **No application code.**

## M1 — Frontend with mock data
- [ ] All 19 screens reachable via Expo Router; typed mock data only.
- [ ] Design tokens implemented (warm white, forest green, rounded cards); contrast ≥ 4.5:1 for body text (checked with a tool).
- [ ] All six classification states render with non-colour cues (icon + label).
- [ ] `tsc --noEmit` clean in strict mode; ESLint clean; Jest + RNTL tests for key components pass.
- [ ] Runs on Android emulator and iOS simulator **or** the untested platform is stated; screenshots supplied.
- [ ] Camera/gallery UI works on a real device or limitation stated.

## M2 — Backend, DB, auth, storage
- [ ] Alembic migrations create all tables from doc 03; `upgrade` and `downgrade` both run on a clean DB.
- [ ] RLS tests: user A cannot read/write user B's rows through the API (negative tests pass).
- [ ] JWT verification rejects expired/forged tokens.
- [ ] Endpoints from doc 04 marked "M2" respond per OpenAPI; contract/authz/state tests pass.
- [ ] Private storage upload + signed URL works; EXIF stripped (test with GPS-tagged fixture).
- [ ] Docker/compose and CI run tests.

## M3 — Camera, upload, OCR
- [ ] Benchmark set of real Indian label photos (size agreed at start of M3) with ground-truth ingredient text committed (images the user owns/has rights to).
- [ ] Reports section-detection hit rate and token-level character error rate on that set — numbers, not adjectives.
- [ ] Blur/low-light/rotated fixtures covered by tests.
- [ ] No ingredient text invented: test proving truncated input yields `section_complete=false`.
- [ ] Manual paste fallback works end-to-end.
- [ ] p90 latency measured and recorded for the stated hardware.

## M4 — Normalisation, rules, evidence engine
- [ ] Rules engine is pure/deterministic: same input + ruleset ⇒ identical output (property test).
- [ ] Class 1 impossible without citation (DB check + unit test).
- [ ] Order-of-ingredients never changes class (test).
- [ ] Normaliser precision/recall on benchmark reported; thresholds justified from data.
- [ ] Every report item exposes citations; unmatched ⇒ class 6.
- [ ] Works with LLM explainer disabled (default).

## M5 — Catalogue & regulatory data
- [ ] Importers idempotent; re-run produces zero diff.
- [ ] India subset coverage of OBF measured and published in the doc.
- [ ] Regulatory rows pass citation CHECK constraints; sample dual-entry verified.
- [ ] Licence register complete; legal-review items closed or explicitly deferred by you.

## M6 — Comparison & recommendations
- [ ] Diff correct on fixture pairs (shared/only-A/only-B).
- [ ] Recommender never returns different-category or incomplete-list products; "no reliable alternative" path tested.
- [ ] Every recommendation has reasons; no price/availability fields present.

## M7 — Accounts, preferences, favourites, history
- [ ] Preferences change report flags; avoid/prefer tested.
- [ ] History/favourites CRUD with RLS; offline history view.
- [ ] Export and delete-account flows work; purge job verified.

## M8 — Testing, security, optimisation, deployment
- [ ] Coverage and test results reported honestly; known gaps listed.
- [ ] Dependency + secret scans clean or triaged; licence audit done.
- [ ] Rate limits and upload hardening verified.
- [ ] Deployment documented with actual free-tier limits and any paid items you approved.
- [ ] Privacy notice, disclaimers, grievance contact in app.
