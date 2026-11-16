import { router } from "expo-router";
import { useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { Button, Screen } from "@/components/ui";
import { useSession } from "@/store";

function Check({ v, set, text }: { v: boolean; set: (b: boolean) => void; text: string }) {
  return (
    <Pressable accessibilityRole="checkbox" accessibilityState={{ checked: v }} onPress={() => set(!v)} className="flex-row items-start gap-3">
      <View className={`mt-0.5 h-6 w-6 items-center justify-center rounded-md border ${v ? "border-forest bg-forest" : "border-line bg-card"}`}>{v ? <Text className="text-white">✓</Text> : null}</View>
      <Text className="flex-1 text-sm leading-5 text-ink">{text}</Text>
    </Pressable>
  );
}

/** Screen 3b: Registration */
export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [adult, setAdult] = useState(false);
  const [consent, setConsent] = useState(false);
  const signIn = useSession((s) => s.signIn);
  const ok = name.trim().length > 0 && /^\S+@\S+\.\S+$/.test(email) && adult && consent;
  const input = "min-h-[52px] rounded-2xl border border-line bg-card px-4 text-base text-ink";
  return (
    <Screen title="Create account" back>
      <TextInput accessibilityLabel="Name" value={name} onChangeText={setName} placeholder="Your name" placeholderTextColor="#66736A" className={input} />
      <TextInput accessibilityLabel="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" placeholder="Email" placeholderTextColor="#66736A" className={input} />
      <Check v={adult} set={setAdult} text="I am 18 or older." />
      <Check v={consent} set={setConsent} text="I agree to the privacy notice. My ingredient preferences are stored only to personalise my reports, and I can export or delete my data any time." />
      <Button label="Create account" disabled={!ok} onPress={() => { signIn(name.trim()); router.replace("/(tabs)/home"); }} />
    </Screen>
  );
}
