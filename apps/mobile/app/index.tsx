import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useEffect } from "react";
import { Text, View } from "react-native";
import Animated, { FadeIn, FadeInDown } from "react-native-reanimated";
import { useSession } from "@/store";

/** Screen 1: Splash. Routes onward after a short beat. */
export default function Splash() {
  const { onboarded, signedIn } = useSession();
  useEffect(() => {
    const t = setTimeout(() => router.replace(!onboarded ? "/onboarding" : signedIn ? "/(tabs)/home" : "/(auth)/login"), 1400);
    return () => clearTimeout(t);
  }, [onboarded, signedIn]);
  return (
    <View className="flex-1 items-center justify-center bg-canvas">
      <Animated.View entering={FadeIn.duration(500)} className="h-24 w-24 items-center justify-center rounded-3xl bg-forest">
        <Ionicons name="scan-outline" size={48} color="#fff" />
      </Animated.View>
      <Animated.Text entering={FadeInDown.delay(300)} className="mt-6 text-3xl font-bold text-ink">LabelLens India</Animated.Text>
      <Animated.Text entering={FadeInDown.delay(500)} className="mt-2 text-base text-muted">Know what is in your products</Animated.Text>
      <Text className="absolute bottom-10 text-xs text-muted">Demo build · Milestone 1</Text>
    </View>
  );
}
