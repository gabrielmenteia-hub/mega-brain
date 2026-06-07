import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, KeyboardAvoidingView, Platform, TouchableOpacity, Alert } from 'react-native';
import { router } from 'expo-router';
import { Colors, Spacing, Typography, Radius } from '../../constants/theme';
import { Button } from '../../components/ui/Button';
import { supabase } from '../../lib/supabase';
import { useAuthStore } from '../../lib/store';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const setAuth = useAuthStore((s) => s.setAuth);

  const handleSubmit = async () => {
    if (!email || !password) return;
    setLoading(true);
    try {
      let result;
      if (isSignUp) {
        result = await supabase.auth.signUp({ email, password });
      } else {
        result = await supabase.auth.signInWithPassword({ email, password });
      }
      if (result.error) throw result.error;
      const session = result.data.session;
      if (session) {
        setAuth(session.user.id, session.access_token, session.user.email ?? email);
        router.replace('/(tabs)');
      }
    } catch (e: any) {
      Alert.alert('Erro', e.message ?? 'Falha na autenticação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.header}>
        <Text style={styles.logo}>⚡ AlphaChat</Text>
        <Text style={styles.subtitle}>{isSignUp ? 'Criar conta' : 'Bem-vindo de volta'}</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.field}>
          <Text style={styles.fieldLabel}>Email</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder="seu@email.com"
            placeholderTextColor={Colors.text.muted}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
          />
        </View>
        <View style={styles.field}>
          <Text style={styles.fieldLabel}>Senha</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            placeholderTextColor={Colors.text.muted}
            secureTextEntry
            autoComplete="password"
          />
        </View>
        <Button label={isSignUp ? 'Criar Conta' : 'Entrar'} onPress={handleSubmit} loading={loading} size="lg" style={styles.btn} />
      </View>

      <TouchableOpacity onPress={() => setIsSignUp(!isSignUp)} style={styles.toggle}>
        <Text style={styles.toggleText}>
          {isSignUp ? 'Já tem conta? ' : 'Não tem conta? '}
          <Text style={styles.toggleAccent}>{isSignUp ? 'Entrar' : 'Criar grátis'}</Text>
        </Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bg.primary,
    justifyContent: 'center',
    padding: Spacing.xl,
    gap: Spacing.xxl,
  },
  header: { gap: Spacing.sm },
  logo: { ...Typography.h1, color: Colors.accent.gold },
  subtitle: { ...Typography.body, color: Colors.text.secondary },
  form: { gap: Spacing.md },
  field: { gap: Spacing.xs },
  fieldLabel: { ...Typography.label, color: Colors.text.secondary },
  input: {
    backgroundColor: Colors.bg.card,
    borderWidth: 1,
    borderColor: Colors.border.default,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm + 4,
    ...Typography.body,
    color: Colors.text.primary,
  },
  btn: { marginTop: Spacing.sm },
  toggle: { alignItems: 'center' },
  toggleText: { ...Typography.body, color: Colors.text.muted },
  toggleAccent: { color: Colors.accent.gold, fontWeight: '600' },
});
