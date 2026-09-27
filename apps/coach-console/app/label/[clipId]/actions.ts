"use server";

import { redirect } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function num(v: FormDataEntryValue | null): number | null {
  const s = String(v ?? "").trim();
  return s === "" ? null : Number(s);
}

export async function saveLabel(formData: FormData) {
  const clipId = String(formData.get("clip_id"));
  const events = String(formData.get("event_names") ?? "").split(",").filter(Boolean);
  const cues = String(formData.get("cue_names") ?? "").split(",").filter(Boolean);
  const excluded = formData.get("excluded") === "on";
  const body = {
    clip_id: clipId,
    coach_id: String(formData.get("coach_id") ?? "").trim(),
    excluded,
    disputed: formData.get("disputed") === "on",
    notes: String(formData.get("notes") ?? ""),
    events: excluded
      ? {}
      : Object.fromEntries(events.map((e) => [e, { t_ms: num(formData.get(`event_${e}`)) }])),
    cues: excluded
      ? {}
      : Object.fromEntries(
          cues.map((c) => [c, { value: num(formData.get(`cue_${c}`)), disputed: formData.get(`disputed_${c}`) === "on" }]),
        ),
  };
  let status: string;
  try {
    const res = await fetch(`${API}/golden/labels`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const out = await res.json();
    status = res.ok ? `saved ${out.path}` : `not saved (${res.status}): ${JSON.stringify(out.detail)}`;
  } catch {
    status = "not saved: API unreachable";
  }
  redirect(`/label/${encodeURIComponent(clipId)}?status=${encodeURIComponent(status)}`);
}
