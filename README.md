# Phone-to-NIL Acceleration OS

Phone-video football acceleration biomechanics → position fit → drill prescription → re-test → NIL/recruiting valuation band.

Closed loop: **Capture → Assess → Prescribe → Train → Re-test → Verify → Value → Match**

This is not a 40-time app. The goal is to measure first-step mechanics, shin angle, hip height, ground-contact time, and position-specific movement cues, and later map the profile to a comparable recruiting / NIL **range**. No composite metric, ever.

## Status (what is real today)

- **Slice 1** (capture → assess → report) and **Slice 2** (WR release / DB break pose pipeline, 6 frozen cues each) run end to end on **synthetic fixture poses**. `/pose/assess` never sees real frames yet; its response says `pose_source: "fixture"`.
- **Golden set: pending.** No real, coach-labeled film exists. No accuracy (MAE) against coach labels is published; calibration error is unmeasured.
- **Gate closed.** Prescription, passport and NIL content return `status: "blocked_on_golden_set"` until `wr_labeled >= 10`, `db_labeled >= 10`, inter-rater done, disputes `<= 2`, and the surface / lighting / athlete mix in `docs/film_first.md` is met. Live state: `GET /gates/golden`.
- **NIL bands are schema placeholders.** p25/p50/p75 are `null`; there is no comp dataset.
- RTMPose is off (`POSE_ADAPTER` defaults to `mediapipe`, which falls back to fixtures if `mediapipe` is not installed).

## Solution

A phone-first OS with two extra layers most sports apps skip:

1. **Judgment (Jev / TypeSafe)** for bounded decisions — usable clip, position template, cue priority, synthetic-highlight risk, grounded claim. No prose.
2. **Evidence RAG** — Retrieve → Judge → Filter → Assemble → Generate → Verify — so drill copy and NIL narrative cannot float free of citations.

## Who pays

HS/college skill players, sprint-conversion football athletes, position coaches, small collectives. Not the NFL in v1.

## Quickstart

```bash
python3 -m pip install -e ".[dev]"
cp .env.example .env
uvicorn services.api.app:app --reload --port 8000
python -m pytest tests -q
```

OpenAPI: http://localhost:8000/docs

Golden-set harness (fixture mode, prints the honesty line): `python -m services.golden_set.harness`

## Endpoints

Every route below exists in `services/api/app.py` or `services/api/film.py`; `tests/test_docs_consistency.py` fails if this table and the app drift.

| Route | Slice | Behaviour today |
| --- | --- | --- |
| `GET /health` | 1 | Liveness |
| `POST /upload` | 1 | Ingest contract + clip-usable judgment; 422 with reasons on reject |
| `POST /assess` | 1 | Template cues (no measurement behind them unless `metrics` are passed) |
| `GET /report/{assessment_id}` | 1 | Stored assessment, after consent cascade |
| `GET /prescribe/{assessment_id}` | 1 | `blocked_on_golden_set`, `drills: []` while gate is closed; 403 if consent revoked |
| `POST /retest` | 1 | New assessment linked to the previous one |
| `GET /nil-band/{athlete_id}` | 1 | `blocked_on_golden_set`; p25/p50/p75 `null` |
| `GET /passport/{athlete_id}` | 1 | `blocked_on_golden_set`, `assessments: []`; `consent` is the athlete's active scopes |
| `POST /coach/annotate` | 1 | Append a coach note to an assessment |
| `GET /roster/{team_id}` | 1 | In-memory roster stub |
| `POST /pose/assess` | 2 | Six frozen cues for `release` / `break` on fixture poses, with `cue_status`, calibration mode, versions |
| `POST /ingest/check` | film-first | Capture contract + filename check; reason codes in `docs/film_first/retake_templates.md` |
| `POST /consent` | film-first | Grant consent scopes |
| `POST /consent/{consent_id}/revoke` | film-first | Revoke, purge covered clips / pose debug / share links, signed receipt |
| `POST /share-link` | film-first | Share link, TTL capped at 30 days |
| `POST /share-link/{token}/revoke` | film-first | Revoke a share link |
| `GET /golden/assignments` | film-first | `data/golden_set/assignments.json` |
| `GET /gates/golden` | film-first | Gate state derived from `data/golden_set/` |
| `GET /nil-band/{athlete_id}/scenarios` | film-first | `schema_only`, `scenarios: []` |
| `GET /position-fit/{athlete_id}` | film-first | `blocked_on_golden_set`, `clusters: []` |

Set `TYPESAFE_API_KEY` to use live Jev. Without it, heuristics keep CI green.

## Repo structure

```
apps/mobile                 Expo capture stub
apps/coach-console          Next.js roster / report
services/api                FastAPI
services/cv_worker          Pose adapters, calibration, events, WR/DB cues (Slice 2)
services/golden_set         Golden-set harness, inter-rater trigger
services/valuation          NIL band placeholder (no comp data; numbers are null)
packages/judgment           Jev client + fallback
packages/evidence           RAG evidence loop
packages/biomech            Cue extraction
data/samples                Templates, drills, comps
docs/legal                  Privacy, consent, NIL, bias
```

## NIL disclaimer

Ranges only, and none are computed yet: band numbers are `null` until a sourced comp dataset exists and the golden-set gate opens. Assumptions + `disclaimer_version` are on every payload. Not an offer. See `docs/legal/nil-disclaimer.md`.

## Attachments Incorporated

| Attachment | Where | Effect |
| --- | --- | --- |
| Build prompt | `PROMPT.md` | Repo contract |
| @imryven Jev builds | `docs/attachments/x-posts.md` | Judgment-only decisions |
| @rvaniaaaa Jev essay | `docs/jev-judgments.md` | Three-question test |
| @techyoutbe RAG essays | `docs/rag-evidence.md` | Evidence loop |
| @0xcodila Jev setup | `docs/attachments/x-posts.md` | Decision-density audit |
| Position templates | `data/samples/position_templates.json` | WR/DB/RB/OL |
| Drill library | `data/samples/drills.json` | Prescription seed |

License: Apache-2.0. Default branch `main`.
