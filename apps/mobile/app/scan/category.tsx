import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Text, View } from "react-native";
import { Card, Loading, Screen } from "@/components/ui";
import { useCategories } from "@/api/hooks";
import { useDraft } from "@/store";

/** Screen 5: Product category selection */
export default function CategoryScreen() {
  const { data, isLoading } = useCategories();
  const setCategory = useDraft((s) => s.setCategory);
  return (
    <Screen title="What are you scanning?" back>
      <Text className="text-sm text-muted">Skincare and personal care for now. Food is planned for a later version.</Text>
      {isLoading ? <Loading /> : (
        <View className="flex-row flex-wrap gap-3">
          {data?.map((c) => (
            <Card key={c.id} className="w-[48%] items-center gap-2 py-5" onPress={() => { setCategory(c.id); router.push("/scan/camera"); }}>
              <Ionicons name={c.icon as never} size={30} color="#1F5D3A" /><Text className="text-base font-semibold text-ink">{c.name}</Text>
            </Card>
          ))}
        </View>
      )}
    </Screen>
  );
}
