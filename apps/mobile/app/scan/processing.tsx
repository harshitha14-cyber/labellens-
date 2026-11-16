import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useEffect, useState } from "react";
import { Text, View } from "react-native";
import { Button, Screen } from "@/components/ui";
import { useDraft } from "@/store";
import { ocrDraft } from "@/mocks/data";

const STEPS = ["Checking image quality", "Straightening and enhancing", "Reading text", "Finding the ingredient list", "Matching ingredient names"];

/** Screen 9: OCR processing (SIMULATED in Milestone 1; real OCR is Milestone 3) */
export default function Processing() {
  const [step, setStep] = useState(0);
  const setTokens = useDraft((s) => s.setTokens);
  useEffect(() => {
    if (step >= STEPS.length) { setTokens(ocrDraft.tokens); router.replace("/scan/confirm"); return; }
    const t = setTimeout(() => setStep((s) => s + 1), 650);
    return () => clearTimeout(t);
  }, [step, setTokens]);
  return (
    <Screen title="Reading your label" scroll={false} footer={<Button variant="ghost" label="Cancel" onPress={() => router.replace("/(tabs)/home")} />}>
      <View className="gap-3 pt-6" accessibilityLiveRegion="polite">
        {STEPS.map((s, i) => (
          <View key={s} className="flex-row items-center gap-3">
            <Ionicons name={i < step ? "checkmark-circle" : i === step ? "ellipse-outline" : "ellipse-outline"} size={22} color={i <= step ? "#1F5D3A" : "#C9C2B4"} />
            <Text className={`text-base ${i <= step ? "text-ink" : "text-muted"}`}>{s}{i === step ? "…" : ""}</Text>
          </View>
        ))}
      </View>
      <Text className="pt-6 text-xs text-muted">Simulated in this demo build. No image is actually analysed yet.</Text>
    </Screen>
  );
}
