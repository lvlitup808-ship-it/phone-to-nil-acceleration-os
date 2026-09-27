import { saveLabel } from "./actions";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Spec = {
  clip_id: string;
  position_target: string;
  movement: string;
  events: string[];
  cues: string[];
  labeling_protocol_version: string | null;
};

async function loadSpec(clipId: string): Promise<Spec | { error: string }> {
  try {
    const res = await fetch(`${API}/golden/labels/${encodeURIComponent(clipId)}/spec`, { cache: "no-store" });
    if (!res.ok) return { error: (await res.json()).detail ?? `HTTP ${res.status}` };
    return await res.json();
  } catch {
    return { error: "API unreachable" };
  }
}

const page = { background: "#0B0F14", color: "#F4F1EA", minHeight: "100vh", padding: 16 } as const;
const row = { display: "flex", gap: 12, alignItems: "center", margin: "6px 0" } as const;

export default async function LabelClip({
  params,
  searchParams,
}: {
  params: { clipId: string };
  searchParams: { status?: string };
}) {
  const spec = await loadSpec(params.clipId);
  if ("error" in spec) {
    return (
      <main style={page}>
        <h1>{params.clipId}</h1>
        <p>Cannot label: {spec.error}</p>
      </main>
    );
  }
  return (
    <main style={page}>
      <h1>
        {spec.clip_id} · {spec.position_target} {spec.movement}
      </h1>
      <p>
        Save is append-only: one label per coach per clip. All {spec.events.length} events and {spec.cues.length} cues
        are required. Unsure on a cue? Leave it blank and mark it disputed. Protocol {spec.labeling_protocol_version}.
      </p>
      {searchParams.status && <p role="status">{searchParams.status}</p>}
      <form action={saveLabel}>
        <input type="hidden" name="clip_id" value={spec.clip_id} />
        <input type="hidden" name="event_names" value={spec.events.join(",")} />
        <input type="hidden" name="cue_names" value={spec.cues.join(",")} />
        <label style={row}>
          coach_id <input name="coach_id" required pattern="coach_[a-z0-9]{1,32}" placeholder="coach_ab" />
        </label>
        <fieldset>
          <legend>Events (ms from clip start)</legend>
          {spec.events.map((e) => (
            <label key={e} style={row}>
              {e} <input name={`event_${e}`} type="number" min={0} step={1} />
            </label>
          ))}
        </fieldset>
        <fieldset>
          <legend>Cues</legend>
          {spec.cues.map((c) => (
            <label key={c} style={row}>
              {c} <input name={`cue_${c}`} type="number" step="any" />
              <input type="checkbox" name={`disputed_${c}`} /> disputed
            </label>
          ))}
        </fieldset>
        <label style={row}>
          <input type="checkbox" name="disputed" /> Whole clip disputed
        </label>
        <label style={row}>
          <input type="checkbox" name="excluded" /> cannot_label (occluded, dark, wrong angle)
        </label>
        <label style={row}>
          notes <textarea name="notes" maxLength={2000} />
        </label>
        <button type="submit">Save label</button>
      </form>
    </main>
  );
}
