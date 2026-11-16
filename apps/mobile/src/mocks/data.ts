/**
 * DEMO DATA ONLY (Milestone 1).
 * Ingredient names are real INCI-style names; every assessment, source and
 * regulation record below is a PLACEHOLDER to exercise the UI. None of it is
 * real safety or regulatory information. Real data arrives in Milestones 4-5.
 */
import type { Alternative, Category, Ingredient, Scan } from "@/types";

export const DEMO_NOTICE = "Demo data — illustrative only, not real assessments";

const demoSource = (title: string) => ({
  organisation: "Demo source (placeholder)",
  title,
  url: "https://example.org/demo-source",
  lastChecked: "2026-11-01",
});

export const categories: Category[] = [
  { id: "sunscreen", name: "Sunscreen", icon: "sunny-outline", usage: "sun" },
  { id: "moisturiser", name: "Moisturiser", icon: "water-outline", usage: "leave_on" },
  { id: "face-wash", name: "Face wash", icon: "happy-outline", usage: "rinse_off" },
  { id: "serum", name: "Serum", icon: "flask-outline", usage: "leave_on" },
  { id: "shampoo", name: "Shampoo", icon: "sparkles-outline", usage: "rinse_off" },
  { id: "conditioner", name: "Conditioner", icon: "leaf-outline", usage: "rinse_off" },
  { id: "body-wash", name: "Body wash", icon: "body-outline", usage: "rinse_off" },
  { id: "makeup", name: "Makeup", icon: "color-palette-outline", usage: "leave_on" },
];

export const ingredients: Ingredient[] = [
  {
    id: "water", canonicalName: "Water", inciName: "Aqua", synonyms: ["Aqua", "Eau", "Purified water"],
    casNumber: "7732-18-5", functions: ["solvent"],
    description: "The base solvent in most water-based cosmetic formulas.",
    classification: 1, classContext: "general cosmetic use",
    summary: "Demo: listed as an accepted base ingredient.", confidence: 0.9, assessedOn: "2026-11-01",
    citations: [demoSource("Demo reference for water")], regulations: [],
  },
  {
    id: "glycerin", canonicalName: "Glycerin", inciName: "Glycerin", synonyms: ["Glycerol", "Glycerine"],
    casNumber: "56-81-5", functions: ["humectant", "skin conditioning"],
    description: "A humectant that attracts and holds water in the product and on skin.",
    classification: 1, classContext: "leave-on and rinse-off products",
    summary: "Demo: accepted for the specified uses.", confidence: 0.85, assessedOn: "2026-11-01",
    citations: [demoSource("Demo reference for glycerin")], regulations: [],
  },
  {
    id: "zinc-oxide", canonicalName: "Zinc Oxide", inciName: "Zinc Oxide", synonyms: ["ZnO", "CI 77947"],
    casNumber: "1314-13-2", functions: ["UV filter", "colorant"],
    description: "A mineral UV filter used in sunscreens; also used as a colourant.",
    classification: 5, classContext: "depends on particle form and use",
    summary: "Demo: assessment depends on particle form, product type and concentration, which a label alone cannot show.",
    confidence: 0.7, assessedOn: "2026-11-01",
    citations: [demoSource("Demo reference for zinc oxide")],
    regulations: [{ jurisdiction: "IN", regulationName: "IS 4707 (Part 4) — DEMO RECORD", provision: "Demo entry", status: "conditional", conditions: "Demo: maximum concentration applies when used as a UV filter.", lastChecked: "2026-11-01", referenceOnly: false }],
  },
  {
    id: "niacinamide", canonicalName: "Niacinamide", inciName: "Niacinamide", synonyms: ["Vitamin B3", "Nicotinamide"],
    casNumber: "98-92-0", functions: ["skin conditioning"],
    description: "A form of vitamin B3 used for skin conditioning.",
    classification: 1, classContext: "leave-on products",
    summary: "Demo: accepted for the specified uses.", confidence: 0.8, assessedOn: "2026-11-01",
    citations: [demoSource("Demo reference for niacinamide")], regulations: [],
  },
  {
    id: "fragrance", canonicalName: "Fragrance", inciName: "Parfum", synonyms: ["Parfum", "Fragrance", "Perfume"],
    functions: ["fragrance"],
    description: "A blend of scent ingredients. The label usually does not list each component.",
    classification: 5, classContext: "individual sensitivity and component mix",
    summary: "Demo: not all fragrance is harmful; suitability depends on the components and on individual sensitivity.",
    confidence: 0.6, assessedOn: "2026-11-01",
    citations: [demoSource("Demo reference for fragrance")], regulations: [],
  },
  {
    id: "phenoxyethanol", canonicalName: "Phenoxyethanol", inciName: "Phenoxyethanol", synonyms: [],
    casNumber: "122-99-6", functions: ["preservative"],
    description: "A preservative that helps stop microbial growth in water-based products.",
    classification: 3, classContext: "restricted by maximum concentration (DEMO)",
    summary: "Demo: appears on a restricted-use list with conditions. Listing alone does not show whether a given product complies.",
    confidence: 0.75, assessedOn: "2026-11-01",
    citations: [demoSource("Demo preservative list entry")],
    regulations: [
      { jurisdiction: "IN", regulationName: "IS 4707 (Part 3) — DEMO RECORD", provision: "Demo entry", status: "restricted", conditions: "Demo: maximum concentration and product-type conditions.", lastChecked: "2026-11-01", referenceOnly: false },
      { jurisdiction: "EU", regulationName: "EU reference — DEMO RECORD", provision: "Demo annex", status: "restricted", conditions: "Reference only — not Indian status.", lastChecked: "2026-11-01", referenceOnly: true },
    ],
  },
  {
    id: "dimethicone", canonicalName: "Dimethicone", inciName: "Dimethicone", synonyms: ["Silicone oil"],
    functions: ["skin conditioning", "emollient"],
    description: "A silicone used for slip and a smooth feel.",
    classification: 4, classContext: "no curated assessment yet",
    summary: "Demo: matched, but no assessment has been added for this ingredient yet.", confidence: 0.3, assessedOn: "2026-11-01",
    citations: [], regulations: [],
  },
  {
    id: "tocopherol", canonicalName: "Tocopherol", inciName: "Tocopherol", synonyms: ["Vitamin E"],
    casNumber: "10191-41-0", functions: ["antioxidant"],
    description: "Vitamin E, used as an antioxidant in formulas.",
    classification: 2, classContext: "demo: concern noted for sensitive skin in some contexts",
    summary: "Demo: a context-specific note, shown to exercise the 'concern in a specified context' state.",
    confidence: 0.5, assessedOn: "2026-11-01",
    citations: [demoSource("Demo reference for tocopherol")], regulations: [],
  },
];

export const ingredientById = (id: string) => ingredients.find((i) => i.id === id);

export const scans: Scan[] = [
  {
    id: "scan-1", productName: "Sample Mineral Sunscreen SPF 50", brand: "Demo Brand", categoryId: "sunscreen",
    createdAt: "2026-11-14T09:30:00Z", saved: true, listComplete: true, verification: "NONE",
    tokens: [
      { position: 1, rawToken: "Aqua", ingredientId: "water", matchMethod: "synonym", matchScore: 1, ocrConfidence: 0.98 },
      { position: 2, rawToken: "Zinc Oxide", ingredientId: "zinc-oxide", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.96 },
      { position: 3, rawToken: "Glycerin", ingredientId: "glycerin", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.97 },
      { position: 4, rawToken: "Niacinamide", ingredientId: "niacinamide", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.95 },
      { position: 5, rawToken: "Dimethicone", ingredientId: "dimethicone", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.94 },
      { position: 6, rawToken: "Phenoxyethanol", ingredientId: "phenoxyethanol", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.93 },
      { position: 7, rawToken: "Parfum", ingredientId: "fragrance", matchMethod: "synonym", matchScore: 1, ocrConfidence: 0.92 },
      { position: 8, rawToken: "Madhuca Longifolia Seed Oil", ingredientId: null, matchMethod: "none", matchScore: 0.41, ocrConfidence: 0.88 },
    ],
  },
  {
    id: "scan-2", productName: "Sample Daily Moisturiser", brand: "Demo Brand", categoryId: "moisturiser",
    createdAt: "2026-11-10T16:05:00Z", saved: false, listComplete: true, verification: "NONE",
    tokens: [
      { position: 1, rawToken: "Aqua", ingredientId: "water", matchMethod: "synonym", matchScore: 1, ocrConfidence: 0.98 },
      { position: 2, rawToken: "Glycerin", ingredientId: "glycerin", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.97 },
      { position: 3, rawToken: "Niacinamide", ingredientId: "niacinamide", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.96 },
      { position: 4, rawToken: "Tocopherol", ingredientId: "tocopherol", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.9 },
      { position: 5, rawToken: "Phenoxyethanol", ingredientId: "phenoxyethanol", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.91 },
    ],
  },
];

/** Output of a simulated OCR run, used by the confirmation screen. */
export const ocrDraft: Scan = {
  id: "draft", productName: "Unnamed product", brand: "", categoryId: "sunscreen",
  createdAt: "2026-11-15T10:00:00Z", saved: false, listComplete: false, verification: "NONE",
  tokens: [
    { position: 1, rawToken: "Aqua", ingredientId: "water", matchMethod: "synonym", matchScore: 1, ocrConfidence: 0.97 },
    { position: 2, rawToken: "Zinc 0xide", ingredientId: null, matchMethod: "fuzzy", matchScore: 0.9, ocrConfidence: 0.71, suggestions: [{ ingredientId: "zinc-oxide", name: "Zinc Oxide", score: 0.9 }] },
    { position: 3, rawToken: "Glycerin", ingredientId: "glycerin", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.95 },
    { position: 4, rawToken: "Phenoxyethanol", ingredientId: "phenoxyethanol", matchMethod: "exact", matchScore: 1, ocrConfidence: 0.9 },
    { position: 5, rawToken: "Aloe Barbadensis Leaf Ext", ingredientId: null, matchMethod: "none", matchScore: 0.5, ocrConfidence: 0.84 },
  ],
};

export const alternatives: Alternative[] = [
  { productName: "Sample Mineral Sunscreen B", brand: "Demo Brand Two", verification: "VERIFIED", sourceDate: "2026-09-12",
    reasons: ["Same category: sunscreen", "Complete, verified ingredient list", "No ingredient from your avoid list", "Shares UV filter and humectant functions"],
    sharedFunctions: ["UV filter", "humectant"] },
  { productName: "Sample Fragrance-free Sunscreen C", brand: "Demo Brand Three", verification: "COMMUNITY_SUBMITTED", sourceDate: "2026-10-30",
    reasons: ["Same category: sunscreen", "Does not list fragrance (your avoid list)", "Ingredient list awaiting independent verification"],
    sharedFunctions: ["UV filter"] },
];
