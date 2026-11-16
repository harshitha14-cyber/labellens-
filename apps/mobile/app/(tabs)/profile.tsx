import { router } from "expo-router";
import { Text, View } from "react-native";
import { Button, Row, Screen } from "@/components/ui";
import { useSession } from "@/store";

/** Screen 18: Profile */
export default function Profile() {
  const { name, signedIn, signOut } = useSession();
  return (
    <Screen title="Profile">
      <View className="items-center gap-2 py-4">
        <View className="h-20 w-20 items-center justify-center rounded-full bg-forest"><Text className="text-3xl font-bold text-white">{name.charAt(0).toUpperCase()}</Text></View>
        <Text className="text-xl font-semibold text-ink">{name}</Text><Text className="text-sm text-muted">{signedIn ? "Signed in (demo)" : "Guest — scans are not synced"}</Text>
      </View>
      <Row icon="options-outline" title="Ingredient preferences" subtitle="Avoid and prefer lists" onPress={() => router.push("/preferences")} />
      <Row icon="settings-outline" title="Settings" onPress={() => router.push("/settings")} />
      <Button variant="ghost" label={signedIn ? "Sign out" : "Sign in"} onPress={() => { signOut(); router.replace("/(auth)/login"); }} />
    </Screen>
  );
}
