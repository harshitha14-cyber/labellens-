import { useState } from "react";
import { Switch, Text, View } from "react-native";
import { Card, Disclaimer, Screen, SectionTitle } from "@/components/ui";
import { usePrefs } from "@/store";

function Item({ title, sub, value, onChange }: { title: string; sub: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <Card className="flex-row items-center gap-3"><View className="flex-1"><Text className="text-base font-semibold text-ink">{title}</Text><Text className="text-sm text-muted">{sub}</Text></View><Switch accessibilityLabel={title} value={value} onValueChange={onChange} trackColor={{ true: "#1F5D3A", false: "#E3DCCF" }} /></Card>
  );
}

/** Screen 19: Settings */
export default function Settings() {
  const { includeCommunity, setCommunity } = usePrefs();
  const [keep, setKeep] = useState(true);
  return (
    <Screen title="Settings" back>
      <SectionTitle>Data</SectionTitle>
      <Item title="Use community-submitted products" sub="Include products awaiting verification in alternatives (always labelled)." value={includeCommunity} onChange={setCommunity} />
      <Item title="Keep my scan photos for 30 days" sub="Unsaved scan photos are deleted after 30 days." value={keep} onChange={setKeep} />
      <SectionTitle>About</SectionTitle>
      <Card className="gap-2"><Text className="text-base text-ink">LabelLens India · v0.1.0 (Milestone 1, demo data)</Text><Text className="text-sm text-muted">Language: English (more Indian languages planned)</Text></Card>
      <Disclaimer />
    </Screen>
  );
}
