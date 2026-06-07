-- AlphaChat — Schema Supabase
-- Execute no SQL Editor do Supabase

-- Usuários
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  subscription_tier VARCHAR(20) DEFAULT 'free',
  subscription_status VARCHAR(20) DEFAULT 'active',
  subscription_expires_at TIMESTAMP,
  stripe_customer_id VARCHAR(255),
  total_xp INTEGER DEFAULT 0,
  level INTEGER DEFAULT 1
);

-- Skills por usuário
CREATE TABLE user_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  skill VARCHAR(50) NOT NULL,
  xp INTEGER DEFAULT 0,
  nivel INTEGER DEFAULT 1,
  UNIQUE(user_id, skill)
);

-- Inicializar skills para novo usuário
CREATE OR REPLACE FUNCTION init_user_skills()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_skills (user_id, skill) VALUES
    (NEW.id, 'confianca'),
    (NEW.id, 'frame'),
    (NEW.id, 'calibracao'),
    (NEW.id, 'polaridade'),
    (NEW.id, 'assertividade');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_user_created
AFTER INSERT ON users
FOR EACH ROW EXECUTE FUNCTION init_user_skills();

-- Sessões de treino
CREATE TABLE training_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  scenario VARCHAR(50) NOT NULL,
  character VARCHAR(50) NOT NULL,
  mode VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  interest_level INTEGER DEFAULT 20,
  turn_count INTEGER DEFAULT 0,
  last_coach_score FLOAT DEFAULT 0,
  xp_gained INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  ended_at TIMESTAMP
);

-- Mensagens
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES training_sessions(id) ON DELETE CASCADE,
  turn INTEGER NOT NULL,
  sender VARCHAR(20) NOT NULL,
  text TEXT NOT NULL,
  analysis JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_sessions_user ON training_sessions(user_id);
CREATE INDEX idx_sessions_created ON training_sessions(created_at);
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_turn ON messages(session_id, turn);
CREATE INDEX idx_users_stripe ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;

-- RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own data" ON users FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users own sessions" ON training_sessions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users own messages" ON messages FOR ALL USING (
  session_id IN (SELECT id FROM training_sessions WHERE user_id = auth.uid())
);
CREATE POLICY "Users own skills" ON user_skills FOR ALL USING (auth.uid() = user_id);
