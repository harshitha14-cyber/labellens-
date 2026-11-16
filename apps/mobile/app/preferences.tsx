import { View, Text } from "react-native";
import { Chip, Loading, Screen, SectionTitle } from "@/components/ui";
import { useIngredients } from "@/api/hooks";
import { usePrefs } from "@/store";

const TAGS = ["Fragrance", "Alcohol", "Essential oils", "Sulphates", "Silicones"];

/** Screen 17: User preferences */
export default function Preferences() {
  const { data, isLoading } = useIngredients();
  const { avoid, prefer, tags, toggleAvoid, togglePrefer, toggleTag } = usePrefs();
  return (
    <Screen title="Preferences" back>
      <Text className="text-sm leading-5 text-muted">These personalise your report. They are your preferences, not medical advice.</Text>
      <SectionTitle hint="Flag these in every report">Avoid</SectionTitle>
      {isLoading ? <Loading /> : <View className="flex-row flex-wrap gap-2">{data?.map((i) => <Chip key={i.id} tone="avoid" label={i.canonicalName} selected={avoid.includes(i.id)} onPress={() => toggleAvoid(i.id)} />)}</View>}
      <SectionTitle hint="Highlight these when present">Prefer</SectionTitle>
      {!isLoading && <View className="flex-row flex-wrap gap-2">{data?.map((i) => <Chip key={i.id} label={i.canonicalName} selected={prefer.includes(i.id)} onPress={() => togglePrefer(i.id)} />)}</View>}
      <SectionTitle hint="Broader sensitivities">Sensitivity tags</SectionTitle>
      <View className="flex-row flex-wrap gap-2">{TAGS.map((t) => <Chip key={t} tone="avoid" label={t} selected={tags.includes(t)} onPress={() => toggleTag(t)} />)}</View>
    </Screen>
  );
}
