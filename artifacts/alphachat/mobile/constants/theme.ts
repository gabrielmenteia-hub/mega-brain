export const Colors = {
  bg: {
    primary: '#0D0D0D',
    secondary: '#141414',
    card: '#1A1A1A',
    elevated: '#222222',
    overlay: 'rgba(0,0,0,0.7)',
  },
  accent: {
    gold: '#C9A84C',
    goldLight: '#E8C870',
    blue: '#4C7BC9',
    teal: '#4CC9A8',
    red: '#C94C4C',
    purple: '#8B4CC9',
  },
  text: {
    primary: '#F5F5F5',
    secondary: '#A0A0A0',
    muted: '#555555',
    inverse: '#0D0D0D',
  },
  border: {
    subtle: '#2A2A2A',
    default: '#333333',
    strong: '#444444',
  },
  status: {
    success: '#4CAF50',
    warning: '#FF9800',
    error: '#F44336',
    info: '#2196F3',
  },
  interest: {
    low: '#C94C4C',
    mid: '#FF9800',
    high: '#4CAF50',
  },
} as const;

export const CharacterColors: Record<string, string> = {
  high_value: Colors.accent.gold,
  intellectual: Colors.accent.blue,
  casual_fun: Colors.accent.teal,
  girl_next_door: Colors.accent.purple,
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const Radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 999,
} as const;

export const Typography = {
  h1: { fontSize: 28, fontWeight: '700' as const, letterSpacing: -0.5 },
  h2: { fontSize: 22, fontWeight: '700' as const, letterSpacing: -0.3 },
  h3: { fontSize: 18, fontWeight: '600' as const },
  body: { fontSize: 15, fontWeight: '400' as const, lineHeight: 22 },
  bodySmall: { fontSize: 13, fontWeight: '400' as const, lineHeight: 18 },
  caption: { fontSize: 11, fontWeight: '500' as const, letterSpacing: 0.5 },
  label: { fontSize: 12, fontWeight: '600' as const, letterSpacing: 0.8, textTransform: 'uppercase' as const },
} as const;
