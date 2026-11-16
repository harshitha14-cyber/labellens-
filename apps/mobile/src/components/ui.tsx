import { Ionicons } from "@expo/vector-icons";
import { type ReactNode } from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { CLASS_META } from "@/theme/classes";
import type { ClassId } from "@/types";
import { DEMO_NOTICE } from "@/mocks/data";

type IconName = React.ComponentProps<typeof Ionicons>["name"];

export function Screen({ children, title, back, scroll = true, footer, demo = true }: { children: ReactNode; title?: string; back?: boolean; scroll?: boolean; footer?: ReactNode; demo?: boolean }) {
  const body = <View className="px-5 pb-8 gap-4">{children}</View>;
  return (
    <SafeAreaView className="flex-1 bg-canvas" edges={["top", "bottom"]}>
      {(title || back) && (
        <View className="flex-row items-center px-3 py-2">
          {back ? (
            <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={() => router.back()} className="h-11 w-11 items-center justify-center">
              <Ionicons name="chevron-back" size={26} color="#1B2A21" />
            </Pressable>
          ) : <View className="w-2" />}
          {title ? <Text accessibilityRole="header" className="flex-1 text-xl font-semibold text-ink">{title}</Text> : null}
        </View>
      )}
      {demo ? <DemoBanner /> : null}
      {scroll ? <ScrollView contentContainerStyle={{ paddingTop: 8 }} keyboardShouldPersistTaps="handled">{body}</ScrollView> : <View className="flex-1 px-5 pb-4 gap-4 pt-2">{children}</View>}
      {footer ? <View className="px-5 pb-3 pt-2">{footer}</View> : null}
    </SafeAreaView>
  );
}

export function DemoBanner() {
  return (
    <View className="mx-5 mb-1 rounded-lg bg-surface px-3 py-1.5" accessibilityRole="text">
      <Text className="text-xs text-muted">{DEMO_NOTICE}</Text>
    </View>
  );
}

export function Card({ children, onPress, className = "" }: { children: ReactNode; onPress?: () => void; className?: string }) {
  const bg = /(^|\s)bg-/.test(className) ? "" : "bg-card";
  const cls = `rounded-xl2 border border-line ${bg} p-4 ${className}`;
  return onPress ? (
    <Pressable accessibilityRole="button" onPress={onPress} className={`${cls} active:opacity-80`}>{children}</Pressable>
  ) : (
    <View className={cls}>{children}</View>
  );
}

export function Button({ label, onPress, variant = "primary", icon, disabled, loading }: { label: string; onPress: () => void; variant?: "primary" | "secondary" | "ghost"; icon?: IconName; disabled?: boolean; loading?: boolean }) {
  const styles = { primary: "bg-forest", secondary: "bg-forest-soft", ghost: "bg-transparent border border-line" }[variant];
  const text = variant === "primary" ? "text-white" : "text-forest-dark";
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} accessibilityState={{ disabled: !!disabled }} disabled={disabled || loading} onPress={onPress}
      className={`min-h-[52px] flex-row items-center justify-center gap-2 rounded-2xl px-5 ${styles} ${disabled ? "opacity-50" : "active:opacity-85"}`}>
      {loading ? <ActivityIndicator color={variant === "primary" ? "#fff" : "#1F5D3A"} /> : icon ? <Ionicons name={icon} size={20} color={variant === "primary" ? "#fff" : "#164A2D"} /> : null}
      <Text className={`text-base font-semibold ${text}`}>{label}</Text>
    </Pressable>
  );
}

export function Chip({ label, selected, onPress, tone = "default" }: { label: string; selected?: boolean; onPress?: () => void; tone?: "default" | "avoid" }) {
  const sel = selected ? (tone === "avoid" ? "bg-c3 border-c3" : "bg-forest border-forest") : "bg-card border-line";
  return (
    <Pressable accessibilityRole="button" accessibilityState={{ selected: !!selected }} onPress={onPress} className={`min-h-[40px] justify-center rounded-full border px-4 ${sel}`}>
      <Text className={`text-sm font-medium ${selected ? "text-white" : "text-ink"}`}>{selected ? "✓ " : ""}{label}</Text>
    </Pressable>
  );
}

export function ClassBadge({ cls, compact }: { cls: ClassId; compact?: boolean }) {
  const m = CLASS_META[cls];
  return (
    <View className={`flex-row items-center gap-1.5 self-start rounded-full px-2.5 py-1 ${m.bg}`} accessible accessibilityLabel={`Classification: ${m.label}`}>
      <Ionicons name={m.icon as IconName} size={14} color={{ 1: "#1F5D3A", 2: "#8A5A00", 3: "#9B2C2C", 4: "#4A5560", 5: "#5B3F8C", 6: "#3D4B57" }[cls]} />
      <Text className={`text-xs font-semibold ${m.text}`}>{compact ? m.short : m.label}</Text>
    </View>
  );
}

export function SectionTitle({ children, hint }: { children: ReactNode; hint?: string }) {
  return (
    <View className="gap-0.5 pt-2">
      <Text accessibilityRole="header" className="text-lg font-semibold text-ink">{children}</Text>
      {hint ? <Text className="text-sm text-muted">{hint}</Text> : null}
    </View>
  );
}

export function Row({ icon, title, subtitle, onPress, right }: { icon?: IconName; title: string; subtitle?: string; onPress?: () => void; right?: ReactNode }) {
  return (
    <Card onPress={onPress} className="flex-row items-center gap-3">
      {icon ? <View className="h-10 w-10 items-center justify-center rounded-full bg-forest-soft"><Ionicons name={icon} size={20} color="#1F5D3A" /></View> : null}
      <View className="flex-1"><Text className="text-base font-semibold text-ink">{title}</Text>{subtitle ? <Text className="text-sm text-muted">{subtitle}</Text> : null}</View>
      {right ?? (onPress ? <Ionicons name="chevron-forward" size={20} color="#55645A" /> : null)}
    </Card>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return <View className="items-center py-10 gap-3" accessibilityLiveRegion="polite"><ActivityIndicator color="#1F5D3A" /><Text className="text-muted">{label}</Text></View>;
}

export function Disclaimer() {
  return <Text className="text-xs leading-5 text-muted">Informational only, based on the label you photographed. Not medical advice and not a diagnosis. Ingredient order does not show concentration. If a product irritates your skin, stop using it and consult a doctor.</Text>;
}
