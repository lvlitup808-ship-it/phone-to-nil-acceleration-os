# Audit baseline — 2026-09-25

Captured on `main` @ `373a48a` before any change in this audit pass. Nothing was fixed before this file was written.

Environment: Linux container, Python 3.11.15, clean clone, `pip install -e ".[dev]"`.
Resolved versions that matter: fastapi 0.141.1, starlette 1.7.0, pydantic 2.13.5, numpy 2.4.6, opencv-python-headless 5.0.0.93, pytest 9.1.1, ruff 0.16.9. `mediapipe` (`[cv]` extra) not installed, so the pose factory falls back to the fixture adapter.

## 1. Install

`python -m pip install -e ".[dev]"` — **succeeds**, exit 0.

## 2. Tests

`python -m pytest tests -q` — **22 passed, 1 failed**.

| Test | Result | Cause |
| --- | --- | --- |
| `tests/lint/test_no_score_word.py::test_no_composite_score_identifier` | FAIL | The lint scans every `.py`/`.md`/`.ts(x)` file, including itself (its own `FORBIDDEN` tuple) and `tests/golden/test_pose_pipeline.py` (which asserts the banned key is *absent*). Five self-hits, zero hits in product code. |
| all others (22) | pass | |

Side effects of a test run (tree is dirty afterwards):

- `tests/golden/test_pose_pipeline.py::test_golden_harness_writes_pending_report` overwrites the tracked file `docs/validation/slice2_report.md` with different content.
- `tests/golden/test_pose_pipeline.py::test_pose_api_additive` writes `artifacts/clp_0001/*` into the repo root; `artifacts/` is not in `.gitignore`.

## 3. Lint and type checks

- `ruff check services packages tests` — **29 findings** (19 auto-fixable). No rule selection is configured in `pyproject.toml`, so the result depends on the ruff version installed. Breakdown: UP017 ×8, BLE001 ×5, I001 ×5, F401 ×4 (unused imports), SIM102, SIM103, UP037, RUF046, C401, RUF015, RUF022 ×1 each.
- `make lint` pipes ruff through `|| true`, so it can never fail. CI (`.github/workflows/ci.yml`) does not run ruff at all.
- `python -m compileall services packages tests` — clean.
- No type checker is configured. Ad-hoc `mypy services packages --ignore-missing-imports` (default strictness, untyped bodies not checked): "no issues found in 48 source files".

## 4. API

`uvicorn services.api.app:app --port 8000` — starts.

| Route | Result |
| --- | --- |
| `GET /health` | 200 `{"status":"ok"}` |
| `GET /docs` | 200 |
| `GET /openapi.json` | 20 operations, every one bound to a handler |
| Slice 1 `POST /upload` → `POST /assess` → `GET /prescribe/{id}` | 200 / 200 / 200 — **prescribe returns drills although the golden-set gate is closed** |
| Slice 1 `GET /nil-band/a1` | 200 with `p25=2500, p50=6000, p75=14000, confidence=0.41` — **hard-coded numbers, no comp data behind them** |
| Slice 1 `GET /passport/a1` | 200 with assessments and a hard-coded `consent: {capture: true, coach: true, public: false}` — **consent state asserted, not looked up; gate not applied** |
| Slice 2 `POST /pose/assess` | 200. Always runs the synthetic fixture pose (the route never passes frames), but the response does not say so; cues carry `source_clip_id` = caller's clip id. |
| `GET /gates/golden` | 200 `blocked_on_golden_set`, missing `wr_labeled 0/10`, `db_labeled 0/10`, `inter_rater`. Progress is a hard-coded dict of zeros, not read from `data/golden_set/`. |
| `GET /position-fit/a1` | 200 `blocked_on_golden_set` |
| `GET /nil-band/a1/scenarios` | 200 `schema_only`, `scenarios: []` |
| `POST /pose/assess` with `clip_id="../../tmp/x"` | 200 **and wrote debug files to `/home/user/tmp/x`, outside the repo** (path traversal via `clip_id`) |

No route returned 500 on fixture input.

## 5. Golden-set harness (fixture mode)

There is no standalone harness entry point; the harness is the test `test_golden_harness_writes_pending_report`. Output it writes:

```
# Slice 2 validation report

golden_set: pending
real_mp4_present: false
Do not treat this file as a performance claim.

- clp_0001: status=ok cues=6 source=fixture
- clp_0002: status=ok cues=6 source=fixture
```

It prints nothing to stdout, and the phrase "do not treat this as athlete validation" does not appear in its output (it appears only in `data/golden_set/manifest.json`'s `note`).

## 6. Findings recorded at baseline (not yet fixed)

P0 — broken, unsafe, or fabricated

1. Lint test fails on `main` (self-match).
2. `/pose/assess` path traversal: `clip_id` is joined into a filesystem path unchecked.
3. `/nil-band/{athlete_id}` (API and `services/valuation`) emits hard-coded p25/p50/p75, confidence 0.41, and "counterfactual" bands. `data/samples/comp_clusters.json` carries invented `n` and dollar quantiles.
4. `/prescribe/{id}` and `/passport/{id}` are not behind the golden-set gate.
5. `/passport` asserts consent flags it never looked up.
6. `angle_from_vertical` clamps negative `dy` to 1e-6, so any upward-pointing segment (tibia ankle→knee, torso hip→nose) returns ≈ ±90° (or exactly 0 when dx = 0). `shin_angle_at_contact` and `lean_at_release` cannot produce a meaningful value on any input. Fixture output: `shin_angle_at_contact = -89.99997`.
7. `ground_contact_time_first_step` emits a constant 170 ms with `cue_status: ok` when no second step is detected; `recovery_first_step` emits a constant 180 ms when the step order is wrong. Both are invented values.
8. When the configured pose adapter raises on real frames, `pipeline_v2` silently substitutes synthetic fixture poses and reports cues from them.

P1 — inconsistency

- Retake packet reason codes (`fps_too_low`, `too_short`, `phone_moved`, `missing_angle`, `no_field_lines`) do not match validator codes (`fps_below_30`, `duration_not_4_to_12s`, `phone_unstable_first_500ms`, `missing_side_or_45`, `bad_filename`); durations disagree (doc 5–10 s, validator 4–12 s).
- Consent revocation receipt lists `deleted_artifacts` but nothing is deleted (in-memory clips and the `artifacts/<clip_id>/` debug files written by `/pose/assess` remain).
- The prompt's reference `services/api/consent.py` does not exist; consent lives in `packages/consent/store.py`. Consent forms have four checkboxes (analysis, improve-system, coach review, public); code accepts any free-form scope strings; `docs/legal/consent.md` lists a different set (recruiter API, authenticity disclosure).
- `assessment_status = "scope_revoked"` is emitted by the consent cascade but is not in `AssessmentStatus`. `AssessmentStatus`/`CueStatus` enums are defined but unused by the pipeline (plain strings).
- `data/schemas/` has no schemas for Assessment, Cue, Event, Consent, Clip or Passport. `coach_session.json` is an example payload with illustrative numbers, not a schema. `core.sql` `consents` table columns differ from the consent payload.
- `hip_rotation_rate` is labeled `deg/s` but computed in px/s; `eye_discipline_proxy` is labeled `deg^2` but computed in px². Slice 1 `extract_cues` labels `hip_height` as `deg` and `first_step_separation`/`asymmetry` as `ms`.
- `docs/film_first.md` gate lists surface / lighting / athlete diversity; `services/api/gates.py` checks only counts, inter-rater and disputes.
- `session_1.md` points at `pose_debug.mp4` and `calibration_debug.png`; code writes `pose_debug.json`, `calibration_debug.json`, `pose_confidence_heatmap.npy`.
- `session_1.md` / `session_1_report.md` "plausible bands" (shin 30–50°, hip height 0.75–0.95) have no source, and the hip-height band is inconsistent with the implemented ratio (hip-to-ankle over nose-to-ankle; a standing adult is near 0.5).
- README describes Slice 3/4 behaviour (scoring, NIL mapping) as present and lists no endpoints.
- MediaPipe adapter hard-codes fps = 60.

P2 — hygiene: unused imports, unsorted imports, unconfigured ruff, `make lint` swallows failures, tests write into the tracked tree.
