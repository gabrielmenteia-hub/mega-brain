import { create } from 'zustand';
import type { ScenarioType, CharacterType, ModeType } from '../constants/scenarios';

// Auth Store
interface AuthState {
  userId: string | null;
  token: string | null;
  email: string | null;
  plan: string;  // 'free' | 'pro' | 'master'
  setAuth: (userId: string, token: string, email: string) => void;
  setPlan: (plan: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  userId: null,
  token: null,
  email: null,
  plan: 'free',
  setAuth: (userId, token, email) => set({ userId, token, email }),
  setPlan: (plan) => set({ plan }),
  clearAuth: () => set({ userId: null, token: null, email: null, plan: 'free' }),
}));

// Session Store
export interface Message {
  role: 'user' | 'character' | 'coach';
  content: string;
  timestamp: string;
  interest_delta?: number;
  coach_tip?: string;
}

interface SessionState {
  sessionId: string | null;
  scenario: ScenarioType | null;
  character: CharacterType | null;
  mode: ModeType | null;
  characterName: string | null;
  interestLevel: number;
  turnCount: number;
  messages: Message[];
  isLoading: boolean;
  startSession: (data: {
    sessionId: string;
    scenario: ScenarioType;
    character: CharacterType;
    mode: ModeType;
    characterName: string;
    openingMessage: string;
    interestLevel: number;
  }) => void;
  addMessage: (msg: Message) => void;
  updateInterest: (level: number) => void;
  incrementTurn: () => void;
  setLoading: (v: boolean) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  scenario: null,
  character: null,
  mode: null,
  characterName: null,
  interestLevel: 20,
  turnCount: 0,
  messages: [],
  isLoading: false,
  startSession: (data) =>
    set({
      sessionId: data.sessionId,
      scenario: data.scenario,
      character: data.character,
      mode: data.mode,
      characterName: data.characterName,
      interestLevel: data.interestLevel,
      turnCount: 0,
      messages: [
        {
          role: 'character',
          content: data.openingMessage,
          timestamp: new Date().toISOString(),
        },
      ],
    }),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateInterest: (level) => set({ interestLevel: level }),
  incrementTurn: () => set((s) => ({ turnCount: s.turnCount + 1 })),
  setLoading: (v) => set({ isLoading: v }),
  clearSession: () =>
    set({
      sessionId: null,
      scenario: null,
      character: null,
      mode: null,
      characterName: null,
      interestLevel: 20,
      turnCount: 0,
      messages: [],
      isLoading: false,
    }),
}));

// Progress Store
interface ProgressState {
  level: number;
  xp: number;
  xpNextLevel: number;
  totalSessions: number;
  bestScore: number;
  streak: number;
  setProgress: (data: Partial<ProgressState>) => void;
}

export const useProgressStore = create<ProgressState>((set) => ({
  level: 1,
  xp: 0,
  xpNextLevel: 100,
  totalSessions: 0,
  bestScore: 0,
  streak: 0,
  setProgress: (data) => set((s) => ({ ...s, ...data })),
}));
