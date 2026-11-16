import { Ionicons } from "@expo/vector-icons";
import { Tabs } from "expo-router";
import type { ColorValue } from "react-native";

function TabIcon({ name, color, size }: { name: React.ComponentProps<typeof Ionicons>["name"]; color: ColorValue; size: number }) {
  return <Ionicons name={name} color={color} size={size} />;
}
const icon = (name: React.ComponentProps<typeof Ionicons>["name"]) => {
  const render = ({ color, size }: { color: ColorValue; size: number }) => <TabIcon name={name} color={color} size={size} />;
  return render;
};

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false, tabBarActiveTintColor: "#1F5D3A", tabBarInactiveTintColor: "#55645A", tabBarStyle: { backgroundColor: "#FFFFFF", borderTopColor: "#E3DCCF", height: 74, paddingTop: 8, paddingBottom: 12 }, tabBarLabelStyle: { fontSize: 12, fontWeight: "600" }, tabBarShowLabel: true }}>
      <Tabs.Screen name="home" options={{ title: "Home", tabBarIcon: icon("home-outline") }} />
      <Tabs.Screen name="history" options={{ title: "History", tabBarIcon: icon("time-outline") }} />
      <Tabs.Screen name="saved" options={{ title: "Saved", tabBarIcon: icon("bookmark-outline") }} />
      <Tabs.Screen name="profile" options={{ title: "Profile", tabBarIcon: icon("person-outline") }} />
    </Tabs>
  );
}
