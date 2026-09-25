# Audit open questions (P3 — not fixed in this pass)

Each item needs real film, a real coach, a hardware benchmark, or a product / legal decision. None was
guessed. Owners are roles; the repo has one CODEOWNER, so "owner" means the person who plays that role.

| # | Item | Why it is blocked | Owner | Blocking |
| --- | --- | --- | --- | --- |
| 1 | Accuracy of all 12 frozen cues (MAE vs coach labels) | Needs ≥ 10 WR + 10 DB coach-labeled clips of real film | Film lead + position coach | Gate stays closed; no accuracy claim allowed |
| 2 | Calibration error (`error_yd`) for `field_line` and `height_prior` | Needs benchmark clips with known field geometry (`docs/validation/calibration_v1.md`) | Film lead | Any distance cue claim |
| 3 | Shin-angle reference convention: angle from the image vertical (what the code computes) vs from the ground | Coaching definition; changes what a "good" number is | Position coach + product | Session 1 sanity check; labeling UI copy |
| 4 | Sanity bands in `session_1.md` (shin 30–50°, hip height 0.75–0.95) | No source. Hip band conflicts with the implemented ratio (standing adult ≈ 0.5). Marked `unverified` | Position coach | Session 1 night review |
| 5 | `ground_contact_time_first_step = max(90, 0.45 × step-to-step ms)` | Heuristic with no source; the 0.45 factor and 90 ms floor are unverified. Needs high-fps film or a contact mat | CV lead | GCT cue meaning |
| 6 | `hip_rotation_rate` measures hip-midpoint translation speed (px/s), not rotation; `eye_discipline_proxy` is nose-vs-hip x variance (px²) | Names are frozen (`cue_freeze_v1.md`); whether the proxies are acceptable is a product call. Units were corrected, names were not touched | Product + CV lead | DB cue interpretation |
| 7 | Lead leg is always the right ankle/knee in WR/DB formulas | Needs a decision on detecting lead leg, and film of left-lead athletes to test | CV lead | Left-lead athletes get wrong cues |
| 8 | Event detector accuracy (motion_start, first_step, release/break) | Needs coach-marked events on real film (±3 frames target in `session_1.md`) | Film lead + coach | Every timing cue |
| 9 | MediaPipe on real football film at 30/60 fps | `mediapipe` is not installed in CI; adapter has never run on real frames here | CV lead | Moving off fixture poses |
| 10 | RTMPose | Stays off. Needs weights and a golden-set comparison (week 3 of `schedule.md`) | CV lead | — |
| 11 | `/pose/assess` accepts a `clip_id` but always runs synthetic fixture poses; it now says `pose_source: "fixture"`. Should it refuse instead until frames are wired? | Product decision (Slice 2 contract is fixture-only by design) | Product | Any external caller treating output as a measurement |
| 12 | Slice 1 `/assess` returns template cues with coaching notes ("Hips rise early…") even when no metric was measured (`value: null`, confidence 0.45) | Copy/product decision; Slice 1 contract. Not changed | Product + copy review (`docs/copy/athlete_facing_review.md`) | Athlete-facing copy |
| 13 | NIL bands: p25/p50/p75 are `null` | No comp dataset exists. Needs a sourced comp dataset and a decision on the model | Product + legal | Any NIL number |
| 14 | Parental consent for minors not enforced; DOB not collected; `minors_mode` on `/pose/assess` is echoed only | Needs legal decision on age capture and what minors mode must change | Legal + product | Filming minors outside the paper-form process |
| 15 | Consent scope vocabulary: "improve the system" checkbox has no scope string; recruiter API / share cards / authenticity disclosure in `consent.md` are on neither form | Legal decision | Legal | Using clips for model improvement |
| 16 | Retention (90 days raw video / pose debug, 30 days Jev logs) not enforced | `data_retention.md` defers to Slice 3; needs storage design | Eng + legal | Storing real athlete film longer than a session |
| 17 | `data/schemas/core.sql` is not wired and drifts from payloads (consents, assessments, clips) | Choosing the DB schema is a design decision; no code reads it | Eng | Moving off in-memory stores |
| 18 | No Consent, Clip, Passport, or CoachSession payload models / schemas; Slice 1 `Assessment` model does not match `/assess` output (no `quality`, adds `evidence`) and is unused; `Drill.cue: CueId` cannot validate `drills.json` (uses Slice 2 cue names) | Needs a decision on which contract is canonical before writing schemas | Eng | External integrators |
| 19 | Gate diversity fields (`surface`, `lighting`, `athlete_id`) are read from manifest clips; the manifest template does not have them yet | Intake form collects them; manifest format change is a data-ops decision | Film lead | Gate can never open until these are recorded |
| 20 | Gate change review: gate now also requires the `film_first.md` mix (3 surfaces, 2 lighting, 3 athletes/position). Stricter than the `wr ≥ 10, db ≥ 10, inter-rater` formula | Confirm the doc's mix is intended to be enforced | Product | Merge of this PR |
| 21 | `/nil-band`, `/prescribe`, `/passport` now return `blocked_on_golden_set` with null / empty values; `NILBand` numeric fields became nullable | Keys are kept, but a client that assumed ints or non-empty drills sees a type/content change. Gates and no-fabrication win per audit rules; confirm | Product | Merge of this PR |
| 22 | Docker image build (`ci.yml` job `docker`) | Not run in this audit (no Docker daemon available here) | Eng | CI result on the PR |
| 23 | Coach console / mobile apps (`apps/`) | Not built or type-checked in this pass (only the Python toolchain was exercised); `apps/mobile/App.tsx` sends a hard-coded `quality_score: 0.88` | Eng | — |
| 24 | Dead code: `packages/judgment/log.py::log_jev`, `packages/media/synthetic.py::corroborate` are never called | Referenced by docs as planned (Jev log retention, synthetic second model). Removing is a product call | Eng | — |
