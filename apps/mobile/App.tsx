import { useState } from "react";
import { SafeAreaView, Text, Pressable, View, StyleSheet } from "react-native";

const API = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export default function App() {
  const [status, setStatus] = useState("Idle");
  const [report, setReport] = useState("");

  async function captureAndAssess() {
    setStatus("Uploading side + 45° stubs…");
    const athleteId = "athlete_demo";
    const clips = [];
    for (const angle of ["side", "fortyfive"]) {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          athlete_id: athleteId,
          angle,
          quality_score: 0.88,
          blur: 0.08,
          uri: `demo://${angle}.mp4`,
        }),
      });
      const json = await res.json();
      if (!res.ok) {
        setStatus(`Retake: ${json.detail?.retake_instructions ?? "quality gate"}`);
        return;
      }
      clips.push(json.clip_id);
    }
    const assess = await fetch(`${API}/assess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        clip_ids: clips,
        athlete_id: athleteId,
        template: "wr_release",
      }),
    });
    const body = await assess.json();
    setStatus("Assessed");
    setReport(JSON.stringify(body.cues?.slice(0, 3), null, 2));
  }

  return (
    <SafeAreaView style={styles.wrap}>
      <Text style={styles.title}>Acceleration OS</Text>
      <Text style={styles.sub}>Phone start → cues → NIL band</Text>
      <Pressable style={styles.btn} onPress={captureAndAssess}>
        <Text style={styles.btnText}>Capture start (demo)</Text>
      </Pressable>
      <Text style={styles.status}>{status}</Text>
      <View style={styles.card}>
        <Text style={styles.mono}>{report || "3–5 cues will land here. No metric dump."}</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: "#0B0F14", padding: 24 },
  title: { color: "#F4F1EA", fontSize: 28, fontWeight: "700" },
  sub: { color: "#9AA4B2", marginTop: 6, marginBottom: 24 },
  btn: { backgroundColor: "#E85D04", padding: 16, borderRadius: 12, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "700" },
  status: { color: "#F4F1EA", marginTop: 16 },
  card: { marginTop: 16, backgroundColor: "#151B23", padding: 16, borderRadius: 12 },
  mono: { color: "#C5D0DC", fontFamily: "Courier", fontSize: 12 },
});
