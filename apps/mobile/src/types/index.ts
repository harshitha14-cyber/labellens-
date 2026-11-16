export type ClassId = 1 | 2 | 3 | 4 | 5 | 6;

export interface Category { id: string; name: string; icon: string; usage: "leave_on" | "rinse_off" | "sun" }

export interface Citation { organisation: string; title: string; url: string; lastChecked: string }

export interface Regulation {
  jurisdiction: "IN" | "EU" | "US";
  regulationName: string;
  provision: string;
  status: "prohibited" | "restricted" | "conditional" | "listed_permitted";
  conditions?: string;
  lastChecked: string;
  referenceOnly: boolean; // EU/US shown as reference, never as Indian status
}

export interface Ingredient {
  id: string;
  canonicalName: string;
  inciName: string;
  synonyms: string[];
  casNumber?: string;
  functions: string[];
  description: string;
  classification: ClassId;
  classContext: string;
  summary: string;
  confidence: number;
  assessedOn: string;
  citations: Citation[];
  regulations: Regulation[];
}

export type MatchMethod = "exact" | "synonym" | "fuzzy" | "manual" | "none";

export interface ScanToken {
  position: number;
  rawToken: string;
  ingredientId: string | null;
  matchMethod: MatchMethod;
  matchScore: number;
  ocrConfidence: number;
  suggestions?: { ingredientId: string; name: string; score: number }[];
}

export interface Scan {
  id: string;
  productName: string;
  brand: string;
  categoryId: string;
  createdAt: string;
  saved: boolean;
  listComplete: boolean;
  tokens: ScanToken[];
  verification: "VERIFIED" | "COMMUNITY_SUBMITTED" | "UNVERIFIED" | "NONE";
}

export interface Alternative {
  productName: string;
  brand: string;
  verification: "VERIFIED" | "COMMUNITY_SUBMITTED" | "UNVERIFIED";
  sourceDate: string;
  reasons: string[];
  sharedFunctions: string[];
}
