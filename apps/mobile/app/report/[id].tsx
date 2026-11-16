import { Ionicons } from "@expo/vector-icons";
import { router, useLocalSearchParams } from "expo-router";
import { Text, View } from "react-native";
import { Button, Card, ClassBadge, Disclaimer, Loading, Screen, SectionTitle } from "@/components/ui";
import { useScan } from "@/api/hooks";
import { classOf, summarise } from "@/api/mockApi";
import { categories, ingredientById } from "@/mocks/data";
import { CLASS_COLORS, CLASS_META } from "@/theme/classes";
import { useDraft, usePrefs, useSaved } from "@/store";
import type { ClassId, Scan } from "@/types";

/** Screen 11: Ingredient analysis report */
export default function Report() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const draft = useDraft();
  const { data, isLoading, isError } = useScan(id === "draft" ? "draft" : id);
  const { avoid, prefer } = usePrefs();
  const { savedScanIds, toggleSaved } = useSaved();
  if (isLoading) return <Screen title="Report" back><Loading label="Analysing…" /></Screen>;
  if (isError || !data) return <Screen title="Report" back><Text className="text-c3">Could not load this report.</Text></Screen>;
  const scan: Scan = id === "draft" ? { ...data, tokens: draft.tokens, categoryId: draft.categoryId ?? data.categoryId } : data;
  const sum = summarise(scan);
  const catName = categories.find((c) => c.id === scan.categoryId)?.name;
  const flagged = scan.tokens.filter((t) => t.ingredientId && avoid.includes(t.ingredientId));
  const liked = scan.tokens.filter((t) => t.ingredientId && prefer.includes(t.ingredientId));
  const saved = savedScanIds.includes(scan.id);
  const completeText = scan.listComplete ? "Full ingredient list detected." : "We could not confirm this is the complete list. Results cover only what you confirmed.";
  return (
    <Screen title="Ingredient report" back footer={<View className="flex-row gap-2"><View className="flex-1"><Button variant="secondary" label={saved ? "Saved" : "Save"} icon={saved ? "bookmark" : "bookmark-outline"} onPress={() => toggleSaved(scan.id)} /></View><View className="flex-1"><Button label="Alternatives" icon="swap-horizontal" onPress={() => router.push("/alternatives")} /></View></View>}>
      <View><Text accessibilityRole="header" className="text-2xl font-bold text-ink">{scan.productName}</Text><Text className="text-sm text-muted">{[scan.brand, catName].filter(Boolean).join(" · ")}</Text></View>
      <Card className={`flex-row gap-3 ${scan.listComplete ? "bg-forest-soft" : "bg-[#FBEFD5]"}`}><Ionicons name={scan.listComplete ? "checkmark-circle" : "alert-circle"} size={22} color={scan.listComplete ? "#1F5D3A" : "#8A5A00"} /><Text className="flex-1 text-sm leading-5 text-ink">{completeText}</Text></Card>
      <Card className="gap-3">
        <Text className="text-base font-semibold text-ink">{sum.total} ingredients by classification</Text>
        <View className="h-3 flex-row overflow-hidden rounded-full bg-surface" accessibilityLabel="Distribution of classifications">
          {([1, 2, 3, 4, 5, 6] as ClassId[]).map((c) => sum.counts[c] > 0 ? <View key={c} style={{ flex: sum.counts[c], backgroundColor: CLASS_COLORS[c] }} /> : null)}
        </View>
        {([1, 2, 3, 4, 5, 6] as ClassId[]).filter((c) => sum.counts[c] > 0).map((c) => <View key={c} className="flex-row items-center justify-between"><ClassBadge cls={c} /><Text className="text-base font-semibold text-ink">{sum.counts[c]}</Text></View>)}
        <Text className="text-xs leading-5 text-muted">There is no single “score”: one number would hide what is unknown. Label order does not show concentration.</Text>
      </Card>
      {(flagged.length > 0 || liked.length > 0) && (<>
        <SectionTitle>Your preferences</SectionTitle>
        {flagged.map((t) => <Card key={t.position} className="bg-[#F8E1E1]"><Text className="text-sm text-ink">Contains <Text className="font-bold">{ingredientById(t.ingredientId!)?.canonicalName}</Text>, which is on your avoid list.</Text></Card>)}
        {liked.map((t) => <Card key={t.position} className="bg-forest-soft"><Text className="text-sm text-ink">Contains <Text className="font-bold">{ingredientById(t.ingredientId!)?.canonicalName}</Text>, which is on your prefer list.</Text></Card>)}
      </>)}
      <SectionTitle hint="Tap an ingredient for sources and detail">All ingredients</SectionTitle>
      {scan.tokens.map((t) => {
        const ing = t.ingredientId ? ingredientById(t.ingredientId) : undefined;
        const cls = classOf(t.ingredientId);
        return (
          <Card key={t.position} className="gap-2" onPress={ing ? () => router.push(`/ingredient/${ing.id}`) : undefined}>
            <View className="flex-row items-center justify-between"><Text className="flex-1 text-base font-semibold text-ink">{t.position}. {ing?.canonicalName ?? t.rawToken}</Text>{ing && <Ionicons name="chevron-forward" size={18} color="#55645A" />}</View>
            <ClassBadge cls={cls} compact />
            <Text className="text-sm leading-5 text-muted">{ing ? ing.functions.join(", ") : CLASS_META[6].explain}</Text>
          </Card>
        );
      })}
      <Button variant="ghost" label="Compare with another product" icon="git-compare-outline" onPress={() => router.push("/compare")} />
      <Disclaimer />
    </Screen>
  );
}
