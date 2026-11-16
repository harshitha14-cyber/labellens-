import { router } from "expo-router";
import { Text } from "react-native";
import { ClassBadge, Loading, Row, Screen } from "@/components/ui";
import { useScans } from "@/api/hooks";
import { categories } from "@/mocks/data";
import { summarise } from "@/api/mockApi";

/** Screen 15: Scan history */
export default function History() {
  const { data, isLoading, isError, refetch } = useScans();
  return (
    <Screen title="Scan history">
      {isLoading ? <Loading /> : isError ? <Text onPress={() => refetch()} className="text-c3">Could not load. Tap to retry.</Text> : data?.length === 0 ? <Text className="text-muted">No scans yet.</Text> :
        data?.map((s) => {
          const sum = summarise(s);
          return <Row key={s.id} icon="time-outline" title={s.productName} subtitle={`${categories.find((c) => c.id === s.categoryId)?.name} · ${new Date(s.createdAt).toLocaleDateString()} · ${sum.total} ingredients`} onPress={() => router.push(`/report/${s.id}`)} right={sum.unmatched ? <ClassBadge cls={6} compact /> : undefined} />;
        })}
    </Screen>
  );
}
