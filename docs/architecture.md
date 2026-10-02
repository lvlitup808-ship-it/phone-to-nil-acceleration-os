# Architecture

```
[Mobile Expo] --upload--> [API FastAPI] --queue--> [CV Worker]
                                |                       |
                                v                       v
                         [Judgment / Jev]         keypoints + events
                                |                       |
                                +---- biomech KPIs -----+
                                |
                                v
                    [Evidence RAG]  retrieve drills / comps / policy
                                |
                     Judge → Filter → Assemble
                                |
                    Generate (cue copy) → Verify grounding
                                |
                                v
                    [Valuation] quantile NIL / recruiting band
                                |
                     [Coach console]  [Athlete passport]
```

## Layers

1. Capture — quality gate before upload (Jev noul: usable clip?)
2. Perception — pose + event detection
3. Biomechanics — 3–5 prioritized cues
4. Decision — Jev choice/score for cue rank and position fit
5. Evidence — RAG over drills, comps, legal text
6. Valuation — ranges only. While the golden-set gate is closed the status is `blocked_on_golden_set` and p25/p50/p75 stay null. No MAE is published.
7. Distribution — share card, roster, collective API

## Data stores

PostgreSQL + pgvector, Redis queue, S3-compatible clip store.
