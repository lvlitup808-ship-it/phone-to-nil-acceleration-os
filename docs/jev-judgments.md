# Jev judgment layer

Source: TypeSafe Jev (Sep 2026) via @rvaniaaaa, @imryven, @0xcodila.

Jev does **not** write. It returns Choice / Score / Noul over a state blob.

SDK: `pip install typesafe-sdk`  
Env: `TYPESAFE_API_KEY`  
HTTP: `POST https://api.typesafe.ai/v1/systemone`

## Three-question test

A decision belongs to Jev only if all three are yes:

1. Can every valid answer be written down in advance?
2. Would a fast human glance settle it?
3. Does it happen often enough that milliseconds and fractions of a cent matter?

One no → keep it as code, a coach, or a generative model.

## Decisions in this product

| Decision | Type | Options / scale |
| --- | --- | --- |
| Clip usable? | noul | retake if below threshold |
| Lighting / angle / occlusion OK? | noul | quality gates |
| Suspected synthetic highlight? | noul | fraud flag |
| Position template | choice | wr_release, db_break, rb_first_cut, ol_first_step, edge, lb_scrape, qb_drop |
| Fix-this-first cue | choice | shin_angle, hip_height, gct, asymmetry, first_step |
| Cue severity | score | low / trainable / blocking |
| Evidence chunk useful? | noul | RAG filter |
| Answer grounded in comps? | noul | NIL verifier |
| Share-card safe to publish? | noul | consent + PII + disclaimer present |

## Thresholds

`JEV_ACCEPT_THRESHOLD` default `0.72`. Below threshold → fallback to heuristic or human coach. High confidence ≠ correctness.

## Pattern

Jev answers the fuzzy question. Ordinary code owns every branch after that. See `packages/judgment`.
