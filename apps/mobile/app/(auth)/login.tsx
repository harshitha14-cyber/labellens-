import { Link, router } from "expo-router";
import { useState } from "react";
import { Text, TextInput, View } from "react-native";
import { Button, Screen } from "@/components/ui";
import { useSession } from "@/store";

/** Screen 3a: Login (mock auth; real Supabase Auth arrives in Milestone 2) */
export default function Login() {
  const [email, setEmail] = useState("");
  const signIn = useSession((s) => s.signIn);
  const valid = /^\S+@\S+\.\S+$/.test(email);
  return (
    <Screen title="Welcome back">
      <Text className="text-base text-muted">Sign in to see your saved scans.</Text>
      <View className="gap-1"><Text className="text-sm font-medium text-ink">Email</Text>
        <TextInput accessibilityLabel="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" placeholder="you@example.com" placeholderTextColor="#66736A" className="min-h-[52px] rounded-2xl border border-line bg-card px-4 text-base text-ink" /></View>
      <Button label="Send me a sign-in link" disabled={!valid} onPress={() => { signIn(email.split("@")[0] ?? "You"); router.replace("/(tabs)/home"); }} />
      <Button variant="ghost" label="Continue as guest" onPress={() => { router.replace("/(tabs)/home"); }} />
      <Link href="/(auth)/register" className="pt-2 text-center text-base text-forest-dark">New here? Create an account</Link>
    </Screen>
  );
}
