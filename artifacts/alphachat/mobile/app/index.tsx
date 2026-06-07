import { Redirect } from 'expo-router';
import { useAuthStore } from '../lib/store';

export default function Root() {
  const { userId } = useAuthStore();
  if (userId) return <Redirect href="/(tabs)" />;
  return <Redirect href="/(auth)/onboarding" />;
}
