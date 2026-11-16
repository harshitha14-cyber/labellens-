import { Ionicons } from "@expo/vector-icons";
import { CameraView, useCameraPermissions } from "expo-camera";
import { router } from "expo-router";
import { useRef, useState } from "react";
import { Pressable, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Button, Screen } from "@/components/ui";
import { useDraft } from "@/store";

/** Screen 6: Camera scanner */
export default function CameraScreen() {
  const [perm, requestPerm] = useCameraPermissions();
  const ref = useRef<CameraView>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { imageUris, addImages } = useDraft();

  if (!perm) return <Screen title="Camera" back><Text className="text-muted">Checking camera access…</Text></Screen>;
  if (!perm.granted) {
    return (
      <Screen title="Camera access" back>
        <Text className="text-base leading-6 text-ink">LabelLens needs the camera to photograph the ingredient list. Photos are private to your account.</Text>
        <Button label="Allow camera" icon="camera-outline" onPress={requestPerm} />
        <Button variant="ghost" label="Upload from gallery instead" icon="images-outline" onPress={() => router.push("/scan/gallery")} />
      </Screen>
    );
  }
  const snap = async () => {
    if (busy) return;
    setBusy(true); setError(null);
    try {
      const pic = await ref.current?.takePictureAsync({ quality: 0.8 });
      if (pic?.uri) addImages([pic.uri]);
    } catch { setError("Could not take the photo. Try again."); }
    finally { setBusy(false); }
  };
  return (
    <SafeAreaView className="flex-1 bg-black">
      <View className="flex-row items-center px-3 py-2">
        <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={() => router.back()} className="h-11 w-11 items-center justify-center"><Ionicons name="close" size={28} color="#fff" /></Pressable>
        <Text className="flex-1 text-center text-base font-semibold text-white">Frame the ingredient list</Text><View className="w-11" />
      </View>
      <View className="flex-1 overflow-hidden rounded-3xl mx-3">
        <CameraView ref={ref} style={{ flex: 1 }} facing="back" />
        <View pointerEvents="none" className="absolute inset-6 rounded-2xl border-2 border-white/80" />
      </View>
      <Text className="px-6 pt-3 text-center text-sm text-white">Photograph only the label. Good light and a flat view help. You can add up to 5 photos.</Text>
      {error ? <Text accessibilityLiveRegion="polite" className="px-6 pt-1 text-center text-sm text-[#FFB4B4]">{error}</Text> : null}
      <View className="flex-row items-center justify-around px-6 py-5">
        <Pressable accessibilityRole="button" accessibilityLabel="Choose from gallery" onPress={() => router.push("/scan/gallery")} className="h-14 w-14 items-center justify-center rounded-full bg-white/20"><Ionicons name="images-outline" size={26} color="#fff" /></Pressable>
        <Pressable accessibilityRole="button" accessibilityLabel="Take photo" onPress={snap} className="h-20 w-20 items-center justify-center rounded-full border-4 border-white bg-white/30 active:opacity-70">{busy ? <Text className="text-white">…</Text> : null}</Pressable>
        <Pressable accessibilityRole="button" accessibilityLabel={`Review ${imageUris.length} photos`} disabled={!imageUris.length} onPress={() => router.push("/scan/preview")} className={`h-14 w-14 items-center justify-center rounded-full bg-forest ${imageUris.length ? "" : "opacity-40"}`}><Text className="text-lg font-bold text-white">{imageUris.length}</Text></Pressable>
      </View>
    </SafeAreaView>
  );
}
