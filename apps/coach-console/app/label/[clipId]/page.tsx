export default function LabelClip({ params }: { params: { clipId: string } }) {
  return (
    <main style={{ background: "#0B0F14", color: "#F4F1EA", minHeight: "100vh", padding: 16 }}>
      <h1>{params.clipId}</h1>
      <p>Three panes: video / events / six cues. Save is append-only. Cannot save without 5 events + 6 cues.</p>
    </main>
  );
}
