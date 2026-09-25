# Consent

Required before an assessment becomes shareable:

1. Athlete (or parent/guardian) accepts capture + processing.
2. Separate toggle for coach visibility.
3. Separate toggle for collective / recruiter API.
4. Separate toggle for public share cards.
5. Deepfake / authenticity scan disclosure.

## What the code stores today

Consent lives in `packages/consent/store.py`, exposed by `POST /consent` and
`POST /consent/{consent_id}/revoke` (`services/api/film.py`). There is no `services/api/consent.py`.

| Field (code) | Source | Notes |
| --- | --- | --- |
| `consent_id` | generated | `cns_` + hash |
| `athlete_id` | request | |
| `consent_scope` | request, list of strings | Free-form. Default `["capture", "coach"]`. `/passport` reads `capture`, `coach`, `public`. |
| `parent_attested` | request, bool | Recorded only. Nothing checks it. |
| `granted_at`, `revoked`, `revoked_at` | generated | |

## Form ↔ code mapping

| Paper form item (`consent_form_minor.md` / `consent_form_adult.md`) | Code field | Status |
| --- | --- | --- |
| Athlete name, parent/guardian name, signatures | — | Not stored (paper only). |
| Date of birth | — | **Not stored.** Without it the API cannot tell a minor from an adult. |
| ☐ Biomechanics analysis | `consent_scope` contains `capture` | Convention, not validated. |
| ☐ Coach review | `consent_scope` contains `coach` | Convention, not validated. |
| ☐ Improve the analysis system (unlabeled) | none agreed | **Open** — no scope string defined. |
| ☐ Public sharing (default NO) | `consent_scope` contains `public` | Convention, not validated. |
| Items 3–5 above (recruiter API, share cards, authenticity disclosure) | none | **Open** — not on either paper form, not in code. |
| "We delete video, measurements, reports within 30 days" | revoke purges clips, pose debug files, share links, and blanks assessments immediately; signed receipt with `deleted_counts` | In-memory store only; no object storage exists yet. |
| "Not kept longer than 90 days" (minor form) | — | **Not enforced.** `docs/legal/data_retention.md` defers enforcement to Slice 3. |

Parental consent for under-18s (`docs/legal/privacy.md`, `.env.example REQUIRE_PARENTAL_CONSENT_UNDER`)
is **not enforced** in code: the API has no age and does not require `parent_attested`. Owner and
decision: `docs/audit/open_questions.md`.
