import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, TextInput, ScrollView, TouchableOpacity,
  StyleSheet, KeyboardAvoidingView, Platform, Alert
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import * as Haptics from 'expo-haptics';
import { Colors, Spacing, Typography, Radius, CharacterColors } from '../../constants/theme';
import { InterestMeter } from '../../components/chat/InterestMeter';
import { MessageBubble } from '../../components/chat/MessageBubble';
import { useSessionStore, useAuthStore } from '../../lib/store';
import { sendMessage, endSession } from '../../lib/api';

export default function ChatSession() {
  useLocalSearchParams<{ id: string }>();
  const [input, setInput] = useState('');
  const scrollRef = useRef<ScrollView>(null);
  const { userId } = useAuthStore();
  const {
    sessionId, character, mode, characterName,
    interestLevel, messages, isLoading,
    addMessage, updateInterest, incrementTurn, setLoading,
  } = useSessionStore();

  const charColor = character ? CharacterColors[character] : Colors.accent.gold;
  const [delta, setDelta] = useState<number | undefined>(undefined);

  useEffect(() => {
    scrollRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !sessionId) return;
    const text = input.trim();
    setInput('');

    addMessage({ role: 'user', content: text, timestamp: new Date().toISOString() });
    setLoading(true);

    try {
      const res = await sendMessage({ session_id: sessionId, text }, userId ?? '');

      const newInterest = res.interest_level ?? interestLevel;
      const d = newInterest - interestLevel;
      setDelta(d !== 0 ? d : undefined);
      updateInterest(newInterest);
      incrementTurn();

      addMessage({
        role: 'character',
        content: res.character_response,
        timestamp: new Date().toISOString(),
        interest_delta: d !== 0 ? d : undefined,
      });

      if (mode === 'guiado' && res.coach_tip) {
        addMessage({ role: 'coach', content: res.coach_tip, timestamp: new Date().toISOString() });
      }

      if (d > 10) Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      else if (d < -10) Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);

    } catch (e) {
      addMessage({ role: 'coach', content: 'Erro ao conectar com o servidor. Verifique sua conexão.', timestamp: new Date().toISOString() });
    } finally {
      setLoading(false);
    }
  };

  const handleEnd = () => {
    Alert.alert('Encerrar sessão?', 'Você receberá sua análise completa.', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Encerrar',
        style: 'destructive',
        onPress: async () => {
          if (!sessionId) return;
          const result = await endSession(sessionId).catch(() => ({ level_up: false }));
          router.replace(`/session/analysis/${sessionId}?level_up=${result.level_up ? '1' : '0'}`);
        },
      },
    ]);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={0}
    >
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: charColor + '44' }]}>
        <View style={styles.headerLeft}>
          <View style={[styles.avatar, { backgroundColor: charColor + '22', borderColor: charColor }]}>
            <Text style={[styles.avatarText, { color: charColor }]}>👤</Text>
          </View>
          <View>
            <Text style={[styles.charName, { color: charColor }]}>{characterName}</Text>
            <Text style={styles.modeBadge}>{mode === 'guiado' ? '🎯 Guiado' : mode === 'desafio' ? '🏆 Desafio' : '🧭 Livre'}</Text>
          </View>
        </View>
        <TouchableOpacity onPress={handleEnd} style={styles.endBtn}>
          <Text style={styles.endText}>Encerrar</Text>
        </TouchableOpacity>
      </View>

      {/* Interest Meter */}
      <InterestMeter level={interestLevel} delta={delta} />

      {/* Messages */}
      <ScrollView
        ref={scrollRef}
        style={styles.messages}
        contentContainerStyle={styles.messagesContent}
        keyboardDismissMode="interactive"
      >
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} characterColor={charColor} />
        ))}
        {isLoading && (
          <View style={styles.typing}>
            <Text style={[styles.typingText, { color: charColor }]}>{characterName} está digitando…</Text>
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Digite sua mensagem..."
          placeholderTextColor={Colors.text.muted}
          multiline
          maxLength={400}
          returnKeyType="send"
          onSubmitEditing={handleSend}
        />
        <TouchableOpacity
          onPress={handleSend}
          disabled={!input.trim() || isLoading}
          style={[styles.sendBtn, { backgroundColor: charColor }, (!input.trim() || isLoading) && styles.sendDisabled]}
        >
          <Text style={styles.sendIcon}>↑</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg.primary },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingTop: 56,
    paddingBottom: Spacing.sm,
    borderBottomWidth: 1,
  },
  headerLeft: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  avatar: { width: 36, height: 36, borderRadius: 18, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center' },
  avatarText: { fontSize: 16 },
  charName: { ...Typography.h3 },
  modeBadge: { ...Typography.caption, color: Colors.text.muted },
  endBtn: {
    backgroundColor: Colors.bg.card,
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: Radius.full,
    borderWidth: 1,
    borderColor: Colors.border.default,
  },
  endText: { ...Typography.bodySmall, color: Colors.text.secondary, fontWeight: '600' },
  messages: { flex: 1 },
  messagesContent: { paddingTop: Spacing.md, paddingBottom: Spacing.md },
  typing: { paddingHorizontal: Spacing.md, marginBottom: Spacing.sm },
  typingText: { ...Typography.caption, fontStyle: 'italic' },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: Spacing.sm,
    padding: Spacing.sm,
    paddingBottom: Platform.OS === 'ios' ? 28 : Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.border.subtle,
    backgroundColor: Colors.bg.secondary,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.bg.card,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: 10,
    ...Typography.body,
    color: Colors.text.primary,
    maxHeight: 120,
    borderWidth: 1,
    borderColor: Colors.border.default,
  },
  sendBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  sendDisabled: { opacity: 0.4 },
  sendIcon: { color: Colors.text.inverse, fontSize: 18, fontWeight: '700' },
});
