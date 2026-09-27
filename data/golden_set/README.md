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
| `athlete_height_cm` | number or `null` | Scale fallback when no yard lines are visible. The 185 / 183 on the two fixtures are made-up scale stand-ins for the synthetic pipeline; never copy them onto a real clip |
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

## Adding a filmed clip (one command)

```bash
python -m services.golden_set.add_clip \
  --athlete-id ath_0001 \
  --position WR \
  --movement release \
  --surface turf \
  --lighting daylight \
  --height-cm 183 \
  --side /path/to/side.mp4 --side-fps 60 \
  --fortyfive /path/to/45.mp4 --fortyfive-fps 60
```

- Copies the videos into `data/golden_set/clips/` (gitignored — raw athlete video is never committed).
- Appends a validated entry to `manifest.json` with `present: true` and the three diversity fields.
- Optional `--clip-id clp_NNNN` (default: next free id). `--dry-run` prints without writing.
- Then run `python -m services.golden_set.manifest` (or `make lint`) to confirm.
- Coach labels go in `labels/`, one file per coach per clip, each with a `coach_id`.
