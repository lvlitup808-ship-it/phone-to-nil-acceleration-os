# Golden set

`manifest.json` lists every golden-set clip. The model is `packages/shared/golden.py`, the generated
schema is `data/schemas/golden_manifest.schema.json`, and the file is checked by:

```bash
python -m services.golden_set.manifest
```

`make lint` and CI run that check, so a malformed manifest fails the build.

## Clip fields

| Field | Values | Notes |
| --- | --- | --- |
| `clip_id` | `clp_0000`–`clp_9999` | Unique within the manifest |
| `athlete_id` | `ath_0000`–`ath_9999` or `null` | Same id as the clip file name (`services/cv_worker/ingest/naming.py`). Never a real name |
| `position_target` | `WR`, `DB` | |
| `movement` | `release`, `break` | |
| `surface` | `turf`, `grass`, `track` or `null` | From the film intake form |
| `lighting` | `daylight`, `night_lit`, `indoor` or `null` | From the film intake form |
| `athlete_height_cm` | number or `null` | Scale fallback when no yard lines are visible |
| `camera_side`, `camera_45` | `{path, fps, present}` | `path` is relative to `data/golden_set/`. `present: true` only when the file is really there |
| `disputed` | `true` / `false` | Disputed clips are excluded from the gate and from MAE |
| `labels` | object | Fixture labels only; coach labels go in `labels/<clip_id>*.json` |

Unknown field names are rejected (a typo like `lightning` fails the check).

## Rule: filmed clips must record athlete, surface, lighting

If either camera has `present: true`, then `athlete_id`, `surface` and `lighting` must be filled in.
The golden-set gate (`services/api/gates.py`, `GET /gates/golden`) counts distinct surfaces (needs 3),
lighting conditions (needs 2) and athletes per position (needs 3) from these fields. A filmed clip
without them would silently not count, so the check refuses it instead.

Clips with no film (the two fixtures, `clp_0001` and `clp_0002`) keep these fields as `null`. Do not
fill them with guesses; they describe film that does not exist.

## Adding a filmed clip

1. Put the files in `clips/`. `*.mp4` is gitignored, so raw athlete video is never committed.
2. Add an entry with `present: true` and the three fields copied from the intake form.
3. Run `python -m services.golden_set.manifest`.
4. Coach labels go in `labels/`, one file per coach per clip, each with a `coach_id`.
