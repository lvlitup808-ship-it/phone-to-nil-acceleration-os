-- NOT WIRED: no code loads this file; the API uses in-memory stores.
-- Known drift from the API payloads (see docs/audit/open_questions.md):
--   consents: API emits consent_id, consent_scope (list), revoked, revoked_at,
--             parent_attested, granted_at; this table has scope TEXT, granted, version.
--   assessments: Slice 2 adds assessment_status, events, calibration_mode, versions,
--             assessment_lineage, consent_id, pose_source; not represented here.
--   clips: API also stores fps, duration_s, consent_id.
-- JSON Schemas generated from the pydantic models live next to this file (*.schema.json).

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
