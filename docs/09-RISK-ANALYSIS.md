# 09 · Licensing, Privacy and Delivery Risk Analysis

Not legal advice; items marked ⚖ need review by an Indian lawyer before public launch.

## A. Licensing / IP
| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R-01 ⚖ | OBF ODbL share-alike could apply to our derived catalogue | M | H | Segregate OBF rows by `import_id`; track attribution; counsel review; be ready to publish/remove the derived subset |
| R-02 ⚖ | BIS IS 4707 is a copyrighted, sold standard; extracting entries could infringe compilation rights | M | H | Store facts + citations only, no text; counsel opinion; fallback = CDSCO/Gazette notices and manual verification links |
| R-03 | CIR / manufacturer content copyrighted | M | M | Link + conclusion category, no copying |
| R-04 | OBF images CC BY-SA | L | M | Don't ingest product images in MVP |
| R-05 | Dependency licences (PaddleOCR Apache-2.0, OpenCV Apache-2.0, RapidFuzz MIT — recall, confirm via `pip-licenses` in M8) | L | M | Licence audit in CI |

## B. Privacy / data protection (India: Digital Personal Data Protection Act 2023 and its Rules — confirm current in-force dates ⚖)
| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R-06 | Photos may contain faces, hands, shelves, location EXIF | M | M | Strip EXIF/GPS server-side; guidance text "photograph only the label"; private bucket; retention default 30 days for unsaved scans |
| R-07 | Sensitivities/skin preferences are health-adjacent personal data | M | H | Collect minimum; explicit consent screen; encrypt at rest (Supabase default), RLS, no analytics on preference content |
| R-08 | Children's data (DPDP has special rules) | L | H | 18+ gate at registration (age confirmation) |
| R-08b | Rights: access, correction, erasure, grievance officer | — | M | `/me/export`, `/me` delete with 30-day grace, in-app grievance contact, privacy notice in English (Indian-language notice before wide launch) |
| R-08c | Third-country transfer (Supabase region) | M | M | Pick Mumbai/Singapore region if available on free tier (verify); document |
| R-08d | Third-party LLM would receive user data | — | H | LLM explainer off by default; only structured non-personal text may ever be sent |

## C. Product / legal-claims
| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R-10 ⚖ | Negative statements about a named brand → defamation / consumer-law exposure | M | H | Neutral factual wording, citations on every statement, "based on the label you photographed", correction channel, no brand rankings |
| R-11 | Users read output as medical advice | M | H | Persistent disclaimer; no diagnosis; "ask a dermatologist" prompts for reactions |
| R-12 | False reassurance from class 1 | M | H | Class 1 wording always "for specified uses"; completeness banner; unmatched shown |
| R-13 | Stale regulation | M | H | Versioning, last-checked dates, watch checklist |
| R-14 | Advertising/claims rules (ASCI/Consumer Protection Act) for app marketing | L | M | No "first of its kind" or health-benefit claims |

## D. Technical / delivery
| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R-15 | OCR accuracy on curved, glossy, tiny Indian labels; bilingual labels | H | H | Multi-photo, confirm-screen editing, manual paste fallback, blur warning, benchmark set of ≥ N real labels in M3 (N set then) |
| R-16 | Ingredient-name normalisation false matches | M | H | Thresholds + user acceptance for fuzzy, show scores, tune on held-out set |
| R-17 | Indian catalogue coverage thin at launch | H | M | Photograph-first design works without it; coverage measured and disclosed |
| R-18 | NativeWind v4/v5 + Expo SDK churn | M | M | Pin versions (D-003); upgrade as dedicated task |
| R-09 | **No verified free host for PaddleOCR API; Supabase free auto-pauses** | H | H | D-008 options; local-first dev; accept paid hosting if approved |
| R-19 | Supabase Free 1 GB storage / 500 MB DB | M | M | Resize/compress, retention purge, monitor |
| R-20 | Paddle install friction (wheels, CPU flags) | M | M | M3 spike first; Docker image |
| R-21 | Recommendation quality with sparse verified data | H | M | Empty state is valid; no fabricated alternatives |
| R-22 | Scope creep into food | M | M | Domain column only; food out of MVP |
| R-23 | Store fees (Google/Apple) are paid | H | L | Flag now; needed only at M8 |

L = likelihood, I = impact (H/M/L).
