# Audit post-repair — 2026-09-25

Re-ran every Step 1 check on the repair branch (`claude/audit-repair-phone-to-nil-fwxhss`). Compare with
[`baseline.md`](baseline.md). Open items: [`open_questions.md`](open_questions.md).

No validation numbers were fabricated in this pass.

## Before / after

| Check | Baseline (`main` @ 373a48a) | Post-repair |
| --- | --- | --- |
| `pip install -e ".[dev]"` | ok | ok (also from a fresh `git clone` into a new venv; that venv reused already-installed system packages, so dependency downloads were not re-tested) |
| CI on PR #12 (head `6d719c6`) | — | `python`, `check`, `docker` all green |
| `pytest tests -q` | 22 passed, **1 failed** (23 tests) | **66 passed, 0 failed** (58 after the repair pass + 8 from the review round) |
| Working tree after tests | dirty (`slice2_report.md` rewritten, `artifacts/` created) | clean |
| `ruff check` | 29 findings, unconfigured rules, `make lint` ignores failures | 0 findings with the pinned rule set; `make lint` and CI fail on findings. With ruff 0.16.9's unconfigured defaults (`--isolated`) 14 stylistic findings remain, mostly BLE001 on the intentional adapter/Jev fallbacks |
| `mypy services packages` | not configured; ad hoc run clean (48 files) | configured, in `make lint` and CI; clean (52 files) |
| API start, `/health`, `/docs` | 200 / 200 | 200 / 200 |
| Any 500 on fixture input | none | none |
| `/pose/assess` with `clip_id="../../tmp/x"` | 200, wrote files outside the repo | 422, nothing written |
| `/prescribe/{id}` | drills returned, gate ignored | `blocked_on_golden_set`, `drills: []` |
| `/nil-band/{id}` | p25/p50/p75 = 2500/6000/14000, confidence 0.41 (invented) | `blocked_on_golden_set`, all numbers `null` |
| `/passport/{id}` | assessments + hard-coded consent `true` | `blocked_on_golden_set`, consent looked up |
| `/gates/golden` | hard-coded zeros | derived from `data/golden_set/`; still 0/10, 0/10 (true state) |
| Golden harness | test only; wrote a tracked file; printed nothing | `python -m services.golden_set.harness` prints `golden_set: pending` and "Do not treat this as athlete validation." |
| Docker image build | not run | passes in CI (`docker` job on PR #12, head `6d719c6`); not run locally (no Docker daemon here) |

## Gates and disciplines

- Golden-set gate: unchanged thresholds (`wr ≥ 10`, `db ≥ 10`, inter-rater done, disputes ≤ 2), plus the
  `docs/film_first.md` mix (3 surfaces, 2 lighting, 3 athletes/position). Only stricter. Needs product
  sign-off (open question 20).
- `POSE_ADAPTER` default is still `mediapipe`; RTMPose still off and still raises.
- The 12 frozen cues are unchanged in name and order; a test now pins `cue_freeze_v1.md` to both extractors.
- No composite metric added. The lint that bans composite identifiers now passes and also scans `.json`.
- No Slice 3 surface added: no prescription output, passport content, NIL numbers, or position-fit labels.
- Consent, retention, and minors-mode logic: nothing removed. Revocation now does more (it deletes).

## Every file changed, and why

Code

| File | Why |
| --- | --- |
| `services/api/app.py` | `clip_id` path-traversal guard + `ARTIFACTS_DIR`; gate on `/prescribe`, `/passport`, `/nil-band`; passport consent looked up; consent-revoke purger for clips and pose debug |
| `services/api/film.py` | `/gates/golden` serves `gate_state()`; share links revoked on consent revoke; B904 |
| `services/api/gates.py` | Progress derived from `data/golden_set/` (real film only); diversity conditions; `gate_state()` |
| `services/valuation/engine.py` | Removed invented band tables, confidence and counterfactuals; nulls + `status: schema_only` |
| `services/valuation/app.py` | Return type hint |
| `packages/shared/models.py` | `NILBand` numbers nullable, `status` added (additive) |
| `packages/shared/slice2.py` | `scope_revoked` in `AssessmentStatus`; `Slice2Event`, `Slice2Assessment` payload models |
| `packages/shared/schemas.py` | New: generate / drift-check `data/schemas/*.schema.json` |
| `packages/consent/store.py` | `active_scopes()`; purgers run on revoke; `deleted_counts` in receipt; enum status |
| `packages/biomech/features.py` | Explicit Slice 1 unit table (hip_height was `deg`, first_step_separation `ms`) |
| `packages/capture/contract.py` | Flattened nested `if`; behaviour checked exhaustively unchanged |
| `packages/judgment/log.py` | `datetime.UTC` (lint) |
| `services/cv_worker/features/common.py` | `angle_from_vertical` clamp bug; `envelope` validates `CueStatus`; type hints |
| `services/cv_worker/features/wr_release.py` | No invented 170 ms GCT; type hints |
| `services/cv_worker/features/db_break.py` | No invented 180 ms recovery step; units px/s and px²; type hints |
| `services/cv_worker/pipeline_v2.py` | No synthetic fallback on real frames (→ `error`); `pose_source`; `fps` threaded; type hints |
| `services/cv_worker/confidence.py` | `rollup` uses the enums; type hints |
| `services/cv_worker/pose/mediapipe_adapter.py` | `fps` parameter instead of hard-coded 60 |
| `services/cv_worker/pose/factory.py`, `calibration/resolve.py`, `calibration/field_line.py`, `events/detector.py`, `pose/fixture_adapter.py` | Type hints, unused imports, lint |
| `services/golden_set/harness.py` | New harness entry point with honesty line |
| `services/golden_set/inter_rater.py` | SIM103 (same behaviour, tested) |
| `services/golden_set/__init__.py`, `services/cv_worker/ingest/__init__.py` | Make them regular packages |

Tests

| File | Why |
| --- | --- |
| `tests/lint/test_no_score_word.py` | Stop self-matching; function renamed to what it checks; scan `.json` |
| `tests/golden/test_pose_pipeline.py` | Harness tests print the honesty line and write to tmp; committed report must equal harness output; traversal test |
| `tests/test_health_and_loop.py` | Replaced assertions on invented NIL numbers with assertions of their absence and of the gate |
| `tests/test_gates.py` | New: gate derivation (fixtures never count), every condition required, blocked routes, passport consent, prescribe opens only with the gate |
| `tests/test_cue_math.py` | New: angle geometry, no invented GCT / recovery values, units |
| `tests/test_status_enums.py` | New: one status vocabulary; fixture runs labelled; adapter failure → `error` |
| `tests/test_film_first.py` | Revocation deletes what the receipt lists |
| `tests/test_docs_consistency.py` | New: retake codes ↔ validator, cue freeze ↔ extractors, README ↔ OpenAPI |
| `tests/test_schemas.py` | New: committed schemas ↔ models, payloads validate |
| `tests/conftest.py` | New: test artifacts go to tmp |

Config / data

| File | Why |
| --- | --- |
| `pyproject.toml` | Pinned ruff rules; mypy config; `mypy` in dev extras |
| `Makefile` | `lint` fails on findings, runs mypy + schema check; `golden` target |
| `.github/workflows/ci.yml` | Runs ruff, mypy, schema drift check |
| `.github/workflows/golden-nightly.yml` | Runs the harness |
| `.gitignore` | `artifacts/` |
| `data/samples/comp_clusters.json` | Invented `n` and dollar quantiles → `null`, `status: placeholder` |
| `data/schemas/*.schema.json` (5 new) | Generated from the models the API emits |
| `data/schemas/coach_session.json` | Labelled as an illustrative example, not real data |
| `data/schemas/core.sql` | Header: not wired, known drift listed (no DDL change) |

## Every doc updated, and what changed

| Doc | Change |
| --- | --- |
| `README.md` | Removed "scores… maps to NIL range" as present-tense; added status section and full endpoint table (test-enforced) |
| `docs/film_first/retake_templates.md` | Headings are the validator's real codes; `bad_filename` added; `no_field_lines` reclassified as a calibration downgrade; 4–12 s stated |
| `docs/film_first/session_1.md` | Debug file names match what the code writes; shin / hip bands marked `unverified` |
| `docs/validation/session_1_report.md` | Same; bands removed from the form |
| `docs/validation/slice2_report.md` | Now generated by the harness |
| `docs/film_first/schedule.md` | Ingest pass-rate guess marked `unverified` |
| `docs/film_first.md` | Points at the enforced gate and the manifest fields it reads |
| `docs/legal/consent.md` | Form ↔ code mapping; gaps stated (DOB, parental attestation, scope vocabulary, retention) |
| `docs/models/mediapipe_v1.md`, `docs/models/rtmpose_v1.md` | Known failure modes, current status |
| `models/model_cards/nil_quantile_v0.md`, `pose_phone_v0.md` | Current outputs / evidence stated (none) |
| `docs/audit/*` | New: baseline, post-repair, open questions |

## Claims marked `unverified`

- Shin-angle sanity band 30–50° and hip-height band 0.75–0.95 (`session_1.md`, `session_1_report.md`) — no source; hip band conflicts with the formula.
- Session 1 ingest pass-rate "6–8" (`schedule.md`) — planning guess, no data.
- GCT heuristic factor 0.45 and 90 ms floor — no source (open question 5).
- `apps/` (Next.js / Expo) — not built or type-checked.
- MediaPipe on real frames — never exercised (no `mediapipe`, no film).

Not marked `unverified` because they are stated as targets, not results: `ICC > 0.8`, capture success
`> 85%` (`docs/ml.md`, `pose_phone_v0.md`).

## P3 items left open

All 29 are in [`open_questions.md`](open_questions.md) with an owner and a blocking reason. The ones a
human must decide before merge are 20 (stricter gate), 21 (blocked routes now return null / empty
values in Slice 1 keys) and 25 (`/pose/assess` rejects unknown / revoked consent ids).

## What was not verified

- Frontend apps.
- Any behaviour on real film: there is none in the repo.
- The shin / lean angle fix is verified on synthetic geometry only (unit tests with known segments), not on film.

No validation numbers were fabricated in this pass.

## Red-green check (Superpowers `verification-before-completion`)

For each fix, the source file(s) were reset to `main` while keeping the new test, the test was run, then
the fix was restored and the test re-run. All 13 went red with the fix reverted and green with it restored.

| Fix | Test | Reverted | Restored |
| --- | --- | --- | --- |
| Angle clamp | `test_cue_math.py::test_angle_from_vertical_is_symmetric_in_image_y` | fail | pass |
| Invented GCT | `test_cue_math.py::test_gct_is_not_invented_without_a_second_step` | fail | pass |
| Invented recovery step | `test_cue_math.py::test_recovery_step_is_not_invented_when_order_is_wrong` | fail | pass |
| NIL numbers | `test_health_and_loop.py::test_valuation_emits_no_invented_numbers` | fail | pass |
| Gate derived from data | `test_gates.py::test_real_labels_count_and_inter_rater` | fail | pass |
| Units | `test_cue_math.py::test_units_match_what_is_computed` | fail | pass |
| Retake codes | `test_docs_consistency.py::test_retake_packet_codes_match_validator` | fail | pass |
| README routes | `test_docs_consistency.py::test_readme_endpoints_exist` | fail | pass |
| Lint self-match | `tests/lint` | fail | pass |
| Path traversal | `test_pose_pipeline.py::test_pose_api_rejects_path_traversal` | fail | pass |
| Passport consent | `test_gates.py::test_passport_consent_is_looked_up_not_asserted` | fail | pass |
| No synthetic fallback | `test_status_enums.py::test_adapter_failure_on_real_frames_is_error_not_synthetic` | fail | pass |
| Consent purge | `test_film_first.py::test_revoke_actually_deletes_what_the_receipt_lists` | fail (purgers disabled; a whole-file revert breaks imports, so it was checked this way) | pass |

## Review round (Superpowers `requesting-code-review`)

An independent reviewer subagent reviewed `373a48a..82390cb` with the Superpowers reviewer template.
Verdict: "With fixes". No critical issues. Every finding below was reproduced with a failing test first
(`tests/test_review_fixes.py`, 7 red before the fix), then fixed.

| Finding | Severity | Outcome |
| --- | --- | --- |
| `/pose/assess` with a revoked consent still wrote pose-debug files that nothing deleted | Important | Fixed: consent is checked before the pipeline runs; revoked → 403, unknown → 404 |
| GCT clamped to a 90 ms floor and reported as `ok` (an invented value) | Important | Fixed: below the floor → `null`, `insufficient_data` |
| Revocation missed an athlete's clips uploaded without `consent_id` | Important | Fixed: those clips are purged too; policy question logged (#26) |
| `/prescribe` would 500 on an assessment with no cues once the gate opens | Minor | Fixed |
| Harness hard-coded `source=fixture` | Minor | Fixed: prints the pipeline's `pose_source` (output unchanged today) |
| Labels without `coach_id` counted as a distinct coach | Minor | Fixed: ignored |
| Manifest film paths could point outside `data/golden_set/` | Minor | Fixed: must resolve inside it |
| Valuation service does not report the gate | Minor | Open (#27) |
| `pose_error` exposes exception text | Minor | Open (#28) |
| Slice 1 `stride_frequency` / `deceleration` units are assumptions | Minor | Open (#29) |

No validation numbers were fabricated in this pass.
