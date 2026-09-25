from __future__ import annotations

from packages.shared.models import Cue, CueId, PositionTemplate

TEMPLATES = {
    PositionTemplate.wr_release: [CueId.shin_angle, CueId.first_step_separation, CueId.hip_height],
    PositionTemplate.db_break: [CueId.deceleration, CueId.hip_height, CueId.asymmetry],
    PositionTemplate.rb_first_cut: [CueId.shin_angle, CueId.deceleration, CueId.ground_contact_time],
    PositionTemplate.ol_first_step: [CueId.shin_angle, CueId.hip_height, CueId.ground_contact_time],
}

UNITS = {
    CueId.shin_angle: "deg",
    CueId.hip_height: "ratio",
    CueId.ground_contact_time: "ms",
    CueId.first_step_separation: "yd",
    CueId.asymmetry: "ratio",
    CueId.stride_frequency: "Hz",
    CueId.deceleration: "ms",
}

NOTES = {
    CueId.shin_angle: "Shin too vertical off the line. Push the track angle on step one.",
    CueId.hip_height: "Hips rise early. Stay in the acceleration posture one extra step.",
    CueId.ground_contact_time: "Contact is long. Cue stiff ankle and faster punch.",
    CueId.first_step_separation: "First step is under the hip. Project the shin and finish the push.",
    CueId.asymmetry: "Left/right split is noisy. Film both sides before loading volume.",
    CueId.stride_frequency: "Frequency drops after step three. Keep the rhythm through 10 yards.",
    CueId.deceleration: "Brake is late. Shorten the last approach step before the cut.",
}


def extract_cues(template: PositionTemplate, metrics: dict[str, float] | None = None) -> list[Cue]:
    metrics = metrics or {}
    ordered = TEMPLATES.get(template, list(CueId)[:4])
    cues: list[Cue] = []
    for i, cue_id in enumerate(ordered[:5], start=1):
        cues.append(
            Cue(
                id=cue_id,
                value=metrics.get(cue_id.value),
                unit=UNITS[cue_id],
                confidence=0.62 if cue_id.value in metrics else 0.45,
                priority=i,
                trainability=0.8 if cue_id != CueId.asymmetry else 0.5,
                note=NOTES[cue_id],
            )
        )
    return cues
