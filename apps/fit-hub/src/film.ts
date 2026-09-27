export type WorkItem = {
  n: string
  chip: string
  src: string
  tags: string[]
}

export const WORK: WorkItem[] = [
  { n: "01.", chip: "STANCE | FIRST STEP", src: "/film/stance.jpg", tags: ["FILM", "BIOMECH", "GATE"] },
  { n: "02.", chip: "POINT | SIGNAL", src: "/film/point.jpg", tags: ["FILM", "SIGNAL", "GATE"] },
  { n: "03.", chip: "TUNNEL | PACK", src: "/film/tunnel.jpg", tags: ["PACK", "FILM", "GATE"] },
  { n: "04.", chip: "LEAP | HASH", src: "/film/leap.jpg", tags: ["HASH", "FILM", "GATE"] },
  { n: "05.", chip: "BELT | AFTER", src: "/film/belt.jpg", tags: ["AFTER", "FILM", "GATE"] },
  { n: "06.", chip: "ROAR | RELEASE", src: "/film/roar.jpg", tags: ["RELEASE", "FILM", "GATE"] },
  { n: "07.", chip: "LOOK | RESET", src: "/film/look.jpg", tags: ["RESET", "FILM", "GATE"] },
]

export const STANCE = "/film/stance.jpg"
export const POINT = "/film/point.jpg"
