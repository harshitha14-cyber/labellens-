# 08 · Indian Regulatory Source Strategy

## 1. Important correction to the brief
Your brief names the **Cosmetics Rules, 2020** and CDSCO. Those are correct, but in practice **India's ingredient-level lists live in the BIS standard IS 4707** (Classification of Cosmetic Raw Materials and Adjuncts), which the Rules make mandatory. Without it the app has no ingredient-level Indian data. I propose adding it as a primary source. (D-007)

## 2. Source hierarchy (what outranks what)
| Rank | Source | Role |
|---|---|---|
| 1 | Drugs and Cosmetics Act, 1940 | statutory basis |
| 2 | **Cosmetics Rules, 2020** (CDSCO-administered), incl. Ninth/Tenth Schedules and amendments | binding rules; colours; product standards list |
| 3 | **BIS IS 4707** — Part 1 (2020), **Part 2 (2025, 5th revision: prohibited "GNRAS" Annex A and restricted Annex B)**, **Part 3 (2025: preservatives)**, Part 4 (2022: UV filters) | ingredient lists, limits, conditions, warnings |
| 4 | CDSCO notices, gazette notifications, FAQs | amendments, effective dates |
| 5 | Product-specific BIS standards (37 listed in the Ninth Schedule per a secondary source) | product-type requirements — later |
| Reference only | EU CosIng/SCCS, US FDA, CIR | labelled "reference — not Indian status" |

## 3. What I found today (secondary sources, **not yet confirmed against primary documents**)
- IS 4707 Part 2:2025 reported published **Aug 2025**, fifth revision; Part 3:2025 (preservatives, standalone for the first time) reported **effective 2026-02-09**; Part 2 mandatory date reported as early 2026 (exact date to confirm). Annex A reportedly ~1,614 prohibited, Annex B ~313–317 restricted (sources differ by a few).
- A third-party site republishes Indian records with entry numbers and "source checked 2026-08-31". **It is a convenience lead, not an authority**; our records must cite BIS/CDSCO/Gazette, not that site.
- Details I have **not** verified: exact mandatory dates, whether Annex A/B text is freely viewable from BIS, CDSCO's current document URLs.

## 4. Record schema (maps to `ingredient_regulations` + `ingredient_sources`)
`source_organisation`, `regulation_name`, `provision` (e.g. "IS 4707 Part 2:2025, Annex B, entry N"), `jurisdiction`, `effective_from` / `published_on` (nullable), `last_checked_on` (required), `source_url` (required), `version`, `status` (prohibited | restricted | conditional | listed_permitted), `conditions` (max %, product type, leave-on/rinse-off), `warnings` (mandatory label text), `binding` (bool), `import_id`. CHECK constraints reject rows missing the required citation fields — **no untraceable rule can be loaded.**

## 5. Matching rules
- Match on CAS first, then INCI/name; Annex entries often cover **groups/salts/"and its salts"** → store `match_scope` (exact | group | salt-family) and show "listed under a group entry" instead of implying an exact hit.
- A hit means "appears on a list with these conditions". Without concentration, product type and use, the app reports **status + conditions**, never "violation". Label order never implies concentration.
- Presence in a *permitted* list ≠ proof of safety for every use (stated in UI copy).
- Fragrance allergen disclosure thresholds (reported amended/corrected in Part 2:2025) are label-compliance facts, stored as conditions.

## 6. Versioning & freshness
Rows are append-only per `version`; a new revision creates new rows and marks old `superseded_on`. Reports store `ruleset_version` + `data_snapshot`. A monthly "regulatory watch" checklist (manual in MVP): CDSCO notices page, BIS gazette, Gazette of India. Reports show "Indian regulatory data checked on <date>".

## 7. Acquisition plan (M5)
1. Locate primary documents (BIS standards portal, CDSCO cosmetics page, e-Gazette). 2. Record exact titles/dates/URLs in `ingredient_sources`. 3. Extract only structured facts for ingredients that appear in our frequency-ranked set first. 4. Dual-entry check on a sample (two reviewers/passes) before marking loaded. 5. Legal review of storing extracts from BIS standards (copyright) — **blocking question**.

## 8. Food (future)
Separate `domain='food'` records: FSSAI Food Products Standards and Food Additives Regulations, Labelling and Display Regulations, amendments. Not implemented now.
