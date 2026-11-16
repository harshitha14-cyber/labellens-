import { Text, View } from "react-native";
import { Card, ClassBadge, Loading, Screen, SectionTitle } from "@/components/ui";
import { useScans } from "@/api/hooks";
import { classOf } from "@/api/mockApi";
import { ingredientById } from "@/mocks/data";
import type { Scan } from "@/types";

const ids = (s: Scan) => new Set(s.tokens.map((t) => t.ingredientId ?? `raw:${t.rawToken.toLowerCase()}`));
const label = (key: string) => (key.startsWith("raw:") ? key.slice(4) : ingredientById(key)?.canonicalName ?? key);

function Group({ title, keys, tone }: { title: string; keys: string[]; tone?: string }) {
  return (
    <Card className={`gap-2 ${tone ?? ""}`}><Text className="text-base font-semibold text-ink">{title} ({keys.length})</Text>
      {keys.length === 0 ? <Text className="text-sm text-muted">None</Text> : keys.map((k) => <View key={k} className="flex-row items-center justify-between gap-2"><Text className="flex-1 text-sm text-ink">{label(k)}</Text><ClassBadge cls={classOf(k.startsWith("raw:") ? null : k)} compact /></View>)}
    </Card>
  );
}

/** Screen 13: Product comparison. Shows differences; never declares a winner. */
export default function Compare() {
  const { data, isLoading } = useScans();
  if (isLoading || !data) return <Screen title="Compare" back><Loading /></Screen>;
  const a = data[0]!, b = data[1]!;
  const A = ids(a), B = ids(b);
  const shared = [...A].filter((x) => B.has(x));
  const onlyA = [...A].filter((x) => !B.has(x));
  const onlyB = [...B].filter((x) => !A.has(x));
  return (
    <Screen title="Compare products" back>
      <View className="flex-row gap-2"><Card className="flex-1"><Text className="text-xs text-muted">Product A</Text><Text className="text-sm font-semibold text-ink">{a.productName}</Text></Card><Card className="flex-1"><Text className="text-xs text-muted">Product B</Text><Text className="text-sm font-semibold text-ink">{b.productName}</Text></Card></View>
      <Text className="text-sm leading-5 text-muted">This shows what differs, not which is “better”. Fewer ingredients does not mean higher quality.</Text>
      <SectionTitle>In both</SectionTitle><Group title="Shared ingredients" keys={shared} />
      <SectionTitle>Only in A</SectionTitle><Group title={a.productName} keys={onlyA} />
      <SectionTitle>Only in B</SectionTitle><Group title={b.productName} keys={onlyB} />
    </Screen>
  );
}
