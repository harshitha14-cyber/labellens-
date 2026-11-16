import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useState } from "react";
import { Text, View } from "react-native";
import { Button, Screen } from "@/components/ui";
import { useSession } from "@/store";

const slides = [
  { icon: "camera-outline", title: "Photograph the label", body: "Works even if the product is in no database. Just photograph the ingredient list." },
  { icon: "create-outline", title: "Check what we read", body: "You confirm and correct the extracted list. We never invent ingredients to fill gaps." },
  { icon: "document-text-outline", title: "Evidence, not scare scores", body: "Every statement shows its source and date. Where evidence is missing, we say so." },
] as const;

/** Screen 2: Onboarding */
export default function Onboarding() {
  const [i, setI] = useState(0);
  const finish = useSession((s) => s.finishOnboarding);
  const s = slides[i]!;
  const last = i === slides.length - 1;
  return (
    <Screen scroll={false} demo={false} footer={<View className="gap-2"><Button label={last ? "Get started" : "Next"} onPress={() => (last ? (finish(), router.replace("/(auth)/login")) : setI(i + 1))} />{!last && <Button variant="ghost" label="Skip" onPress={() => { finish(); router.replace("/(auth)/login"); }} />}</View>}>
      <View className="flex-1 items-center justify-center gap-5 px-2">
        <View className="h-28 w-28 items-center justify-center rounded-full bg-forest-soft"><Ionicons name={s.icon} size={52} color="#1F5D3A" /></View>
        <Text accessibilityRole="header" className="text-center text-2xl font-bold text-ink">{s.title}</Text>
        <Text className="text-center text-base leading-6 text-muted">{s.body}</Text>
        <View className="flex-row gap-2">{slides.map((_, k) => <View key={k} className={`h-2 rounded-full ${k === i ? "w-6 bg-forest" : "w-2 bg-line"}`} />)}</View>
      </View>
    </Screen>
  );
}
