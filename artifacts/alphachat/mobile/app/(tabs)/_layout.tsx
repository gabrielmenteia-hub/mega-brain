import { Tabs } from 'expo-router';
import { Colors, Typography } from '../../constants/theme';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.bg.secondary,
          borderTopColor: Colors.border.subtle,
          borderTopWidth: 1,
          paddingBottom: 6,
          height: 60,
        },
        tabBarActiveTintColor: Colors.accent.gold,
        tabBarInactiveTintColor: Colors.text.muted,
        tabBarLabelStyle: { ...Typography.caption, marginBottom: 2 },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: 'Início', tabBarIcon: ({ color }) => <TabIcon emoji="⚡" color={color} /> }}
      />
      <Tabs.Screen
        name="library"
        options={{ title: 'Biblioteca', tabBarIcon: ({ color }) => <TabIcon emoji="📚" color={color} /> }}
      />
      <Tabs.Screen
        name="profile"
        options={{ title: 'Perfil', tabBarIcon: ({ color }) => <TabIcon emoji="👤" color={color} /> }}
      />
    </Tabs>
  );
}

function TabIcon({ emoji, color }: { emoji: string; color: string }) {
  const { Text } = require('react-native');
  return <Text style={{ fontSize: 20, opacity: color === Colors.accent.gold ? 1 : 0.5 }}>{emoji}</Text>;
}
