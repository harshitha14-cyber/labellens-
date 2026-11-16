import { classOf, matchLocal, summarise } from "@/api/mockApi";
import { ingredients, scans, ocrDraft } from "@/mocks/data";
import { useDraft, usePrefs } from "@/store";

describe("summarise / classOf", () => {
  it("counts every token exactly once", () => {
    for (const s of scans) {
      const sum = summarise(s);
      const total = (Object.values(sum.counts) as number[]).reduce((a, b) => a + b, 0);
      expect(total).toBe(s.tokens.length);
    }
  });
  it("unmatched tokens are class 6, never silently dropped", () => {
    expect(classOf(null)).toBe(6);
    expect(summarise(scans[0]!).counts[6]).toBe(1);
  });
  it("is deterministic: same input, same output", () => {
    expect(summarise(scans[0]!)).toEqual(summarise(scans[0]!));
  });
  it("ingredient order never changes classification", () => {
    const rev = { ...scans[0]!, tokens: [...scans[0]!.tokens].reverse() };
    expect(summarise(rev).counts).toEqual(summarise(scans[0]!).counts);
  });
});

describe("demo data integrity", () => {
  it("class 1 ingredients all have at least one citation", () => {
    for (const i of ingredients.filter((x) => x.classification === 1)) expect(i.citations.length).toBeGreaterThan(0);
  });
  it("EU/US regulations are always flagged reference-only", () => {
    for (const r of ingredients.flatMap((i) => i.regulations)) if (r.jurisdiction !== "IN") expect(r.referenceOnly).toBe(true);
  });
  it("every token's ingredientId exists or is null", () => {
    for (const t of [...scans, ocrDraft].flatMap((s) => s.tokens)) if (t.ingredientId) expect(ingredients.some((i) => i.id === t.ingredientId)).toBe(true);
  });
});

describe("matchLocal", () => {
  it("matches names and synonyms case-insensitively", () => {
    expect(matchLocal("aqua")).toBe("water");
    expect(matchLocal("VITAMIN E")).toBe("tocopherol");
  });
  it("does not fuzzy-guess: OCR error stays unmatched", () => {
    expect(matchLocal("Zinc 0xide")).toBeNull();
    expect(matchLocal("")).toBeNull();
  });
});

describe("stores", () => {
  it("draft keeps at most 5 images", () => {
    useDraft.getState().reset();
    useDraft.getState().addImages(["1", "2", "3", "4", "5", "6", "7"]);
    expect(useDraft.getState().imageUris).toHaveLength(5);
  });
  it("preferences toggle avoid", () => {
    usePrefs.setState({ avoid: [] });
    usePrefs.getState().toggleAvoid("fragrance");
    expect(usePrefs.getState().avoid).toEqual(["fragrance"]);
    usePrefs.getState().toggleAvoid("fragrance");
    expect(usePrefs.getState().avoid).toEqual([]);
  });
});
