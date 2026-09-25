const QUEUE = [
  { clip_id: "clp_0001", position: "WR", movement: "release", status: "unlabeled" },
  { clip_id: "clp_0002", position: "DB", movement: "break", status: "unlabeled" },
];

export default function LabelQueue() {
  return (
    <main style={{ background: "#0B0F14", color: "#F4F1EA", minHeight: "100vh", padding: 32 }}>
      <h1>Label queue</h1>
      <p>golden_set: pending · target 10 WR + 10 DB</p>
      <ul>
        {QUEUE.map((row) => (
          <li key={row.clip_id}>
            <a href={`/label/${row.clip_id}`} style={{ color: "#F4F1EA" }}>
              {row.clip_id} {row.position} {row.movement} {row.status}
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}
