export type WorkItem = {
  n: string
  chip: string
  title: string
  src: string
  tags: string[]
}

export const WORK: WorkItem[] = [
  { n: "01.", chip: "STANCE | FIRST STEP", title: "Stance", src: "/film/stance.jpg", tags: ["FILM", "BIOMECH", "GATE"] },
  { n: "02.", chip: "POINT | SIGNAL", title: "Point", src: "/film/point.jpg", tags: ["FILM", "SIGNAL", "GATE"] },
  { n: "03.", chip: "TUNNEL | PACK", title: "Tunnel", src: "/film/tunnel.jpg", tags: ["PACK", "PRE", "FILM"] },
  { n: "04.", chip: "LEAP | HASH", title: "Leap", src: "/film/leap.jpg", tags: ["HASH", "FILM", "GATE"] },
  { n: "05.", chip: "BELT | AFTER", title: "Belt", src: "/film/belt.jpg", tags: ["AFTER", "FILM"] },
  { n: "06.", chip: "ROAR | RELEASE", title: "Roar", src: "/film/roar.jpg", tags: ["RELEASE", "FILM"] },
  { n: "07.", chip: "LOOK | RESET", title: "Look", src: "/film/look.jpg", tags: ["RESET", "FILM"] },
]

export const PILLARS = [
  {
    title: "Film intake",
    body: "Surface, lighting, and athlete_id belong on every filmed clip or the manifest check fails. Consent is a separate step and is not part of that check.",
    tags: ["TURF / GRASS / TRACK", "DAYLIGHT / NIGHT / INDOOR"],
  },
  {
    title: "Cue freeze",
    body: "Twelve frozen cues. Fixture poses until the golden set opens. Report cue names, not a grade.",
    tags: ["SHIN", "GCT", "HIP", "RELEASE", "BREAK"],
  },
  {
    title: "Closed loop",
    body: "Capture → assess → prescribe → re-test. Drills stay empty while the gate is closed.",
    tags: ["INGEST", "ASSESS", "RE-TEST"],
  },
  {
    title: "Value later",
    body: "NIL bands stay null. Schema only. No composite, no p50, no Saturday dollar.",
    tags: ["NO COMPOSITE", "NO P50"],
  },
]
