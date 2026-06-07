import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, Dimensions, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Spacing, Typography, Radius } from '../../constants/theme';
import { Button } from '../../components/ui/Button';

const { width } = Dimensions.get('window');

const SLIDES = [
  {
    emoji: '⚡',
    title: 'Simulador de\nConversas Reais',
    body: '6 livros. 89 conceitos. Um coach de IA que analisa cada resposta sua em tempo real.',
    accent: Colors.accent.gold,
  },
  {
    emoji: '🎭',
    title: '4 Personalidades,\nInfinitas Situações',
    body: 'Isabela (High Value), Marina (Intelectual), Carla (Casual), Sofia (Girl Next Door). Cada uma com comportamentos únicos.',
    accent: Colors.accent.blue,
  },
  {
    emoji: '📈',
    title: 'Feedback\nImediato e Preciso',
    body: 'Nível de interesse em tempo real. Análise pós-sessão. Aprenda o que funciona — e o que não funciona.',
    accent: Colors.accent.teal,
  },
  {
    emoji: '🏆',
    title: 'Progrida.\nEvoluia. Domine.',
    body: 'XP, níveis, conquistas. Cada sessão é uma aula. Cada evolução é mensurável.',
    accent: Colors.accent.gold,
  },
];

export default function Onboarding() {
  const [current, setCurrent] = useState(0);

  const next = () => {
    if (current < SLIDES.length - 1) setCurrent(current + 1);
    else router.replace('/(auth)/login');
  };

  const slide = SLIDES[current];

  return (
    <LinearGradient colors={[Colors.bg.primary, Colors.bg.secondary]} style={styles.container}>
      <View style={styles.skipRow}>
        {current < SLIDES.length - 1 ? (
          <TouchableOpacity onPress={() => router.replace('/(auth)/login')}>
            <Text style={styles.skip}>Pular</Text>
          </TouchableOpacity>
        ) : <View />}
      </View>

      <View style={styles.content}>
        <Text style={styles.emoji}>{slide.emoji}</Text>
        <Text style={[styles.title, { color: slide.accent }]}>{slide.title}</Text>
        <Text style={styles.body}>{slide.body}</Text>
      </View>

      <View style={styles.footer}>
        <View style={styles.dots}>
          {SLIDES.map((_, i) => (
            <View
              key={i}
              style={[styles.dot, i === current && { backgroundColor: slide.accent, width: 20 }]}
            />
          ))}
        </View>
        <Button
          label={current === SLIDES.length - 1 ? 'Começar' : 'Próximo'}
          onPress={next}
          size="lg"
          style={styles.btn}
        />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 60 },
  skipRow: { paddingHorizontal: Spacing.xl, alignItems: 'flex-end' },
  skip: { ...Typography.body, color: Colors.text.muted },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
    gap: Spacing.lg,
  },
  emoji: { fontSize: 72 },
  title: { ...Typography.h1, textAlign: 'center', lineHeight: 38 },
  body: { ...Typography.body, color: Colors.text.secondary, textAlign: 'center', lineHeight: 24 },
  footer: { padding: Spacing.xl, gap: Spacing.lg },
  dots: { flexDirection: 'row', justifyContent: 'center', gap: 6 },
  dot: { width: 6, height: 6, borderRadius: 3, backgroundColor: Colors.border.strong },
  btn: { width: '100%' },
});
