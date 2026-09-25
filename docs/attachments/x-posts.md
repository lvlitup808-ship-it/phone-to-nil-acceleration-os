# X posts incorporated

## Jev / TypeSafe — judgment, not generation

- https://x.com/imryven/status/2102833122198843579
  What people built with Jev: none of the flagship demos generate prose. Each returns a number against a predefined answer. That is the pattern for capture QA, cue ranking, fraud flags, and grounding checks.

- https://x.com/rvaniaaaa/status/2101709732314558639
  Jev launched 2026-09-15. Vocabulary is Choice / Score / Noul. Three-question test before any call. Code owns branches after the judgment. Thresholds exist because confidence ≠ correctness.

- https://x.com/0xcodila/status/2102805532960542928
  Decision-density audit: find every pause that is a classification wearing a paragraph. Wire those to Jev. Keep generation for cue language and athlete-facing copy only.

Implementation: `packages/judgment/client.py`, `docs/jev-judgments.md`.

## Production RAG as an evidence pipeline

- https://x.com/techyoutbe/status/2103123038342684948
- https://x.com/techyoutbe/status/2103131819818565702

Loop is Retrieve → Judge → Filter → Assemble → Generate → Verify, with a rewrite path on failed grounding. Applied to drills, comps, and NIL claims.

Implementation: `packages/evidence/pipeline.py`, `docs/rag-evidence.md`.
