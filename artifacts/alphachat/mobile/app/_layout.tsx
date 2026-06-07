import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Colors } from '../constants/theme';
import { supabase } from '../lib/supabase';
import { useAuthStore } from '../lib/store';

export default function RootLayout() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  useEffect(() => {
    // Restore session on app start
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setAuth(session.user.id, session.access_token, session.user.email ?? '');
      }
    });

    // Listen for auth state changes (login, logout, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setAuth(session.user.id, session.access_token, session.user.email ?? '');
      } else {
        clearAuth();
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: Colors.bg.primary },
          animation: 'fade_from_bottom',
        }}
      >
        <Stack.Screen name="(auth)" options={{ animation: 'fade' }} />
        <Stack.Screen name="(tabs)" options={{ animation: 'fade' }} />
        <Stack.Screen name="session/setup" />
        <Stack.Screen name="session/[id]" />
        <Stack.Screen name="session/analysis/[id]" />
      </Stack>
    </>
  );
}
