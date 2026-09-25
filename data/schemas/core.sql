CREATE TABLE IF NOT EXISTS athletes (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  school_level TEXT,
  team_id TEXT
);

CREATE TABLE IF NOT EXISTS clips (
  id TEXT PRIMARY KEY,
  athlete_id TEXT NOT NULL,
  angle TEXT NOT NULL,
  uri TEXT,
  quality JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS assessments (
  id TEXT PRIMARY KEY,
  athlete_id TEXT NOT NULL,
  template TEXT NOT NULL,
  cues JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS consents (
  id TEXT PRIMARY KEY,
  athlete_id TEXT NOT NULL,
  scope TEXT NOT NULL,
  granted BOOLEAN NOT NULL,
  version TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
