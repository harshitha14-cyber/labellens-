import { create } from "zustand";
import type { ScanToken } from "@/types";

interface SessionState { signedIn: boolean; onboarded: boolean; name: string; signIn: (n: string) => void; signOut: () => void; finishOnboarding: () => void }
export const useSession = create<SessionState>((set) => ({
  signedIn: false, onboarded: false, name: "Guest",
  signIn: (name) => set({ signedIn: true, name }),
  signOut: () => set({ signedIn: false, name: "Guest" }),
  finishOnboarding: () => set({ onboarded: true }),
}));

interface DraftState {
  categoryId: string | null;
  imageUris: string[];
  tokens: ScanToken[];
  setCategory: (id: string) => void;
  addImages: (uris: string[]) => void;
  removeImage: (uri: string) => void;
  setTokens: (t: ScanToken[]) => void;
  reset: () => void;
}
export const useDraft = create<DraftState>((set) => ({
  categoryId: null, imageUris: [], tokens: [],
  setCategory: (categoryId) => set({ categoryId }),
  addImages: (uris) => set((s) => ({ imageUris: [...s.imageUris, ...uris].slice(0, 5) })),
  removeImage: (uri) => set((s) => ({ imageUris: s.imageUris.filter((u) => u !== uri) })),
  setTokens: (tokens) => set({ tokens }),
  reset: () => set({ categoryId: null, imageUris: [], tokens: [] }),
}));

interface PrefState {
  avoid: string[]; prefer: string[]; tags: string[]; includeCommunity: boolean;
  toggleAvoid: (id: string) => void; togglePrefer: (id: string) => void; toggleTag: (t: string) => void; setCommunity: (v: boolean) => void;
}
const toggle = (arr: string[], v: string) => (arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);
export const usePrefs = create<PrefState>((set) => ({
  avoid: ["fragrance"], prefer: ["niacinamide"], tags: [], includeCommunity: false,
  toggleAvoid: (id) => set((s) => ({ avoid: toggle(s.avoid, id) })),
  togglePrefer: (id) => set((s) => ({ prefer: toggle(s.prefer, id) })),
  toggleTag: (t) => set((s) => ({ tags: toggle(s.tags, t) })),
  setCommunity: (includeCommunity) => set({ includeCommunity }),
}));

interface SavedState { savedScanIds: string[]; toggleSaved: (id: string) => void }
export const useSaved = create<SavedState>((set) => ({
  savedScanIds: ["scan-1"],
  toggleSaved: (id) => set((s) => ({ savedScanIds: toggle(s.savedScanIds, id) })),
}));
