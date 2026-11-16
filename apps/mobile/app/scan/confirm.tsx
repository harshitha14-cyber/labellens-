import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { Button, Card, ClassBadge, Screen, SectionTitle } from "@/components/ui";
import { useDraft } from "@/store";
import { classOf, matchLocal } from "@/api/mockApi";
import type { ScanToken } from "@/types";

/** Screen 10: Ingredient confirmation. Nothing is auto-completed; unmatched stays unmatched. */
export default function Confirm() {
  const { tokens, setTokens } = useDraft();
  const [adding, setAdding] = useState("");
  const update = (pos: number, patch: Partial<ScanToken>) => setTokens(tokens.map((t) => (t.position === pos ? { ...t, ...patch } : t)));
  const remove = (pos: number) => setTokens(tokens.filter((t) => t.position !== pos).map((t, i) => ({ ...t, position: i + 1 })));
  const add = () => { const v = adding.trim(); if (!v) return; setTokens([...tokens, { position: tokens.length + 1, rawToken: v, ingredientId: null, matchMethod: "none", matchScore: 0, ocrConfidence: 1 }]); setAdding(""); };
  const needsReview = tokens.filter((t) => t.suggestions?.length && !t.ingredientId).length;
  return (
    <Screen title="Confirm ingredients" back footer={<Button label="Analyse ingredients" icon="analytics-outline" disabled={!tokens.length} onPress={() => router.push("/report/draft")} />}>
      <Card className="gap-1 bg-surface"><Text className="text-sm leading-5 text-ink">Check each line against your label. Fix mistakes, remove extras, add anything missing. We never fill in gaps for you.</Text>{needsReview > 0 && <Text className="text-sm font-semibold text-c2">{needsReview} line(s) have a suggestion to review.</Text>}</Card>
      <SectionTitle>{tokens.length} ingredients</SectionTitle>
      {tokens.map((t) => (
        <Card key={t.position} className="gap-2">
          <View className="flex-row items-center gap-2">
            <Text className="w-6 text-sm text-muted">{t.position}</Text>
            <TextInput accessibilityLabel={`Ingredient ${t.position}`} value={t.rawToken} onChangeText={(v) => { const id = matchLocal(v); update(t.position, { rawToken: v, ingredientId: id, matchMethod: id ? "manual" : "none", matchScore: id ? 1 : 0, suggestions: undefined }); }} className="min-h-[44px] flex-1 rounded-xl border border-line px-3 text-base text-ink" />
            <Pressable accessibilityRole="button" accessibilityLabel={`Remove ${t.rawToken}`} onPress={() => remove(t.position)} className="h-11 w-11 items-center justify-center"><Ionicons name="trash-outline" size={22} color="#55645A" /></Pressable>
          </View>
          <View className="flex-row flex-wrap items-center gap-2 pl-8">
            <ClassBadge cls={classOf(t.ingredientId)} compact />
            {t.ocrConfidence < 0.8 && <Text className="text-xs text-c2">Low read confidence</Text>}
          </View>
          {t.suggestions?.filter(() => !t.ingredientId).map((s) => (
            <Pressable key={s.ingredientId} accessibilityRole="button" onPress={() => update(t.position, { ingredientId: s.ingredientId, rawToken: s.name, matchMethod: "manual", matchScore: s.score, suggestions: undefined })} className="ml-8 min-h-[44px] justify-center rounded-xl bg-forest-soft px-3">
              <Text className="text-sm text-forest-dark">Did you mean <Text className="font-bold">{s.name}</Text>? ({Math.round(s.score * 100)}% match) — tap to accept</Text>
            </Pressable>
          ))}
        </Card>
      ))}
      <View className="flex-row gap-2"><TextInput accessibilityLabel="Add an ingredient" value={adding} onChangeText={setAdding} placeholder="Add a missing ingredient" placeholderTextColor="#66736A" className="min-h-[48px] flex-1 rounded-xl border border-line bg-card px-3 text-base text-ink" onSubmitEditing={add} /><Button label="Add" variant="secondary" onPress={add} /></View>
    </Screen>
  );
}
