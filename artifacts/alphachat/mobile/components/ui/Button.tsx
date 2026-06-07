import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle } from 'react-native';
import { Colors, Radius, Typography } from '../../constants/theme';

interface Props {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

export function Button({ label, onPress, variant = 'primary', size = 'md', loading, disabled, style }: Props) {
  const isDisabled = disabled || loading;
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.75}
      style={[styles.base, styles[variant], styles[`size_${size}`], isDisabled && styles.disabled, style]}
    >
      {loading ? (
        <ActivityIndicator size="small" color={variant === 'primary' ? Colors.text.inverse : Colors.text.primary} />
      ) : (
        <Text style={[styles.label, styles[`label_${variant}`], styles[`labelSize_${size}`]]}>{label}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: Radius.md,
  },
  primary: {
    backgroundColor: Colors.accent.gold,
  },
  secondary: {
    backgroundColor: Colors.bg.elevated,
    borderWidth: 1,
    borderColor: Colors.border.default,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  danger: {
    backgroundColor: Colors.status.error,
  },
  size_sm: { paddingHorizontal: 16, paddingVertical: 8 },
  size_md: { paddingHorizontal: 24, paddingVertical: 14 },
  size_lg: { paddingHorizontal: 32, paddingVertical: 18 },
  disabled: { opacity: 0.4 },
  label: { ...Typography.body, fontWeight: '600' },
  label_primary: { color: Colors.text.inverse },
  label_secondary: { color: Colors.text.primary },
  label_ghost: { color: Colors.accent.gold },
  label_danger: { color: Colors.text.primary },
  labelSize_sm: { fontSize: 13 },
  labelSize_md: { fontSize: 15 },
  labelSize_lg: { fontSize: 17 },
});
