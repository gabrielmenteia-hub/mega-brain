import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert, Linking } from 'react-native';
import { router } from 'expo-router';
import { Colors, Spacing, Typography, Radius } from '../../constants/theme';
import { Card } from '../../components/ui/Card';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { useAuthStore, useProgressStore } from '../../lib/store';
import { supabase } from '../../lib/supabase';
import { getSubscriptionStatus, createCheckout } from '../../lib/api';

const PLAN_LABELS: Record<string, string> = {
  free: '🆓 Gratuito',
  pro: '⚡ Pro',
  master: '👑 Master',
};

const PLAN_DETAIL: Record<string, string> = {
  free: '3 sessões/dia · Modo guiado básico',
  pro: '20 sessões/dia · Coach avançado',
  master: 'Sessões ilimitadas · Todos os recursos',
};

export default function Profile() {
  const { email, plan, setPlan, clearAuth } = useAuthStore();
  const { level, xp, xpNextLevel, totalSessions, bestScore, streak } = useProgressStore();
  const [loadingUpgrade, setLoadingUpgrade] = useState(false);

  useEffect(() => {
    getSubscriptionStatus()
      .then((d) => { if (d?.plan) setPlan(d.plan); })
      .catch(() => {});
  }, []);

  const handleLogout = () => {
    Alert.alert('Sair', 'Deseja sair da conta?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Sair',
        style: 'destructive',
        onPress: async () => {
          await supabase.auth.signOut();
          clearAuth();
          router.replace('/(auth)/login');
        },
      },
    ]);
  };

  const handleUpgrade = async (targetPlan: 'pro' | 'master') => {
    setLoadingUpgrade(true);
    try {
      const result = await createCheckout(targetPlan);
      if (result?.checkout_url) {
        await Linking.openURL(result.checkout_url);
      }
    } catch {
      Alert.alert('Erro', 'Não foi possível iniciar o checkout. Tente novamente.');
    } finally {
      setLoadingUpgrade(false);
    }
  };

  const username = email?.split('@')[0] ?? 'Usuário';
  const isPaid = plan !== 'free';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Avatar & Info */}
      <View style={styles.hero}>
        <View style={styles.avatarCircle}>
          <Text style={styles.avatarLetter}>{username[0].toUpperCase()}</Text>
        </View>
        <Text style={styles.username}>{username}</Text>
        <Text style={styles.email}>{email}</Text>
        <View style={styles.planBadge}>
          <Text style={styles.planText}>{PLAN_LABELS[plan] ?? PLAN_LABELS.free}</Text>
        </View>
      </View>

      {/* Level */}
      <Card style={styles.section}>
        <View style={styles.levelRow}>
          <Text style={styles.levelTitle}>Nível {level}</Text>
          <Text style={styles.levelXP}>{xp} / {xpNextLevel} XP</Text>
        </View>
        <ProgressBar value={xp} max={xpNextLevel} color={Colors.accent.gold} height={8} />
        <Text style={styles.levelHint}>
          {xpNextLevel - xp} XP para Nível {level + 1}
        </Text>
      </Card>

      {/* Stats */}
      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>ESTATÍSTICAS</Text>
        <View style={styles.statsGrid}>
          <StatItem value={totalSessions} label="Sessões" />
          <StatItem value={bestScore > 0 ? bestScore.toFixed(1) : '—'} label="Melhor Score" />
          <StatItem value={streak} label="Streak" />
          <StatItem value={totalSessions > 0 ? Math.round((bestScore / 10) * 100) + '%' : '—'} label="Taxa Acerto" />
        </View>
      </Card>

      {/* Plan */}
      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>PLANO</Text>
        <View style={styles.planRow}>
          <View>
            <Text style={styles.planName}>{PLAN_LABELS[plan] ?? PLAN_LABELS.free}</Text>
            <Text style={styles.planDetail}>{PLAN_DETAIL[plan] ?? PLAN_DETAIL.free}</Text>
          </View>
          {!isPaid && (
            <TouchableOpacity
              style={[styles.upgradeBtn, loadingUpgrade && styles.upgradeBtnDisabled]}
              onPress={() => handleUpgrade('pro')}
              disabled={loadingUpgrade}
            >
              <Text style={styles.upgradeText}>{loadingUpgrade ? '…' : 'Upgrade ›'}</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.planFeatures}>
          <PlanFeature label="Simulações ilimitadas" available={plan === 'master'} />
          <PlanFeature label="Todos os cenários" available={true} />
          <PlanFeature label="Coach avançado" available={isPaid} />
          <PlanFeature label="Análise profunda" available={isPaid} />
          <PlanFeature label="Biblioteca completa" available={true} />
        </View>

        {!isPaid && (
          <View style={styles.plansRow}>
            <TouchableOpacity
              style={styles.planOption}
              onPress={() => handleUpgrade('pro')}
              disabled={loadingUpgrade}
            >
              <Text style={styles.planOptionTitle}>Pro</Text>
              <Text style={styles.planOptionPrice}>R$ 29,90/mês</Text>
              <Text style={styles.planOptionDetail}>20 sessões/dia</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.planOption, styles.planOptionHighlight]}
              onPress={() => handleUpgrade('master')}
              disabled={loadingUpgrade}
            >
              <Text style={[styles.planOptionTitle, { color: Colors.accent.gold }]}>Master</Text>
              <Text style={styles.planOptionPrice}>R$ 59,90/mês</Text>
              <Text style={styles.planOptionDetail}>Ilimitado</Text>
            </TouchableOpacity>
          </View>
        )}
      </Card>

      {/* Actions */}
      <Card style={styles.section}>
        <TouchableOpacity style={styles.menuItem} onPress={handleLogout}>
          <Text style={styles.menuItemText}>Sair da conta</Text>
          <Text style={styles.menuItemArrow}>›</Text>
        </TouchableOpacity>
      </Card>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function StatItem({ value, label }: { value: any; label: string }) {
  return (
    <View style={statStyles.item}>
      <Text style={statStyles.value}>{value}</Text>
      <Text style={statStyles.label}>{label}</Text>
    </View>
  );
}

function PlanFeature({ label, available }: { label: string; available: boolean }) {
  return (
    <View style={featureStyles.row}>
      <Text style={[featureStyles.check, { color: available ? Colors.interest.high : Colors.text.muted }]}>
        {available ? '✓' : '✗'}
      </Text>
      <Text style={[featureStyles.label, !available && { color: Colors.text.muted }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg.primary },
  content: { gap: Spacing.md, paddingBottom: Spacing.xl },
  hero: { alignItems: 'center', paddingTop: 60, paddingBottom: Spacing.lg, gap: Spacing.sm, paddingHorizontal: Spacing.md },
  avatarCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: Colors.accent.gold + '22',
    borderWidth: 2,
    borderColor: Colors.accent.gold,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarLetter: { ...Typography.h1, color: Colors.accent.gold },
  username: { ...Typography.h2, color: Colors.text.primary },
  email: { ...Typography.bodySmall, color: Colors.text.muted },
  planBadge: { backgroundColor: Colors.bg.elevated, borderRadius: Radius.full, paddingHorizontal: 12, paddingVertical: 4 },
  planText: { ...Typography.caption, color: Colors.text.secondary },
  section: { marginHorizontal: Spacing.md, gap: Spacing.sm },
  sectionTitle: { ...Typography.label, color: Colors.text.muted },
  levelRow: { flexDirection: 'row', justifyContent: 'space-between' },
  levelTitle: { ...Typography.h3, color: Colors.accent.gold },
  levelXP: { ...Typography.caption, color: Colors.text.muted },
  levelHint: { ...Typography.caption, color: Colors.text.muted },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  planRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  planName: { ...Typography.h3, color: Colors.text.primary },
  planDetail: { ...Typography.caption, color: Colors.text.muted },
  upgradeBtn: { backgroundColor: Colors.accent.gold, borderRadius: Radius.full, paddingHorizontal: 16, paddingVertical: 6 },
  upgradeBtnDisabled: { opacity: 0.5 },
  upgradeText: { ...Typography.caption, color: Colors.text.inverse, fontWeight: '700' },
  planFeatures: { gap: Spacing.xs, marginTop: Spacing.xs },
  plansRow: { flexDirection: 'row', gap: Spacing.sm, marginTop: Spacing.sm },
  planOption: {
    flex: 1,
    backgroundColor: Colors.bg.elevated,
    borderRadius: Radius.md,
    padding: Spacing.sm,
    alignItems: 'center',
    gap: 2,
    borderWidth: 1,
    borderColor: Colors.border.subtle,
  },
  planOptionHighlight: {
    borderColor: Colors.accent.gold,
    backgroundColor: Colors.accent.gold + '12',
  },
  planOptionTitle: { ...Typography.label, color: Colors.text.primary },
  planOptionPrice: { ...Typography.h3, color: Colors.text.primary },
  planOptionDetail: { ...Typography.caption, color: Colors.text.muted },
  menuItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: Spacing.xs },
  menuItemText: { ...Typography.body, color: Colors.status.error },
  menuItemArrow: { ...Typography.body, color: Colors.text.muted },
});

const statStyles = StyleSheet.create({
  item: { width: '47%', backgroundColor: Colors.bg.elevated, borderRadius: Radius.md, padding: Spacing.sm, alignItems: 'center', gap: 2 },
  value: { ...Typography.h2, color: Colors.text.primary },
  label: { ...Typography.caption, color: Colors.text.muted },
});

const featureStyles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  check: { ...Typography.body, fontWeight: '700', width: 16 },
  label: { ...Typography.body, color: Colors.text.secondary },
});
