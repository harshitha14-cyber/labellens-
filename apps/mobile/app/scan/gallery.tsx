import * as ImagePicker from "expo-image-picker";
import { router } from "expo-router";
import { useState } from "react";
import { Text } from "react-native";
import { Button, Screen } from "@/components/ui";
import { useDraft } from "@/store";

/** Screen 7: Gallery upload */
export default function Gallery() {
  const addImages = useDraft((s) => s.addImages);
  const [error, setError] = useState<string | null>(null);
  const pick = async () => {
    setError(null);
    const res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["images"], allowsMultipleSelection: true, selectionLimit: 5, quality: 0.9 });
    if (res.canceled) return;
    if (res.assets.length === 0) { setError("No images were selected."); return; }
    addImages(res.assets.map((a) => a.uri));
    router.replace("/scan/preview");
  };
  return (
    <Screen title="Upload from gallery" back>
      <Text className="text-base leading-6 text-ink">Choose up to 5 clear photos of the ingredient list. Avoid photos with faces or personal items in the background.</Text>
      <Button label="Choose photos" icon="images-outline" onPress={pick} />
      {error ? <Text className="text-c3">{error}</Text> : null}
    </Screen>
  );
}
