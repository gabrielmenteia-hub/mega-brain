export type ScenarioType = 'match_no_app' | 'primeira_mensagem' | 'primeiro_encontro' | 'testes_e_objecoes' | 'escalacao';
export type CharacterType = 'casual_fun' | 'intellectual' | 'high_value' | 'girl_next_door';
export type ModeType = 'livre' | 'guiado' | 'desafio';

export const SCENARIOS: Record<ScenarioType, { label: string; description: string; icon: string; difficulty: number }> = {
  match_no_app: {
    label: 'Match no App',
    description: 'Primeiro contato via app de relacionamento. Transforme o match em conversa real.',
    icon: '📱',
    difficulty: 1,
  },
  primeira_mensagem: {
    label: 'Primeira Mensagem',
    description: 'Abordagem fria nas redes sociais. Crie conexão do zero.',
    icon: '✉️',
    difficulty: 2,
  },
  primeiro_encontro: {
    label: 'Primeiro Encontro',
    description: 'Café ou drink. Construa atração presencial em tempo real.',
    icon: '☕',
    difficulty: 3,
  },
  testes_e_objecoes: {
    label: 'Testes e Objeções',
    description: 'Ela está testando seus limites. Responda com confiança e autenticidade.',
    icon: '⚔️',
    difficulty: 4,
  },
  escalacao: {
    label: 'Escalação',
    description: 'A conexão está estabelecida. Eleve o nível da interação com calibração.',
    icon: '🔥',
    difficulty: 5,
  },
};

export const CHARACTERS: Record<CharacterType, {
  name: string;
  age: number;
  archetype: string;
  description: string;
  challenge: string;
  colorKey: string;
}> = {
  high_value: {
    name: 'Isabela',
    age: 27,
    archetype: 'High Value',
    description: 'Executiva bem-sucedida. Acostumada com homens que tentam impressioná-la. Valoriza autenticidade e presença.',
    challenge: 'Não se deixar impressionar com facilidade',
    colorKey: 'gold',
  },
  intellectual: {
    name: 'Marina',
    age: 25,
    archetype: 'Intelectual',
    description: 'Doutoranda em filosofia. Analítica e perspicaz. Responde a ideias e profundidade.',
    challenge: 'Vai testar sua consistência intelectual',
    colorKey: 'blue',
  },
  casual_fun: {
    name: 'Carla',
    age: 23,
    archetype: 'Casual Fun',
    description: 'Espontânea e divertida. Quer energia boa e leveza. Desaparece com quem é pesado.',
    challenge: 'Manter o fluxo sem forçar',
    colorKey: 'teal',
  },
  girl_next_door: {
    name: 'Sofia',
    age: 24,
    archetype: 'Girl Next Door',
    description: 'Gentil e observadora. Valoriza conexão genuína acima de tudo.',
    challenge: 'Detecta pretensão imediatamente',
    colorKey: 'purple',
  },
};

export const MODES: Record<ModeType, { label: string; description: string; icon: string }> = {
  livre: {
    label: 'Livre',
    description: 'Sem assistência. Você dirige a conversa.',
    icon: '🧭',
  },
  guiado: {
    label: 'Guiado',
    description: 'Coach sugere abordagens em tempo real.',
    icon: '🎯',
  },
  desafio: {
    label: 'Desafio',
    description: 'Situações difíceis. Pontuação dobrada.',
    icon: '🏆',
  },
};
