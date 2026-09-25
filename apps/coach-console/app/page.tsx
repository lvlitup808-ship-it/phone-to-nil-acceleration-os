const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function loadRoster() {
  try {
    const res = await fetch(`${API}/roster/team_demo`, { cache: "no-store" });
    return await res.json();
  } catch {
    return { id: "team_demo", athletes: [], offline: true };
  }
}

export default async function Page() {
  const roster = await loadRoster();
  return (
    <main style={{ fontFamily: "Georgia, serif", background: "#0B0F14", color: "#F4F1EA", minHeight: "100vh", padding: 40 }}>
      <p style={{ letterSpacing: 3, color: "#E85D04", fontSize: 12 }}>COACH CONSOLE</p>
      <h1>Roster / reports</h1>
      <p style={{ color: "#9AA4B2" }}>Annotate cues. Compare starts. Do not publish NIL point estimates.</p>
      <section style={{ marginTop: 24, background: "#151B23", padding: 20, borderRadius: 12 }}>
        <h2>Team {roster.id}</h2>
        <pre>{JSON.stringify(roster, null, 2)}</pre>
      </section>
    </main>
  );
}
