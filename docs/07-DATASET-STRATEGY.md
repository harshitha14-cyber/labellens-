# 07 · Dataset Integration Strategy

Principle: every record carries provenance (`data_imports` row + source URL + licence + checked date). Imports are idempotent scripts in `services/api/data_pipeline/`, never hand-edited SQL.

| Dataset | Used for | Licence (to confirm with counsel at M5) | Method | Constraints |
|---|---|---|---|---|
| **Open Beauty Facts** | Product names/brands/ingredient text, India subset | Database under ODbL, contents under DbCL, images CC BY-SA (individually) — *share-alike/attribution obligations may apply to a derived database* | Bulk export or API; filter `countries_tags` for India; stage in `UNVERIFIED` | Keep OBF-derived rows tagged by `import_id` so they can be separated, published or removed. Indian coverage is unknown until sampled (M5 first task: measure it, don't assume). Ingredient text is user-entered → incomplete/wrong often |
| **User submissions** | Fill Indian gaps | Our terms (grant licence on submit) | Scan → confirmed list → `POST /products` → `COMMUNITY_SUBMITTED` | Moderation + verification workflow needed; never auto-promote |
| **Manufacturer pages** | Verified lists | Copyright of site | Manual/assisted capture of **facts** with URL + date; no scraping at scale in MVP | Check each site's terms/robots; store source URL and capture date |
| **PubChem** | CAS, CID, InChIKey, synonyms | NCBI data; generally open, some depositor data has own terms | PUG-REST lookups, cached | Respect rate limit (about 5 req/s per NCBI guidance — verify), identifiers only, cite CID |
| **CIR** | Evidence references | CIR reports are copyrighted publications | Store conclusion category + citation + URL; **no full-text copying** | Manual curation, versioned `assessed_on` |
| **EU CosIng** | Function terms, INCI names, EU reference status | EU reuse policy (typically permissive, attribution) — verify | Import INCI/function; EU status stored with `jurisdiction='EU'` and rendered as "reference only" | CosIng's current download availability not verified today |
| **IS 4707 / Cosmetics Rules 2020 / CDSCO** | Indian regulatory records | Government rules are public; **BIS standards are sold/copyrighted documents** | See doc 08 | Store structured facts + citation, not document text |

## Import pipeline stages
fetch (store raw + checksum) → parse → map to schema → validate (required fields, CAS format, no duplicate keys) → dry-run diff report → load in transaction → record `data_imports`.

## Seed sizing (MVP target to prove the engine, not coverage claims)
Curated ingredient set sized after sampling real Indian labels in M3/M4 (frequency-ranked). Coverage % will be **measured and reported**, not asserted.

## Quality gates
- No product enters `VERIFIED` without a recorded source and checker.
- `ingredient_list_complete=false` unless the list covers the full labelled section.
- Duplicates resolved by (brand, name, identifier) rules; conflicts kept as separate rows flagged for review.
