# Film first

The bottleneck is not code. It is **20 consented, coach-labeled clips**.

Do not start Slice 3 while the golden set is pending.

1. Consent 3 WR + 3 DB athletes (minors: parent on the form).
2. Shoot side + 45, 5-10s, 30fps+, phone still for the first half-second.
3. Assign each clip to a coach with a due date.
4. Label in /label/[clipId]. Protocol version stamped on every save.

Slice 3 gate: 10 WR + 10 DB, 3 surfaces, 2 lighting, 3 athletes/position, 2 coaches on 4 clips.

The gate is enforced in `services/api/gates.py` and served on `GET /gates/golden`. It also requires disputed clips <= 2. Only labels on clips with real film on disk count; fixture manifest entries never do. Surface, lighting and athlete counts are read from the manifest fields `surface`, `lighting`, `athlete_id`, which the intake form collects. A clip with film present must record all three, or `python -m services.golden_set.manifest` (run by `make lint` and CI) rejects it. Field reference: `data/golden_set/README.md`.
