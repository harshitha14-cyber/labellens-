import { Ionicons } from "@expo/vector-icons";
import { Text, View } from "react-native";
import { Card, Loading, Screen, SectionTitle } from "@/components/ui";
import { useAlternatives } from "@/api/hooks";
import { usePrefs } from "@/store";

/** Screen 14: Alternative products. Every result is explained; empty state is valid. */
export default function Alternatives() {
  const { data, isLoading } = useAlternatives();
  const includeCommunity = usePrefs((s) => s.includeCommunity);
  const list = (data ?? []).filter((a) => a.verification === "VERIFIED" || includeCommunity);
  return (
    <Screen title="Comparable products" back>
      <Text className="text-sm leading-5 text-muted">Same category and function, with a complete ingredient list. We do not show prices or availability.</Text>
      {isLoading ? <Loading /> : list.length === 0 ? (
        <Card className="gap-2"><Text className="text-base font-semibold text-ink">No reliable alternative found</Text><Text className="text-sm leading-5 text-muted">We only suggest products with a verified, complete ingredient list. None match yet. You can enable community-submitted products in Settings.</Text></Card>
      ) : list.map((a) => (
        <Card key={a.productName} className="gap-2">
          <Text className="text-base font-semibold text-ink">{a.productName}</Text><Text className="text-sm text-muted">{a.brand}</Text>
          <View className={`flex-row items-center gap-1.5 self-start rounded-full px-2.5 py-1 ${a.verification === "VERIFIED" ? "bg-forest-soft" : "bg-surface"}`}><Ionicons name={a.verification === "VERIFIED" ? "shield-checkmark" : "people"} size={14} color="#164A2D" /><Text className="text-xs font-semibold text-forest-dark">{a.verification === "VERIFIED" ? "Verified" : "Community submitted — unverified"}</Text></View>
          <SectionTitle>Why this is suggested</SectionTitle>
          {a.reasons.map((r) => <Text key={r} className="text-sm leading-5 text-ink">• {r}</Text>)}
          <Text className="text-xs text-muted">Ingredient list source date: {a.sourceDate}</Text>
        </Card>
      ))}
    </Screen>
  );
}
