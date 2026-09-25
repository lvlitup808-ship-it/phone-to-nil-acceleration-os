# Phone-to-NIL Acceleration OS

Phone-video football acceleration biomechanics → position fit → drill prescription → re-test → NIL/recruiting valuation band.

Closed loop: **Capture → Assess → Prescribe → Train → Re-test → Verify → Value → Match**

This is not a 40-time app. It scores first-step mechanics, shin angle, hip height, ground-contact time, and position-specific movement DNA, then maps the profile to a comparable recruiting / NIL **range**.

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

Set `TYPESAFE_API_KEY` to use live Jev. Without it, heuristics keep CI green.

## Repo structure

```
apps/mobile                 Expo capture stub
apps/coach-console          Next.js roster / report
services/api                FastAPI
services/cv_worker          Pose + event stub
services/valuation          Quantile NIL band
packages/judgment           Jev client + fallback
packages/evidence           RAG evidence loop
packages/biomech            Cue extraction
data/samples                Templates, drills, comps
docs/legal                  Privacy, consent, NIL, bias
```

## NIL disclaimer

Ranges only. Confidence + assumptions + `disclaimer_version` on every payload. Not an offer. See `docs/legal/nil-disclaimer.md`.

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
