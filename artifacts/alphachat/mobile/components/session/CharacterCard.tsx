import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';
import { Colors, CharacterColors, Radius, Spacing, Typography } from '../../constants/theme';
import { CHARACTERS, type CharacterType } from '../../constants/scenarios';

interface Props {
  type: CharacterType;
  selected?: boolean;
  onPress: () => void;
}

export function CharacterCard({ type, selected, onPress }: Props) {
  const char = CHARACTERS[type];
  const color = CharacterColors[type];

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.8}
      style={[styles.card, selected && { borderColor: color, backgroundColor: color + '12' }]}
    >
      <View style={styles.header}>
        <View style={[styles.badge, { backgroundColor: color + '22' }]}>
          <Text style={[styles.archetype, { color }]}>{char.archetype}</Text>
        </View>
        {selected && <View style={[styles.dot, { backgroundColor: color }]} />}
      </View>
      <Text style={styles.name}>{char.name}, {char.age}</Text>
      <Text style={styles.description}>{char.description}</Text>
      <View style={[styles.challengeRow, { borderTopColor: color + '33' }]}>
        <Text style={[styles.challengeLabel, { color }]}>⚡ </Text>
        <Text style={styles.challengeText}>{char.challenge}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.bg.card,
    borderRadius: Radius.lg,
    borderWidth: 1.5,
    borderColor: Colors.border.subtle,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  badge: { borderRadius: Radius.full, paddingHorizontal: 10, paddingVertical: 3 },
  archetype: { ...Typography.label, fontSize: 10 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  name: { ...Typography.h3, color: Colors.text.primary },
  description: { ...Typography.bodySmall, color: Colors.text.secondary, lineHeight: 18 },
  challengeRow: { flexDirection: 'row', borderTopWidth: 1, paddingTop: Spacing.sm },
  challengeLabel: { ...Typography.bodySmall, fontWeight: '700' },
  challengeText: { ...Typography.bodySmall, color: Colors.text.muted, flex: 1 },
});
