# Contributing

1. Open an issue (`bug`, `feature`, `attachment`, `model`, or `legal`).
2. Branch from `main`: `feat/<slug>` or `fix/<slug>`.
3. NIL copy must stay a range + assumptions + disclaimer. Do not invent dollars: p25/p50/p75 stay null until the golden-set gate opens. No MAE and no composite.
4. Bounded decisions go through `packages/judgment`. Generation + RAG stay in `packages/evidence`.
5. Do not commit athlete video, PII, or API keys.
6. Claude Code sessions in this repo load the [Superpowers](https://github.com/obra/superpowers) plugin
   (`.claude/settings.json`). Its `verification-before-completion`, `test-driven-development` and
   `requesting-code-review` skills are the default way to work here: no "fixed" or "passing" claim
   without a fresh command run, and a regression test must fail with the fix reverted.
   Superpowers' brainstorming/planning flow does not override the film-first gate or `docs/product/cue_freeze_v1.md`.
