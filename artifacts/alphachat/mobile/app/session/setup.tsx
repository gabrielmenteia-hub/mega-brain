import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Colors, Spacing, Typography, Radius, CharacterColors } from '../../constants/theme';
import { Button } from '../../components/ui/Button';
import { CharacterCard } from '../../components/session/CharacterCard';
import { SCENARIOS, CHARACTERS, MODES, type ScenarioType, type CharacterType, type ModeType } from '../../constants/scenarios';
import { createSession } from '../../lib/api';
import { useAuthStore, useSessionStore } from '../../lib/store';

export default function SessionSetup() {
  const params = useLocalSearchParams<{ scenario?: string; character?: string; mode?: string }>();
  const [scenario, setScenario] = useState<ScenarioType>((params.scenario as ScenarioType) ?? 'testes_e_objecoes');
  const [character, setCharacter] = useState<CharacterType>((params.character as CharacterType) ?? 'high_value');
  const [mode, setMode] = useState<ModeType>((params.mode as ModeType) ?? 'guiado');
  const [loading, setLoading] = useState(false);
  const { userId } = useAuthStore();
  const startSession = useSessionStore((s) => s.startSession);

  const handleStart = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const data = await createSession({ scenario, character, mode });
      startSession({
        sessionId: data.session_id,
        scenario,
        character,
        mode,
        characterName: data.character_name,
        openingMessage: data.opening_message,
        interestLevel: data.interest_level,
      });
      router.replace(`/session/${data.session_id}`);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.back}>‹ Voltar</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Nova Sessão</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Scenario */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>CENÁRIO</Text>
          <View style={styles.scenarioGrid}>
            {(Object.entries(SCENARIOS) as [ScenarioType, typeof SCENARIOS[ScenarioType]][]).map(([key, scen]) => (
              <TouchableOpacity
                key={key}
                style={[styles.scenarioCard, scenario === key && styles.scenarioSelected]}
                onPress={() => setScenario(key)}
                activeOpacity={0.8}
              >
                <Text style={styles.scenarioIcon}>{scen.icon}</Text>
                <Text style={[styles.scenarioLabel, scenario === key && { color: Colors.accent.gold }]}>{scen.label}</Text>
                <View style={styles.diffRow}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <View key={i} style={[styles.diffDot, i < scen.difficulty && { backgroundColor: Colors.accent.gold }]} />
                  ))}
                </View>
              </TouchableOpacity>
            ))}
          </View>
          {scenario && (
            <Text style={styles.scenarioDesc}>{SCENARIOS[scenario].description}</Text>
          )}
        </View>

        {/* Character */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>PERSONAGEM</Text>
          <View style={styles.charList}>
            {(Object.keys(CHARACTERS) as CharacterType[]).map((key) => (
              <CharacterCard key={key} type={key} selected={character === key} onPress={() => setCharacter(key)} />
            ))}
          </View>
        </View>

        {/* Mode */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>MODO</Text>
          <View style={styles.modeRow}>
            {(Object.entries(MODES) as [ModeType, typeof MODES[ModeType]][]).map(([key, m]) => (
              <TouchableOpacity
                key={key}
                style={[styles.modeCard, mode === key && styles.modeSelected]}
                onPress={() => setMode(key)}
                activeOpacity={0.8}
              >
                <Text style={styles.modeIcon}>{m.icon}</Text>
                <Text style={[styles.modeLabel, mode === key && { color: Colors.accent.gold }]}>{m.label}</Text>
                <Text style={styles.modeDesc}>{m.description}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>

      <View style={styles.footer}>
        <Button
          label={`Começar com ${character ? CHARACTERS[character].name : '...'}`}
          onPress={handleStart}
          loading={loading}
          size="lg"
          style={styles.startBtn}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg.primary },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingTop: 56,
    paddingBottom: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border.subtle,
  },
  back: { ...Typography.body, color: Colors.accent.gold, width: 60 },
  title: { ...Typography.h3, color: Colors.text.primary },
  content: { padding: Spacing.md, gap: Spacing.xl },
  section: { gap: Spacing.sm },
  sectionTitle: { ...Typography.label, color: Colors.text.muted },
  scenarioGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  scenarioCard: {
    backgroundColor: Colors.bg.card,
    borderRadius: Radius.md,
    borderWidth: 1.5,
    borderColor: Colors.border.subtle,
    padding: Spacing.sm,
    alignItems: 'center',
    gap: 4,
    width: '30%',
  },
  scenarioSelected: { borderColor: Colors.accent.gold, backgroundColor: Colors.accent.gold + '12' },
  scenarioIcon: { fontSize: 22 },
  scenarioLabel: { ...Typography.caption, color: Colors.text.secondary, textAlign: 'center', fontWeight: '600' },
  diffRow: { flexDirection: 'row', gap: 2 },
  diffDot: { width: 5, height: 5, borderRadius: 2.5, backgroundColor: Colors.border.strong },
  scenarioDesc: { ...Typography.bodySmall, color: Colors.text.muted, fontStyle: 'italic' },
  charList: { gap: Spacing.sm },
  modeRow: { flexDirection: 'row', gap: Spacing.sm },
  modeCard: {
    flex: 1,
    backgroundColor: Colors.bg.card,
    borderRadius: Radius.md,
    borderWidth: 1.5,
    borderColor: Colors.border.subtle,
    padding: Spacing.sm,
    alignItems: 'center',
    gap: 4,
  },
  modeSelected: { borderColor: Colors.accent.gold, backgroundColor: Colors.accent.gold + '12' },
  modeIcon: { fontSize: 22 },
  modeLabel: { ...Typography.caption, color: Colors.text.secondary, fontWeight: '700' },
  modeDesc: { ...Typography.caption, color: Colors.text.muted, textAlign: 'center', lineHeight: 14 },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: Spacing.md,
    paddingBottom: 32,
    backgroundColor: Colors.bg.primary,
    borderTopWidth: 1,
    borderTopColor: Colors.border.subtle,
  },
  startBtn: { width: '100%' },
});
