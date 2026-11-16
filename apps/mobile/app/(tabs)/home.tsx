import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Text, View } from "react-native";
import { Button, Card, Loading, Row, Screen, SectionTitle } from "@/components/ui";
import { useScans } from "@/api/hooks";
import { useDraft, useSession } from "@/store";
import { categories } from "@/mocks/data";

/** Screen 4: Home dashboard */
export default function Home() {
  const name = useSession((s) => s.name);
  const reset = useDraft((s) => s.reset);
  const { data, isLoading } = useScans();
  return (
    <Screen>
      <View className="pt-2"><Text className="text-sm text-muted">Hello, {name}</Text><Text accessibilityRole="header" className="text-3xl font-bold text-ink">What are you checking today?</Text></View>
      <Card className="gap-3 bg-forest">
        <View className="flex-row items-center gap-3"><Ionicons name="scan-outline" size={28} color="#fff" /><Text className="flex-1 text-lg font-semibold text-white">Scan an ingredient label</Text></View>
        <Text className="text-sm leading-5 text-white">Works for any product, even ones we have never seen.</Text>
        <Button variant="secondary" label="Start a scan" icon="camera-outline" onPress={() => { reset(); router.push("/scan/category"); }} />
      </Card>
      <SectionTitle hint="Pick a category to begin">Categories</SectionTitle>
      <View className="flex-row flex-wrap gap-2">
        {categories.slice(0, 4).map((c) => (
          <Card key={c.id} className="w-[48%] items-center gap-2" onPress={() => { reset(); useDraft.getState().setCategory(c.id); router.push("/scan/camera"); }}>
            <Ionicons name={c.icon as never} size={26} color="#1F5D3A" /><Text className="text-base font-medium text-ink">{c.name}</Text>
          </Card>
        ))}
      </View>
      <SectionTitle>Recent scans</SectionTitle>
      {isLoading ? <Loading /> : data?.slice(0, 2).map((s) => <Row key={s.id} icon="document-text-outline" title={s.productName} subtitle={`${s.brand} · ${new Date(s.createdAt).toLocaleDateString()}`} onPress={() => router.push(`/report/${s.id}`)} />)}
      <Button variant="ghost" label="Compare two products" icon="swap-horizontal" onPress={() => router.push("/compare")} />
    </Screen>
  );
}
