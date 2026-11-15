# 01 · Product Requirements Document — LabelLens India

Status: Milestone 0 draft · Date: 2026-11-15

## 1. Purpose
Help Indian consumers understand the ingredients in skincare and personal-care products by photographing the ingredient label. Analysis must work for products that exist in no database.

## 2. Users
| Persona | Need | Key behaviour |
|---|---|---|
| Ingredient-curious shopper | "What is in this and what does each thing do?" | Scans in-store; wants fast, plain-language output |
| Sensitivity-aware user | "Does this contain things I avoid?" | Sets avoid/prefer list once; scans repeatedly |
| Comparison shopper | "How does X differ from Y?" | Compares two products ingredient by ingredient |
| Contributor (later) | Adds missing Indian products | Submits label photos |

## 3. Scope
**In (MVP, cosmetics only):** sunscreen, moisturiser, face wash, serum, shampoo, conditioner, body wash, makeup. English-language labels.
**Out (MVP):** food analysis (architecture only), Hindi/Tamil OCR (architecture only), barcode-only lookup, prices, availability, e-commerce links, medical advice, an overall "safety score".

## 4. Functional requirements
IDs are referenced by acceptance criteria (doc 10).

| ID | Requirement |
|---|---|
| FR-01 | User selects a category before scanning |
| FR-02 | Capture via camera, or upload from gallery; 1–5 images per scan |
| FR-03 | Client-side crop/rotate preview before upload |
| FR-04 | Server validates type (JPEG/PNG/WEBP/HEIC→JPEG), size (≤10 MB), dimensions (≥600 px short side), strips EXIF/GPS |
| FR-05 | Preprocess: deskew/rotation fix, contrast/CLAHE, denoise; curved-label best effort |
| FR-06 | OCR English text with per-line confidence |
| FR-07 | Detect ingredient section (header variants + end markers); if not found, show full text and ask user to select |
| FR-08 | Clean and split into ingredient tokens; respect parentheses/brackets |
| FR-09 | Normalise tokens to canonical ingredients (exact → synonym → fuzzy); retain unmatched tokens visibly |
| FR-10 | Confirmation screen: edit, add, remove, reorder, accept/reject fuzzy suggestions; no silent auto-completion |
| FR-11 | Deterministic analysis of confirmed list in the context of the category |
| FR-12 | Report: per-ingredient function, classification (6 classes), evidence citations, India regulatory status, user-preference flags, list completeness indicator |
| FR-13 | Ingredient detail screen with full citations and "last assessed" date |
| FR-14 | Compare two scans/products: shared, only-in-A, only-in-B, function-grouped |
| FR-15 | Alternatives: comparable, verified, reasoned; explicit "no reliable alternative found" state |
| FR-16 | Save scans, history, favourites; delete any scan and its images |
| FR-17 | Preferences: avoid list, prefer list, sensitivity tags (fragrance, alcohol, etc.) |
| FR-18 | Auth (email + OTP/magic link; Google optional); account deletion and data export |
| FR-19 | Product catalogue record with verification status; unknown products allowed |
| FR-20 | App works with zero paid APIs; optional LLM text explanation is a plug-in, off by default |

## 5. Non-functional requirements
- **Accuracy over coverage:** unmatched is always shown as unmatched.
- **Latency target (MVP, CPU server):** single image OCR+parse ≤ 10 s p90 (to be measured in M3, not promised).
- **Privacy:** images private by default; EXIF stripped; retention configurable (default proposal: unsaved scan images deleted after 30 days).
- **Accessibility:** WCAG 2.1 AA contrast; dynamic type; screen-reader labels; never rely on colour alone for classification.
- **Platforms:** Android first-class (Indian market), iOS supported.
- **Offline:** history viewable offline (cached); scanning requires network.
- **Cost:** ₹0 development; documented limits for hosted free tiers.

## 6. Classification model (user-visible)
1. Generally accepted for specified uses — requires ≥1 citation.
2. Concern identified in a specified context — context and citation shown.
3. Restricted under a specified jurisdiction — jurisdiction + provision shown; sub-type: prohibited / restricted / conditional.
4. Insufficient evidence — matched, no curated assessment.
5. Context dependent — depends on concentration, product type or individual sensitivity.
6. Unrecognised / unmatched.

**Decision rule order (deterministic):** unmatched → 6; India regulation hit → 3; contextual concern record → 2; context-dependent flag → 5; cited accepted-use record → 1; else 4. Class 1 can never be assigned without a citation.

**No overall product score in the MVP.** A single number implies precision the evidence does not support. Report shows a distribution (counts per class) and completeness instead. *(Decision D-004, needs your confirmation.)*

## 7. Claims policy (hard rules)
- Never infer concentration from label order.
- Distinguish hazard vs risk; regulatory status vs personal sensitivity.
- Never diagnose; never say "safe"/"toxic" unqualified.
- EU/US status shown only as labelled reference, never as Indian status.
- Product-level wording is neutral and factual (defamation/consumer-law risk).
- Every safety statement links to a source record.

## 8. Success metrics (post-MVP, for planning only)
Ingredient match rate on a held-out set of Indian labels; % tokens user-corrected; scan completion rate; report-view-to-save rate. Targets are set in M3/M4 after measurement.

## 9. Assumptions & open questions
See DECISIONS.md (D-003 Expo SDK pin, D-004 no score, D-006 extra tables, D-008 OCR hosting) and doc 09 (risks).
