import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../../constants/theme';
import type { Message } from '../../lib/store';

interface Props {
  message: Message;
  characterColor?: string;
}

export function MessageBubble({ message, characterColor = Colors.accent.gold }: Props) {
  const isUser = message.role === 'user';
  const isCoach = message.role === 'coach';

  if (isCoach) {
    return (
      <View style={styles.coachContainer}>
        <View style={styles.coachBubble}>
          <Text style={styles.coachLabel}>💡 COACH</Text>
          <Text style={styles.coachText}>{message.content}</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={[styles.row, isUser && styles.rowRight]}>
      {!isUser && (
        <View style={[styles.avatar, { backgroundColor: characterColor + '22', borderColor: characterColor }]}>
          <Text style={[styles.avatarText, { color: characterColor }]}>
            {message.role === 'character' ? '👤' : '?'}
          </Text>
        </View>
      )}
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.charBubble, !isUser && { borderColor: characterColor + '44' }]}>
        <Text style={[styles.text, isUser && styles.userText]}>{message.content}</Text>
        {message.interest_delta !== undefined && message.interest_delta !== 0 && (
          <Text style={[
            styles.delta,
            { color: message.interest_delta > 0 ? Colors.interest.high : Colors.interest.low }
          ]}>
            {message.interest_delta > 0 ? `+${message.interest_delta}` : message.interest_delta} interesse
          </Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md, paddingHorizontal: Spacing.md },
  rowRight: { flexDirection: 'row-reverse' },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: Radius.full,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    marginTop: 2,
  },
  avatarText: { fontSize: 14 },
  bubble: {
    maxWidth: '78%',
    padding: Spacing.sm + 4,
    borderRadius: Radius.lg,
    borderWidth: 1,
  },
  userBubble: {
    backgroundColor: Colors.accent.gold,
    borderColor: 'transparent',
    borderBottomRightRadius: 4,
  },
  charBubble: {
    backgroundColor: Colors.bg.card,
    borderBottomLeftRadius: 4,
  },
  text: { ...Typography.body, color: Colors.text.primary },
  userText: { color: Colors.text.inverse },
  delta: { ...Typography.caption, marginTop: 4, fontWeight: '700' },
  coachContainer: { paddingHorizontal: Spacing.md, marginBottom: Spacing.md },
  coachBubble: {
    backgroundColor: Colors.accent.blue + '18',
    borderWidth: 1,
    borderColor: Colors.accent.blue + '55',
    borderRadius: Radius.md,
    padding: Spacing.sm + 4,
  },
  coachLabel: { ...Typography.label, color: Colors.accent.blue, marginBottom: 4 },
  coachText: { ...Typography.bodySmall, color: Colors.text.secondary },
});
