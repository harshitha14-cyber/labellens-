import { router } from "expo-router";
import { Text } from "react-native";
import { Loading, Row, Screen } from "@/components/ui";
import { useScans } from "@/api/hooks";
import { useSaved } from "@/store";

/** Screen 16: Saved products */
export default function Saved() {
  const { data, isLoading } = useScans();
  const ids = useSaved((s) => s.savedScanIds);
  const list = data?.filter((s) => ids.includes(s.id)) ?? [];
  return (
    <Screen title="Saved">
      {isLoading ? <Loading /> : list.length === 0 ? <Text className="text-muted">Nothing saved yet. Open a report and tap Save.</Text> : list.map((s) => <Row key={s.id} icon="bookmark" title={s.productName} subtitle={s.brand} onPress={() => router.push(`/report/${s.id}`)} />)}
    </Screen>
  );
}
