import axios from 'axios';
import Constants from 'expo-constants';

const BASE_URL = Constants.expoConfig?.extra?.apiUrl ?? 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config: any) => {
  const { useAuthStore } = require('./store');
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Sessions
export const createSession = async (payload: { scenario: string; character: string; mode: string }) => {
  const { data } = await api.post('/api/sessions/create', payload);
  return data;
};

export const endSession = async (sessionId: string) => {
  const { data } = await api.post(`/api/sessions/${sessionId}/end`);
  return data;
};

export const getSession = async (sessionId: string) => {
  const { data } = await api.get(`/api/sessions/${sessionId}`);
  return data;
};

// Messages
export const sendMessage = async (payload: { session_id: string; text: string }) => {
  const { data } = await api.post('/api/messages/send', payload);
  return data;
};

export const getHistory = async (sessionId: string) => {
  const { data } = await api.get(`/api/messages/history/${sessionId}`);
  return data;
};

// Progress
export const getUserProgress = async () => {
  const { data } = await api.get('/api/progress/overview');
  return data;
};

export const getSessionAnalysis = async (sessionId: string) => {
  const { data } = await api.get(`/api/progress/session/${sessionId}`);
  return data;
};

// Knowledge
export const searchKnowledge = async (query: string, topK = 5) => {
  const { data } = await api.get(
    `/api/knowledge/search?query=${encodeURIComponent(query)}&top_k=${topK}`
  );
  return data;
};

export const getConcept = async (conceptId: string) => {
  const { data } = await api.get(`/api/knowledge/concept/${conceptId}`);
  return data;
};

// Subscription
export const getSubscriptionStatus = async () => {
  const { data } = await api.get('/api/subscription/status');
  return data;
};

export const getPlans = async () => {
  const { data } = await api.get('/api/subscription/plans');
  return data;
};

export const createCheckout = async (plan: string) => {
  const { data } = await api.post('/api/subscription/checkout', { plan });
  return data;
};
