# Model card: pose_phone_v0

- Task: markerless 2D pose from phone football starts (adapters: `docs/models/mediapipe_v1.md`,
  `docs/models/rtmpose_v1.md`, fixture for CI)
- Validation target (not met, not measured): ICC > 0.8 vs mocap / timing gates before share-card use
- Current evidence: none. `golden_set: pending`; all CI runs use synthetic fixture poses.
- Not a medical device
- Known failure modes: see the adapter cards. Cue-formula limits (heuristics without a source) are
  listed in `docs/audit/open_questions.md`.
