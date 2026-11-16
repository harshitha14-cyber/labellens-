import type { ClassId } from "@/types";

/** Six classification states. Colour is never the only cue: icon + label always shown. */
export const CLASS_META: Record<ClassId, { label: string; short: string; icon: string; text: string; bg: string; explain: string }> = {
  1: { label: "Generally accepted for specified uses", short: "Accepted", icon: "checkmark-circle", text: "text-c1", bg: "bg-forest-soft", explain: "Supported by a cited assessment for the uses stated. This is not a guarantee for every product or concentration." },
  2: { label: "Concern identified in a specified context", short: "Context concern", icon: "alert-circle", text: "text-c2", bg: "bg-[#FBEFD5]", explain: "A cited concern applies in a specific context shown with the ingredient." },
  3: { label: "Restricted under a specified jurisdiction", short: "Restricted", icon: "shield-half", text: "text-c3", bg: "bg-[#F8E1E1]", explain: "Appears on a regulatory list with conditions. A label cannot show whether a product meets those conditions." },
  4: { label: "Insufficient evidence", short: "Limited evidence", icon: "help-circle", text: "text-c4", bg: "bg-[#E8EBEE]", explain: "Recognised, but no curated assessment is available yet." },
  5: { label: "Context dependent", short: "Depends", icon: "git-branch", text: "text-c5", bg: "bg-[#ECE5F6]", explain: "Depends on concentration, product type or individual sensitivity." },
  6: { label: "Unrecognised or unmatched", short: "Unmatched", icon: "search", text: "text-c6", bg: "bg-[#E3E8EC]", explain: "Not matched to a known ingredient. It has not been assessed." },
};

export const CLASS_COLORS: Record<ClassId, string> = {
  1: "#1F5D3A", 2: "#8A5A00", 3: "#9B2C2C", 4: "#4A5560", 5: "#5B3F8C", 6: "#3D4B57",
};
