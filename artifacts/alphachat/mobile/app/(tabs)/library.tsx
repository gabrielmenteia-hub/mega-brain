import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { Colors, Spacing, Typography, Radius } from '../../constants/theme';
import { Card } from '../../components/ui/Card';
import { searchKnowledge } from '../../lib/api';

interface Concept {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  score?: number;
}

const CATEGORIES = ['Todos', 'Presença', 'Atração', 'Comunicação', 'Frame', 'Escalação', 'Autenticidade'];

export default function Library() {
  const [query, setQuery] = useState('');
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState('Todos');

  const search = async (q: string) => {
    if (!q.trim()) { setConcepts([]); return; }
    setLoading(true);
    try {
      const res = await searchKnowledge(q, 10);
      const mapped: Concept[] = (res.concepts ?? []).map((c: any) => ({
        id: c.id,
        title: c.nome,
        summary: c.principio,
        category: c.livros?.[0] ?? 'Conceito',
        source: c.livros?.join(', ') ?? '',
        score: c.score_similaridade,
      }));
      setConcepts(mapped);
    } catch {
      setConcepts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const t = setTimeout(() => search(query), 400);
    return () => clearTimeout(t);
  }, [query]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Biblioteca</Text>
        <Text style={styles.subtitle}>89 conceitos de 6 livros especializados</Text>
      </View>

      <View style={styles.searchRow}>
        <TextInput
          style={styles.search}
          value={query}
          onChangeText={setQuery}
          placeholder="Buscar conceito, técnica, situação..."
          placeholderTextColor={Colors.text.muted}
        />
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.cats} contentContainerStyle={styles.catsContent}>
        {CATEGORIES.map((c) => (
          <TouchableOpacity
            key={c}
            onPress={() => setActiveCategory(c)}
            style={[styles.catChip, activeCategory === c && styles.catActive]}
          >
            <Text style={[styles.catText, activeCategory === c && styles.catTextActive]}>{c}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView contentContainerStyle={styles.content}>
        {loading && <Text style={styles.loading}>Buscando…</Text>}
        {!loading && query && concepts.length === 0 && (
          <Text style={styles.empty}>Nenhum resultado para "{query}"</Text>
        )}
        {!query && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>📚</Text>
            <Text style={styles.emptyTitle}>Busca Semântica</Text>
            <Text style={styles.emptyBody}>
              Digite qualquer coisa — situação, sentimento, problema — e o sistema encontra os conceitos relevantes na base de conhecimento.
            </Text>
            <Text style={styles.emptyExample}>Experimente: "ela ficou fria de repente"</Text>
          </View>
        )}
        {concepts.map((c, i) => (
          <Card key={c.id ?? i} style={styles.conceptCard}>
            <View style={styles.conceptHeader}>
              <View style={styles.categoryBadge}>
                <Text style={styles.categoryText}>{c.category}</Text>
              </View>
              {c.score != null && (
                <Text style={styles.relevance}>{Math.round(c.score * 100)}% relevante</Text>
              )}
            </View>
            <Text style={styles.conceptTitle}>{c.title}</Text>
            <Text style={styles.conceptSummary}>{c.summary}</Text>
            <Text style={styles.conceptSource}>— {c.source}</Text>
          </Card>
        ))}
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.bg.primary },
  header: { paddingHorizontal: Spacing.md, paddingTop: 60, paddingBottom: Spacing.sm, gap: 2 },
  title: { ...Typography.h2, color: Colors.text.primary },
  subtitle: { ...Typography.caption, color: Colors.text.muted },
  searchRow: { paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm },
  search: {
    backgroundColor: Colors.bg.card,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm + 4,
    ...Typography.body,
    color: Colors.text.primary,
    borderWidth: 1,
    borderColor: Colors.border.default,
  },
  cats: { flexGrow: 0 },
  catsContent: { paddingHorizontal: Spacing.md, gap: Spacing.xs, paddingBottom: Spacing.sm },
  catChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: Radius.full,
    backgroundColor: Colors.bg.card,
    borderWidth: 1,
    borderColor: Colors.border.subtle,
  },
  catActive: { backgroundColor: Colors.accent.gold + '22', borderColor: Colors.accent.gold },
  catText: { ...Typography.caption, color: Colors.text.secondary, fontWeight: '600' },
  catTextActive: { color: Colors.accent.gold },
  content: { padding: Spacing.md, gap: Spacing.sm },
  loading: { ...Typography.body, color: Colors.text.muted, textAlign: 'center', paddingTop: Spacing.xl },
  empty: { ...Typography.body, color: Colors.text.muted, textAlign: 'center', paddingTop: Spacing.xl },
  emptyState: { alignItems: 'center', paddingTop: Spacing.xxl, gap: Spacing.md, paddingHorizontal: Spacing.xl },
  emptyIcon: { fontSize: 48 },
  emptyTitle: { ...Typography.h3, color: Colors.text.primary },
  emptyBody: { ...Typography.body, color: Colors.text.secondary, textAlign: 'center', lineHeight: 22 },
  emptyExample: { ...Typography.bodySmall, color: Colors.text.muted, fontStyle: 'italic' },
  conceptCard: { gap: Spacing.sm },
  conceptHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  categoryBadge: {
    backgroundColor: Colors.accent.gold + '18',
    borderRadius: Radius.full,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  categoryText: { ...Typography.caption, color: Colors.accent.gold, fontWeight: '700' },
  relevance: { ...Typography.caption, color: Colors.text.muted },
  conceptTitle: { ...Typography.h3, color: Colors.text.primary },
  conceptSummary: { ...Typography.body, color: Colors.text.secondary, lineHeight: 22 },
  conceptSource: { ...Typography.caption, color: Colors.text.muted, fontStyle: 'italic' },
});
