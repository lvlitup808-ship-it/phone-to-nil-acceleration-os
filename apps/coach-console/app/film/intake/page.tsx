export default function FilmIntake() {
  return (
    <main style={{ padding: 24, fontFamily: "ui-sans-serif", maxWidth: 640 }}>
      <h1>Film intake</h1>
      <p>Incomplete = upload blocked.</p>
      <form>
        <label>Athlete ID <input name="athlete_id" placeholder="ath____" required /></label>
        <label>Position target
          <select name="position_target" required>
            <option>WR</option>
            <option>DB</option>
          </select>
        </label>
        <label>Movement
          <select name="movement" required>
            <option>release</option>
            <option>break</option>
          </select>
        </label>
        <label>Height (cm) <input name="height_cm" type="number" required /></label>
        <label>Surface
          <select name="surface">
            <option>turf</option>
            <option>grass</option>
            <option>track</option>
          </select>
        </label>
        <label>Lighting
          <select name="lighting">
            <option>daylight</option>
            <option>night_lit</option>
            <option>indoor</option>
          </select>
        </label>
        <label>Side clip present <input type="checkbox" name="side_present" /></label>
        <label>Side duration / fps <input name="side_meta" /></label>
        <label>45 clip present <input type="checkbox" name="fortyfive_present" /></label>
        <label>45 duration / fps <input name="fortyfive_meta" /></label>
        <label>Consent id <input name="consent_id" placeholder="cns____" required /></label>
        <label>Filmer name <input name="filmer" required /></label>
        <label>
          <input type="checkbox" name="still_start" required />
          Athlete stood still 1 second at start
        </label>
        <button type="submit">Lock intake</button>
      </form>
    </main>
  );
}
