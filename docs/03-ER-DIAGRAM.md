# 03 · Database Design (PostgreSQL)

All 19 requested tables are present. **Proposed additions (need approval, D-006):** `data_imports` (dataset provenance/licence per import run), `user_preference_items` (child rows for avoid/prefer lists), `ingredient_function_map` (many-to-many join; `ingredient_functions` stays the lookup). PKs are UUID (`gen_random_uuid()`), all tables have `created_at`/`updated_at` (timestamptz) unless noted.

## ER diagram
```mermaid
erDiagram
  users ||--o| user_preferences : has
  user_preferences ||--o{ user_preference_items : lists
  users ||--o{ scans : owns
  users ||--o{ user_favourites : saves
  users ||--o{ product_comparisons : creates
  product_categories ||--o{ products : classifies
  product_categories ||--o{ scans : "scanned as"
  products ||--o{ product_ingredients : contains
  ingredients ||--o{ product_ingredients : "appears in"
  ingredients ||--o{ ingredient_synonyms : "known as"
  ingredients ||--o{ ingredient_function_map : performs
  ingredient_functions ||--o{ ingredient_function_map : defines
  ingredients ||--o{ ingredient_assessments : assessed
  ingredient_sources ||--o{ ingredient_assessments : supports
  ingredients ||--o{ ingredient_regulations : regulated
  ingredient_sources ||--o{ ingredient_regulations : "cites"
  data_imports ||--o{ products : "imported via"
  data_imports ||--o{ ingredient_regulations : "imported via"
  scans ||--o{ scan_images : has
  scan_images ||--o| extracted_text : yields
  scans ||--o{ scan_ingredients : lists
  ingredients ||--o{ scan_ingredients : "matched to"
  scans ||--o| scan_reports : produces
  scans |o--o| products : "linked to (optional)"
  scans ||--o{ alternative_products : suggests
  products ||--o{ alternative_products : "is alternative"
  product_comparisons }o--|| scans : "left"
  product_comparisons }o--o| scans : "right scan"
  product_comparisons }o--o| products : "right product"
  user_favourites }o--o| products : favourites
  user_favourites }o--o| scans : favourites

  users { uuid id PK "= auth.users.id" text display_name text locale timestamptz deleted_at }
  user_preferences { uuid id PK uuid user_id FK_UQ bool include_community_products }
  user_preference_items { uuid id PK uuid preference_id FK uuid ingredient_id FK text kind "avoid|prefer" text tag "e.g. fragrance" }
  product_categories { uuid id PK text slug UQ text name text domain "cosmetics|food" text usage_type "leave_on|rinse_off|sun" }
  products { uuid id PK text name text brand uuid category_id FK text country_of_origin text product_identifier "barcode/SKU" text ingredient_list_source date source_date text verification_status "VERIFIED|COMMUNITY_SUBMITTED|UNVERIFIED" bool ingredient_list_complete uuid import_id FK uuid submitted_by FK }
  ingredients { uuid id PK text canonical_name UQ text inci_name text cas_number text pubchem_cid text description text category text domain }
  ingredient_synonyms { uuid id PK uuid ingredient_id FK text synonym text synonym_normalised text language text kind "common|inci|trade|misspelling" }
  ingredient_functions { uuid id PK text slug UQ text name text description }
  ingredient_function_map { uuid ingredient_id FK uuid function_id FK }
  product_ingredients { uuid id PK uuid product_id FK uuid ingredient_id FK "nullable if unmatched" text raw_name int position }
  ingredient_sources { uuid id PK text organisation text title text url text licence date published_on date last_checked_on }
  ingredient_assessments { uuid id PK uuid ingredient_id FK uuid source_id FK smallint classification "1-5" text context "e.g. leave_on, sun" text summary numeric confidence date assessed_on text ruleset_version }
  ingredient_regulations { uuid id PK uuid ingredient_id FK uuid source_id FK text jurisdiction "IN|EU|US" text regulation_name text provision "e.g. IS 4707 Pt2 Annex B #92" text status "prohibited|restricted|conditional|permitted_listed" text conditions "max conc, product type" text warnings date effective_from date last_checked_on text version bool binding }
  data_imports { uuid id PK text dataset text dataset_version text licence text source_url timestamptz run_at text checksum }
  scans { uuid id PK uuid user_id FK uuid category_id FK uuid product_id FK text status text language bool saved text note timestamptz deleted_at }
  scan_images { uuid id PK uuid scan_id FK text storage_path int width int height numeric blur_score int seq }
  extracted_text { uuid id PK uuid scan_image_id FK_UQ text raw_text text cleaned_text jsonb boxes_json numeric mean_confidence text engine text engine_version text section_text bool section_complete }
  scan_ingredients { uuid id PK uuid scan_id FK int position text raw_token uuid ingredient_id FK "nullable" numeric ocr_confidence numeric match_score text match_method "exact|synonym|fuzzy|manual|none" text user_status "pending|confirmed|edited|removed|added" }
  scan_reports { uuid id PK uuid scan_id FK_UQ jsonb report_json text ruleset_version text data_snapshot jsonb class_counts bool list_complete }
  alternative_products { uuid id PK uuid scan_id FK uuid product_id FK int rank jsonb reasons_json }
  product_comparisons { uuid id PK uuid user_id FK uuid left_scan_id FK uuid right_scan_id FK uuid right_product_id FK jsonb result_json }
  user_favourites { uuid id PK uuid user_id FK uuid product_id FK uuid scan_id FK }
```

## Constraints & indexes (summary)
| Table | Unique | Notable indexes / checks |
|---|---|---|
| ingredients | `canonical_name`; partial unique `cas_number` where not null | GIN trigram on `canonical_name`, `inci_name` |
| ingredient_synonyms | (`ingredient_id`,`synonym_normalised`,`language`) | btree + GIN trigram on `synonym_normalised` |
| products | (`brand`,`name`,`product_identifier`) nulls-not-distinct | `category_id`, `verification_status`; GIN trigram on `name`; CHECK status in enum |
| product_ingredients | (`product_id`,`position`) | `ingredient_id` |
| ingredient_assessments | (`ingredient_id`,`source_id`,`context`,`assessed_on`) | CHECK `classification` 1–5; CHECK class 1 requires `source_id` NOT NULL |
| ingredient_regulations | (`ingredient_id`,`jurisdiction`,`regulation_name`,`provision`,`version`) | `jurisdiction`; CHECK required citation fields NOT NULL (source_id, regulation_name, provision, jurisdiction, last_checked_on) |
| scans | — | (`user_id`,`created_at` desc); partial index `saved` |
| scan_ingredients | (`scan_id`,`position`) | `ingredient_id` |
| scan_reports | `scan_id` | — |
| user_favourites | (`user_id`,`product_id`), (`user_id`,`scan_id`) | CHECK exactly one of product_id/scan_id non-null |
| scan_images | (`scan_id`,`seq`) | — |

`pg_trgm` extension enabled for fuzzy candidate retrieval; RapidFuzz re-scores in Python.

Class 6 ("unmatched") is **not stored** in `ingredient_assessments`; it is derived at analysis time from `scan_ingredients.ingredient_id IS NULL`.

## Row Level Security
| Group | Tables | Policy |
|---|---|---|
| User-owned | users, user_preferences, user_preference_items, scans, scan_images, extracted_text, scan_ingredients, scan_reports, alternative_products, product_comparisons, user_favourites | `USING (owner = auth.uid())` for SELECT/INSERT/UPDATE/DELETE; child tables via `EXISTS` join to `scans.user_id` |
| Reference (read-only to clients) | ingredients, ingredient_synonyms, ingredient_functions, ingredient_function_map, ingredient_assessments, ingredient_sources, ingredient_regulations, product_categories | SELECT for `authenticated`; no client writes |
| Catalogue | products, product_ingredients | SELECT for `authenticated` (VERIFIED, UNVERIFIED, COMMUNITY_SUBMITTED all visible, always labelled); INSERT own `COMMUNITY_SUBMITTED` only; UPDATE/DELETE own while unverified; verification changes admin-only |
| Provenance | data_imports | admin only |

Storage: bucket `scan-images` private; policy `(storage.foldername(name))[1] = auth.uid()::text`.

Soft delete (`deleted_at`) on users/scans for the 30-day grace window, followed by hard purge job (privacy doc 09).

## Migration plan
`0001_extensions_and_enums` → `0002_reference_tables` → `0003_products` → `0004_scans` → `0005_rls_policies` → `0006_indexes` → seeds as separate idempotent scripts (not migrations).
