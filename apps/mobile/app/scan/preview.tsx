import { Image } from "expo-image";
import * as ImageManipulator from "expo-image-manipulator";
import { router } from "expo-router";
import { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { Button, Card, Screen } from "@/components/ui";
import { useDraft } from "@/store";

/** Screen 8: Image preview and editing (rotate; interactive crop planned, see limitations) */
export default function Preview() {
  const { imageUris, removeImage, addImages } = useDraft();
  const [busy, setBusy] = useState<string | null>(null);
  const rotate = async (uri: string) => {
    setBusy(uri);
    try {
      const out = await ImageManipulator.manipulateAsync(uri, [{ rotate: 90 }], { compress: 0.85, format: ImageManipulator.SaveFormat.JPEG });
      removeImage(uri); addImages([out.uri]);
    } finally { setBusy(null); }
  };
  return (
    <Screen title="Check your photos" back footer={<Button label={`Read ingredients (${imageUris.length})`} icon="scan-outline" disabled={!imageUris.length} onPress={() => router.push("/scan/processing")} />}>
      <Text className="text-sm text-muted">Make sure the whole ingredient list is sharp and readable. Rotate if needed.</Text>
      {imageUris.length === 0 && <Card><Text className="text-muted">No photos yet.</Text><Button variant="secondary" label="Add a photo" onPress={() => router.replace("/scan/camera")} /></Card>}
      {imageUris.map((uri) => (
        <Card key={uri} className="gap-3 p-2">
          <Image source={{ uri }} style={{ width: "100%", height: 240, borderRadius: 14 }} contentFit="contain" accessibilityLabel="Label photo preview" />
          <View className="flex-row gap-2 px-2 pb-2">
            <Pressable accessibilityRole="button" onPress={() => rotate(uri)} disabled={busy === uri} className="min-h-[44px] flex-1 items-center justify-center rounded-xl bg-forest-soft"><Text className="font-semibold text-forest-dark">{busy === uri ? "Rotating…" : "Rotate 90°"}</Text></Pressable>
            <Pressable accessibilityRole="button" onPress={() => removeImage(uri)} className="min-h-[44px] flex-1 items-center justify-center rounded-xl border border-line"><Text className="font-semibold text-ink">Remove</Text></Pressable>
          </View>
        </Card>
      ))}
    </Screen>
  );
}
