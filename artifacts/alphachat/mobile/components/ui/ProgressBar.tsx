import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Radius, Typography } from '../../constants/theme';

interface Props {
  value: number;
  max?: number;
  label?: string;
  color?: string;
  height?: number;
  showValue?: boolean;
}

export function ProgressBar({ value, max = 100, label, color = Colors.accent.gold, height = 6, showValue }: Props) {
  const pct = Math.min(Math.max(value / max, 0), 1);
  return (
    <View style={styles.container}>
      {(label || showValue) && (
        <View style={styles.header}>
          {label && <Text style={styles.label}>{label}</Text>}
          {showValue && <Text style={[styles.label, { color }]}>{Math.round(pct * 100)}%</Text>}
        </View>
      )}
      <View style={[styles.track, { height }]}>
        <View style={[styles.fill, { width: `${pct * 100}%`, backgroundColor: color, height }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: 4 },
  header: { flexDirection: 'row', justifyContent: 'space-between' },
  label: { ...Typography.caption, color: Colors.text.secondary },
  track: {
    backgroundColor: Colors.bg.elevated,
    borderRadius: Radius.full,
    overflow: 'hidden',
  },
  fill: {
    borderRadius: Radius.full,
  },
});
