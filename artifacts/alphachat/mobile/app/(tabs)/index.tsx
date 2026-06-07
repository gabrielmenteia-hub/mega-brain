import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Spacing, Typography, Radius } from '../../constants/theme';
import { Card } from '../../components/ui/Card';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { Button } from '../../components/ui/Button';
import { useAuthStore, useProgressStore } from '../../lib/store';
import { getUserProgress } from '../../lib/api';
import { SCENARIOS, CHARACTERS } from '../../constants/scenarios';

const QUICK_STARTS = [
  { scenario: 'testes_e_objecoes' as const, character: 'high_value' as const, mode: 'guiado' as const, label: 'Isabela — Testes' },
  { scenario: 'primeiro_encontro' as const, character: 'intellectual' as const, mode: 'desafio' as const, label: 'Marina — Encontro' },
  { scenario: 'match_no_app' as const, character: 'casual_fun' as const, mode: 'livre' as const, label: 'Carla — Match' },
];

export default function Dashboard() {
  const { userId, email } = useAuthStore();
  const { level, xp, xpNextLevel, totalSessions, bestScore, streak, setProgress } = useProgressStore();
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    if (!userId) return;
    try {
      const data = await getUserProgress();
      setProgress({
        level: data.level,
        xp: data.xp,
        xpNextLevel: data.xpNextLevel,
        totalSessions: data.totalSessions,
        bestScore: data.bestScore,
        streak: data.streak,
      });
    } catch {}
  };

  useEffect(() => { load(); }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.accent.gold} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Olá, {email?.split('@')[0] ?? 'Senhor'}</Text>
          <Text style={styles.headerSub}>Nível {level} · {streak > 0 ? `🔥 ${streak} dias seguidos` : 'Comece sua streak'}</Text>
        </View>
        <View style={styles.xpBadge}>
          <Text style={styles.xpText}>{xp} XP</Text>
        </View>
      </View>

      {/* Level progress */}
      <Card style={styles.levelCard}>
        <View style={styles.levelRow}>
          <Text style={styles.levelLabel}>NÍVEL {level}</Text>
          <Text style={styles.levelSub}>{xp}/{xpNextLevel} XP</Text>
        </View>
        <ProgressBar value={xp} max={xpNextLevel} color={Colors.accent.gold} height={8} />
        <Text style={styles.levelHint}>+{xpNextLevel - xp} XP para Nível {level + 1}</Text>
      </Card>

      {/* Stats Row */}
      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{totalSessions}</Text>
          <Text style={styles.statLabel}>Sessões</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{bestScore > 0 ? bestScore.toFixed(1) : '—'}</Text>
          <Text style={styles.statLabel}>Melhor Score</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{streak}</Text>
          <Text style={styles.statLabel}>Streak</Text>
        </Card>
      </View>

      {/* New Session CTA */}
      <LinearGradient
        colors={[Colors.accent.gold + '22', Colors.accent.gold + '08']}
        style={styles.ctaCard}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <Text style={styles.ctaTitle}>Nova Simulação</Text>
        <Text style={styles.ctaBody}>Escolha cenário, personagem e modo. O coach analisa cada mensagem.</Text>
        <Button label="Iniciar Sessão" onPress={() => router.push('/session/setup')} size="md" />
      </LinearGradient>

      {/* Quick Start */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>ACESSO RÁPIDO</Text>
        <View style={styles.quickList}>
          {QUICK_STARTS.map((qs, i) => {
            const char = CHARACTERS[qs.character];
            const scen = SCENARIOS[qs.scenario];
            return (
              <TouchableOpacity
                key={i}
                style={styles.quickItem}
                activeOpacity={0.75}
                onPress={() => router.push({ pathname: '/session/setup', params: qs })}
              >
                <Text style={styles.quickEmoji}>{scen.icon}</Text>
                <View style={styles.quickText}>
                  <Text style={styles.quickLabel}>{qs.label}</Text>
                  <Text style={styles.quickSub}>{scen.label} · Modo {qs.mode}</Text>
                </View>
                <Text style={styles.quickArrow}>›</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg.primary },
  content: { padding: Spacing.md, gap: Spacing.md, paddingTop: 60 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  greeting: { ...Typography.h2, color: Colors.text.primary },
  headerSub: { ...Typography.bodySmall, color: Colors.text.secondary, marginTop: 2 },
  xpBadge: {
    backgroundColor: Colors.accent.gold + '22',
    borderRadius: Radius.full,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: Colors.accent.gold + '44',
  },
  xpText: { ...Typography.label, color: Colors.accent.gold },
  levelCard: { gap: Spacing.sm },
  levelRow: { flexDirection: 'row', justifyContent: 'space-between' },
  levelLabel: { ...Typography.label, color: Colors.accent.gold },
  levelSub: { ...Typography.caption, color: Colors.text.muted },
  levelHint: { ...Typography.caption, color: Colors.text.muted },
  statsRow: { flexDirection: 'row', gap: Spacing.sm },
  statCard: { flex: 1, alignItems: 'center', gap: 2 },
  statValue: { ...Typography.h2, color: Colors.text.primary },
  statLabel: { ...Typography.caption, color: Colors.text.muted },
  ctaCard: {
    borderRadius: Radius.lg,
    padding: Spacing.md,
    gap: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.accent.gold + '33',
  },
  ctaTitle: { ...Typography.h3, color: Colors.accent.gold },
  ctaBody: { ...Typography.bodySmall, color: Colors.text.secondary },
  section: { gap: Spacing.sm },
  sectionTitle: { ...Typography.label, color: Colors.text.muted },
  quickList: { gap: Spacing.xs },
  quickItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.bg.card,
    padding: Spacing.md,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border.subtle,
  },
  quickEmoji: { fontSize: 22 },
  quickText: { flex: 1 },
  quickLabel: { ...Typography.body, color: Colors.text.primary, fontWeight: '600' },
  quickSub: { ...Typography.caption, color: Colors.text.muted },
  quickArrow: { fontSize: 20, color: Colors.text.muted },
});
