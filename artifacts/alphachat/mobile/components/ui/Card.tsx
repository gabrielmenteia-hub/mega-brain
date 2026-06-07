import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Colors, Radius, Spacing } from '../../constants/theme';

interface Props {
  children: React.ReactNode;
  style?: ViewStyle;
  elevated?: boolean;
  padded?: boolean;
}

export function Card({ children, style, elevated, padded = true }: Props) {
  return (
    <View style={[styles.card, elevated && styles.elevated, padded && styles.padded, style]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.bg.card,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.border.subtle,
  },
  elevated: {
    backgroundColor: Colors.bg.elevated,
    borderColor: Colors.border.default,
  },
  padded: {
    padding: Spacing.md,
  },
});
