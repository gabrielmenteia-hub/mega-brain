import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Spacing, Typography, Radius, CharacterColors } from '../../../constants/theme';
import { Card } from '../../../components/ui/Card';
import { ProgressBar } from '../../../components/ui/ProgressBar';
import { Button } from '../../../components/ui/Button';
import { getSessionAnalysis } from '../../../lib/api';
import { useSessionStore } from '../../../lib/store';
import { SCENARIOS, CHARACTERS } from '../../../constants/scenarios';

interface Analysis {
  score_overall: number;
  duration_minutes: number;
  total_turns: number;
  final_interest: number;
  xp_gained: number;
  level_up: boolean;
  scores: {
    confianca: number;
    frame: number;
    calibracao: number;
    polaridade: number;
    assertividade: number;
  };
  milestones: string[];
  concepts_encountered: string[];
  coach_summary: string;
  top_moment: string;
  improvement_tip: string;
}

export default function SessionAnalysis() {
  const { id, level_up: levelUpParam } = useLocalSearchParams<{ id: string; level_up?: string }>();
  const { scenario, character, characterName, clearSession } = useSessionStore();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const didLevelUp = levelUpParam === '1';

  const charColor = character ? CharacterColors[character] : Colors.accent.gold;

  useEffect(() => {
    if (!id) return;
    getSessionAnalysis(id)
      .then(setAnalysis)
      .catch(() => {
        // Fallback mock while API is not connected
        setAnalysis({
          score_overall: 7.8,
          duration_minutes: 12,
          total_turns: 8,
          final_interest: 72,
          xp_gained: 85,
          level_up: false,
          scores: { confianca: 8.2, frame: 7.5, calibracao: 7.8, polaridade: 7.0, assertividade: 7.6 },
          milestones: ['Primeira reação positiva', 'Manteve frame sob pressão'],
          concepts_encountered: ['Presença', 'Calibração emocional', 'Autenticidade'],
          coach_summary: 'Boa sessão. Você manteve a presença e não cedeu nos momentos de teste.',
          top_moment: 'Quando parou de tentar impressionar e foi genuíno.',
          improvement_tip: 'Trabalhe a escalação — você recua rápido demais quando ela hesita.',
        });
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleNewSession = () => {
    clearSession();
    router.replace('/session/setup');
  };

  const handleHome = () => {
    clearSession();
    router.replace('/(tabs)');
  };

  if (loading) {
    return (
      <View style={styles.loading}>
        <Text style={styles.loadingText}>Analisando sessão…</Text>
      </View>
    );
  }

  if (!analysis) return null;

  const scoreColor = analysis.score_overall >= 8 ? Colors.interest.high : analysis.score_overall >= 6 ? Colors.interest.mid : Colors.interest.low;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <LinearGradient colors={[Colors.bg.secondary, Colors.bg.primary]} style={styles.header}>
        {didLevelUp && (
          <View style={styles.levelUpBadge}>
            <Text style={styles.levelUpText}>⬆️ LEVEL UP!</Text>
          </View>
        )}
        <Text style={styles.title}>Análise da Sessão</Text>
        <Text style={[styles.charLine, { color: charColor }]}>
          {characterName} · {scenario ? SCENARIOS[scenario].label : ''} · {analysis.duration_minutes} min
        </Text>

        {/* Score */}
        <View style={styles.scoreContainer}>
          <Text style={[styles.scoreValue, { color: scoreColor }]}>{analysis.score_overall.toFixed(1)}</Text>
          <Text style={styles.scoreMax}>/10</Text>
        </View>
        <Text style={[styles.xpEarned, { color: Colors.accent.gold }]}>+{analysis.xp_gained} XP</Text>
      </LinearGradient>

      {/* Scores breakdown */}
      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>SCORES</Text>
        <View style={styles.scoresGrid}>
          {Object.entries(analysis.scores).map(([key, val]) => (
            <View key={key} style={styles.scoreItem}>
              <View style={styles.scoreItemHeader}>
                <Text style={styles.scoreItemLabel}>{formatScoreKey(key)}</Text>
                <Text style={[styles.scoreItemValue, { color: val >= 8 ? Colors.interest.high : val >= 6 ? Colors.interest.mid : Colors.interest.low }]}>
                  {val.toFixed(1)}
                </Text>
              </View>
              <ProgressBar value={val} max={10} color={charColor} height={4} />
            </View>
          ))}
        </View>
      </Card>

      {/* Coach Summary */}
      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>💬 COACH</Text>
        <Text style={styles.coachText}>{analysis.coach_summary}</Text>
        {analysis.top_moment && (
          <View style={[styles.moment, { borderLeftColor: Colors.interest.high }]}>
            <Text style={styles.momentLabel}>MELHOR MOMENTO</Text>
            <Text style={styles.momentText}>{analysis.top_moment}</Text>
          </View>
        )}
        {analysis.improvement_tip && (
          <View style={[styles.moment, { borderLeftColor: Colors.accent.gold }]}>
            <Text style={styles.momentLabel}>PRÓXIMO FOCO</Text>
            <Text style={styles.momentText}>{analysis.improvement_tip}</Text>
          </View>
        )}
      </Card>

      {/* Interest & Stats */}
      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>SESSÃO</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statVal}>{analysis.final_interest}</Text>
            <Text style={styles.statLbl}>Interesse Final</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statVal}>{analysis.total_turns}</Text>
            <Text style={styles.statLbl}>Turnos</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statVal}>{analysis.duration_minutes}m</Text>
            <Text style={styles.statLbl}>Duração</Text>
          </View>
        </View>
      </Card>

      {/* Milestones */}
      {analysis.milestones.length > 0 && (
        <Card style={styles.section}>
          <Text style={styles.sectionTitle}>🏅 CONQUISTAS</Text>
          {analysis.milestones.map((m, i) => (
            <Text key={i} style={styles.milestone}>✓ {m}</Text>
          ))}
        </Card>
      )}

      {/* Concepts */}
      {analysis.concepts_encountered.length > 0 && (
        <Card style={styles.section}>
          <Text style={styles.sectionTitle}>📚 CONCEITOS APLICADOS</Text>
          <View style={styles.tagRow}>
            {analysis.concepts_encountered.map((c, i) => (
              <View key={i} style={[styles.tag, { borderColor: charColor + '55' }]}>
                <Text style={[styles.tagText, { color: charColor }]}>{c}</Text>
              </View>
            ))}
          </View>
        </Card>
      )}

      {/* Actions */}
      <View style={styles.actions}>
        <Button label="Nova Sessão" onPress={handleNewSession} size="lg" style={styles.actionBtn} />
        <Button label="Início" onPress={handleHome} variant="secondary" size="lg" style={styles.actionBtn} />
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function formatScoreKey(key: string) {
  const map: Record<string, string> = {
    confianca: 'Confiança',
    frame: 'Frame',
    calibracao: 'Calibração',
    polaridade: 'Polaridade',
    assertividade: 'Assertividade',
  };
  return map[key] ?? key;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg.primary },
  content: { gap: Spacing.md, paddingBottom: Spacing.xl },
  loading: { flex: 1, backgroundColor: Colors.bg.primary, alignItems: 'center', justifyContent: 'center' },
  loadingText: { ...Typography.body, color: Colors.text.muted },
  header: { padding: Spacing.xl, paddingTop: 70, alignItems: 'center', gap: Spacing.sm },
  levelUpBadge: { backgroundColor: Colors.accent.gold + '22', borderRadius: Radius.full, paddingHorizontal: 16, paddingVertical: 4, borderWidth: 1, borderColor: Colors.accent.gold },
  levelUpText: { ...Typography.label, color: Colors.accent.gold },
  title: { ...Typography.h2, color: Colors.text.primary },
  charLine: { ...Typography.bodySmall },
  scoreContainer: { flexDirection: 'row', alignItems: 'baseline', gap: 4 },
  scoreValue: { fontSize: 64, fontWeight: '700', lineHeight: 72 },
  scoreMax: { ...Typography.h2, color: Colors.text.muted },
  xpEarned: { ...Typography.h3, fontWeight: '700' },
  section: { marginHorizontal: Spacing.md, gap: Spacing.sm },
  sectionTitle: { ...Typography.label, color: Colors.text.muted },
  scoresGrid: { gap: Spacing.sm },
  scoreItem: { gap: 4 },
  scoreItemHeader: { flexDirection: 'row', justifyContent: 'space-between' },
  scoreItemLabel: { ...Typography.bodySmall, color: Colors.text.secondary },
  scoreItemValue: { ...Typography.bodySmall, fontWeight: '700' },
  coachText: { ...Typography.body, color: Colors.text.secondary, lineHeight: 22 },
  moment: { borderLeftWidth: 3, paddingLeft: Spacing.sm, gap: 2, marginTop: Spacing.sm },
  momentLabel: { ...Typography.label, color: Colors.text.muted, fontSize: 10 },
  momentText: { ...Typography.bodySmall, color: Colors.text.primary },
  statsGrid: { flexDirection: 'row', justifyContent: 'space-around' },
  statItem: { alignItems: 'center', gap: 2 },
  statVal: { ...Typography.h2, color: Colors.text.primary },
  statLbl: { ...Typography.caption, color: Colors.text.muted },
  milestone: { ...Typography.body, color: Colors.text.secondary },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs },
  tag: { borderRadius: Radius.full, borderWidth: 1, paddingHorizontal: 10, paddingVertical: 4 },
  tagText: { ...Typography.caption, fontWeight: '600' },
  actions: { flexDirection: 'row', gap: Spacing.sm, paddingHorizontal: Spacing.md, marginTop: Spacing.sm },
  actionBtn: { flex: 1 },
});
