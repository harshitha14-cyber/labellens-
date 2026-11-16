/** Mock API used only in Milestone 1. Replaced by the real FastAPI client in Milestone 2. */
import { alternatives, categories, ingredientById, ingredients, ocrDraft, scans } from "@/mocks/data";
import type { Alternative, Category, ClassId, Ingredient, Scan } from "@/types";

const delay = <T,>(value: T, ms = 350): Promise<T> => new Promise((r) => setTimeout(() => r(value), ms));

export const api = {
  categories: (): Promise<Category[]> => delay(categories, 100),
  scans: (): Promise<Scan[]> => delay(scans),
  scan: async (id: string): Promise<Scan> => {
    const s = id === "draft" ? ocrDraft : scans.find((x) => x.id === id);
    if (!s) throw new Error("Scan not found");
    return delay(s);
  },
  ingredient: async (id: string): Promise<Ingredient> => {
    const i = ingredientById(id);
    if (!i) throw new Error("Ingredient not found");
    return delay(i, 200);
  },
  ingredients: (): Promise<Ingredient[]> => delay(ingredients, 100),
  alternatives: (): Promise<Alternative[]> => delay(alternatives),
};

export interface ReportSummary {
  counts: Record<ClassId, number>;
  total: number;
  unmatched: number;
}

/** Pure helper: same input always gives same output (mirrors the deterministic engine's contract). */
export function summarise(scan: Scan): ReportSummary {
  const counts: Record<ClassId, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 };
  for (const t of scan.tokens) {
    const ing = t.ingredientId ? ingredientById(t.ingredientId) : undefined;
    counts[ing ? ing.classification : 6] += 1;
  }
  return { counts, total: scan.tokens.length, unmatched: counts[6] };
}

export function classOf(ingredientId: string | null): ClassId {
  const ing = ingredientId ? ingredientById(ingredientId) : undefined;
  return ing ? ing.classification : 6;
}

/** Demo-only exact name/synonym matcher used when the user edits a line (real normaliser: Milestone 4). */
export function matchLocal(text: string): string | null {
  const q = text.trim().toLowerCase();
  if (!q) return null;
  const hit = ingredients.find((i) => [i.canonicalName, i.inciName, ...i.synonyms].some((n) => n.toLowerCase() === q));
  return hit ? hit.id : null;
}
