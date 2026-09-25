# Model card: nil_quantile_v0

- Task: informational NIL/recruiting band
- Intended outputs: p25 / p50 / p75 + assumptions + cluster IDs
- **Current outputs: p25 / p50 / p75 / confidence are `null`, `status: schema_only`.** There is no comp
  dataset; `data/samples/comp_clusters.json` holds placeholder cluster ids with null counts and
  quantiles. The API additionally returns `blocked_on_golden_set` while the golden-set gate is closed.
- Forbidden: point estimates as headlines; any number not traceable to a sourced comp row
  (`docs/rag-evidence.md`).
- Known failure modes: none measurable — no model exists yet.
