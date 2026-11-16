import { Linking, Pressable, Text, View } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Card, ClassBadge, Disclaimer, Loading, Screen, SectionTitle } from "@/components/ui";
import { useIngredient } from "@/api/hooks";
import { CLASS_META } from "@/theme/classes";

/** Screen 12: Individual ingredient information */
export default function IngredientScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data: i, isLoading, isError } = useIngredient(id);
  if (isLoading) return <Screen title="Ingredient" back><Loading /></Screen>;
  if (isError || !i) return <Screen title="Ingredient" back><Text className="text-c3">Ingredient not found.</Text></Screen>;
  const indian = i.regulations.filter((r) => !r.referenceOnly);
  const ref = i.regulations.filter((r) => r.referenceOnly);
  return (
    <Screen title={i.canonicalName} back>
      <Text className="text-sm text-muted">INCI: {i.inciName}{i.casNumber ? ` · CAS ${i.casNumber}` : ""}</Text>
      {i.synonyms.length > 0 && <Text className="text-sm text-muted">Also known as: {i.synonyms.join(", ")}</Text>}
      <Text className="text-base leading-6 text-ink">{i.description}</Text>
      <View className="flex-row flex-wrap gap-2">{i.functions.map((f) => <View key={f} className="rounded-full bg-surface px-3 py-1"><Text className="text-sm text-ink">{f}</Text></View>)}</View>
      <SectionTitle>Assessment</SectionTitle>
      <Card className="gap-2">
        <ClassBadge cls={i.classification} />
        <Text className="text-sm text-muted">Context: {i.classContext}</Text>
        <Text className="text-base leading-6 text-ink">{i.summary}</Text>
        <Text className="text-xs text-muted">{CLASS_META[i.classification].explain}</Text>
        <Text className="text-xs text-muted">Confidence {Math.round(i.confidence * 100)}% · assessed {i.assessedOn}</Text>
      </Card>
      <SectionTitle hint="Indian status comes only from Indian sources">India regulatory status</SectionTitle>
      {indian.length === 0 ? <Card><Text className="text-sm text-muted">No Indian regulatory record loaded for this ingredient yet. That does not mean it is unregulated.</Text></Card> : indian.map((r) => (
        <Card key={r.regulationName} className="gap-1"><Text className="text-base font-semibold text-ink">{r.regulationName}</Text><Text className="text-sm text-ink">{r.provision} · {r.status}</Text>{r.conditions ? <Text className="text-sm text-muted">{r.conditions}</Text> : null}<Text className="text-xs text-muted">Last checked {r.lastChecked}</Text></Card>
      ))}
      {ref.length > 0 && (<><SectionTitle hint="Reference only. Not equivalent to Indian status">Other jurisdictions</SectionTitle>{ref.map((r) => <Card key={r.regulationName} className="gap-1 bg-surface"><Text className="text-sm font-semibold text-ink">{r.jurisdiction}: {r.regulationName}</Text><Text className="text-xs text-muted">{r.conditions}</Text></Card>)}</>)}
      <SectionTitle>Sources</SectionTitle>
      {i.citations.length === 0 ? <Card><Text className="text-sm text-muted">No sources yet, so we make no safety statement about this ingredient.</Text></Card> : i.citations.map((c) => (
        <Pressable key={c.title} accessibilityRole="link" onPress={() => Linking.openURL(c.url)}><Card className="gap-1"><Text className="text-base font-semibold text-forest-dark">{c.title}</Text><Text className="text-sm text-muted">{c.organisation} · checked {c.lastChecked}</Text></Card></Pressable>
      ))}
      <Disclaimer />
    </Screen>
  );
}
