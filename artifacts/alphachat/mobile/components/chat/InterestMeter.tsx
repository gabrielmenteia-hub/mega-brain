import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Typography, Spacing } from '../../constants/theme';

interface Props {
  level: number;
  delta?: number;
}

function getColor(level: number) {
  if (level >= 70) return Colors.interest.high;
  if (level >= 40) return Colors.interest.mid;
  return Colors.interest.low;
}

function getLabel(level: number) {
  if (level >= 90) return 'Eletrizante';
  if (level >= 75) return 'Alta Atração';
  if (level >= 55) return 'Interessada';
  if (level >= 35) return 'Curiosa';
  if (level >= 20) return 'Neutra';
  return 'Distante';
}

export function InterestMeter({ level, delta }: Props) {
  const color = getColor(level);
  const pct = Math.min(Math.max(level, 0), 100);

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <Text style={styles.label}>INTERESSE</Text>
        <View style={styles.valueRow}>
          {delta !== undefined && delta !== 0 && (
            <Text style={[styles.delta, { color: delta > 0 ? Colors.interest.high : Colors.interest.low }]}>
              {delta > 0 ? `+${delta}` : delta}
            </Text>
          )}
          <Text style={[styles.value, { color }]}>{level}</Text>
        </View>
      </View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${pct}%`, backgroundColor: color }]} />
      </View>
      <Text style={[styles.levelLabel, { color }]}>{getLabel(level)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 4,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    backgroundColor: Colors.bg.secondary,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border.subtle,
  },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  label: { ...Typography.label, color: Colors.text.muted },
  valueRow: { flexDirection: 'row', alignItems: 'baseline', gap: 6 },
  delta: { ...Typography.caption, fontWeight: '700' },
  value: { ...Typography.h3, fontWeight: '700' },
  track: {
    height: 4,
    backgroundColor: Colors.bg.elevated,
    borderRadius: 2,
    overflow: 'hidden',
  },
  fill: { height: 4, borderRadius: 2 },
  levelLabel: { ...Typography.caption, fontWeight: '600' },
});
