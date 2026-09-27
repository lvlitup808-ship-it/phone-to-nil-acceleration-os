import { useEffect, useState } from "react";
import { WORK, PILLARS } from "./film";

function FilmPlate({ src, alt }: { src: string; alt: string }) {
  const [ok, setOk] = useState(true);
  return (
    <div className="relative overflow-hidden rounded-[24px] bg-neutral-950 aspect-[16/10] w-full max-w-[720px]">
      {ok ? (
        <img
          src={src}
          alt={alt}
          className="absolute inset-0 h-full w-full object-cover"
          onError={() => setOk(false)}
        />
      ) : (
        <div className="absolute inset-0 grid place-items-center border border-[var(--color-line)] font-mono text-[10px] tracking-[0.18em] text-[var(--color-mute)]">
          FILM PENDING
        </div>
      )}
    </div>
  );
}

function Intro({ onDone }: { onDone: () => void }) {
  const [phase, setPhase] = useState<"word" | "reel">("word");
  const [leaving, setLeaving] = useState(false);

  useEffect(() => {
    const a = window.setTimeout(() => setPhase("reel"), 900);
    const b = window.setTimeout(() => finish(), 4200);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" || e.key === "Enter") finish();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.clearTimeout(a);
      window.clearTimeout(b);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  function finish() {
    setLeaving(true);
    window.setTimeout(onDone, 560);
  }

  return (
    <div className={`fixed inset-0 z-50 ${leaving ? "intro-leave" : ""}`} onClick={finish}>
      {phase === "word" ? (
        <div className="flex h-full items-center justify-center bg-white text-black">
          <p className="font-display text-[clamp(2.5rem,8vw,6rem)] font-semibold tracking-tight">
            20
            <span className="relative -top-1 mx-0.5 inline-block h-[0.18em] w-[0.18em] rounded-full bg-black align-middle" />
            HUB
          </p>
        </div>
      ) : (
        <div className="relative flex h-full flex-col items-center justify-center bg-[#e8e8e8] text-black">
          <p className="absolute top-10 font-mono text-[11px] tracking-[0.2em] text-neutral-500">04;47</p>
          <p
            className="pointer-events-none absolute inset-x-0 text-center font-display text-[clamp(4.5rem,22vw,16rem)] font-bold leading-none text-transparent"
            style={{ WebkitTextStroke: "6px #111" }}
          >
            STANCE
          </p>
          <div className="relative z-10 size-[min(70vw,70vh)] overflow-hidden rounded-full bg-neutral-300">
            <img
              src="/film/stance.jpg"
              alt=""
              className="h-full w-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
            <span className="absolute inset-0 grid place-items-center font-body text-sm font-medium text-white drop-shadow">
              Fit Hub
            </span>
          </div>
          <p className="absolute bottom-10 font-mono text-[11px] tracking-[0.2em] text-neutral-500">10-YD</p>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [intro, setIntro] = useState(true);

  return (
    <div className="min-h-screen bg-black text-[#eee]">
      {intro && <Intro onDone={() => setIntro(false)} />}

      <header className="fixed inset-x-0 top-0 z-40 flex items-center justify-between px-6 py-5 md:px-10">
        <a href="#top" className="font-display text-sm font-semibold tracking-tight">
          FIT HUB
        </a>
        <nav className="flex gap-6 font-mono text-[11px] tracking-[0.16em] text-[var(--color-mute)]">
          <a href="#work" className="hover:text-[#eee]">
            WORK
          </a>
          <a href="#lab" className="hover:text-[#eee]">
            LAB
          </a>
          <a href="#contact" className="hover:text-[#eee]">
            CONTACT
          </a>
        </nav>
      </header>

      <main id="top">
        <section className="grid min-h-screen grid-cols-1 items-end gap-16 px-6 pb-24 pt-28 md:grid-cols-[1.2fr_0.8fr] md:px-10 md:pt-36">
          <h1 className="stack-head text-[clamp(2.6rem,7vw,5.6rem)]">
            {"WE\nFILM\nTHE\nFIRST\nSTEP\nTHEN\nWE\nRUN\nIT\nAGAIN".split("\n").map((w, i) => (
              <span key={`${w}-${i}`} className="block">
                {w}
              </span>
            ))}
          </h1>
          <p className="max-w-sm justify-self-start font-body text-[13px] font-light leading-6 text-[var(--color-mute)] md:justify-self-end md:text-right">
            A PERFORMANCE LAB FOR FOOTBALL-TO-SPRINT ATHLETES. PHONE FILM. STANCE. SHIN. DRIVE. RE-TEST. NO COMPOSITE
            SCORE. NO MADE-UP NIL BAND. WORK FROM THE HASH MARK OUT.
          </p>
        </section>

        <section id="work" className="px-6 md:px-10">
          <p className="font-mono text-[10px] tracking-[0.2em] text-[var(--color-mute)]">FEATURED WORK</p>
          <div className="mt-6 grid gap-10 md:grid-cols-[1.4fr_0.6fr] md:items-start">
            <h2 className="stack-head text-[clamp(1.6rem,3.4vw,2.6rem)]">
              SMART, VIOLENT, AND A LITTLE PATIENT.
              <br />
              BECAUSE SPEED DOES NOT GUESS.
            </h2>
            <p className="max-w-xs font-body text-[13px] font-light leading-6 text-[var(--color-mute)] md:justify-self-end md:text-right">
              From stance film to tunnel walk to the point. Work people remember on Saturday.
            </p>
          </div>

          <div className="mt-16">
            {WORK.map((item) => (
              <article key={item.n} className="border-t border-[var(--color-line)] py-10">
                <div className="grid items-center gap-6 md:grid-cols-[auto_1fr_minmax(0,720px)_auto]">
                  <span className="font-mono text-[11px] text-[var(--color-mute)]">{item.n}</span>
                  <span className="w-fit bg-white px-2 py-0.5 font-mono text-[10px] tracking-[0.08em] text-black">
                    {item.chip}
                  </span>
                  <FilmPlate src={item.src} alt={item.title} />
                  <ul className="hidden text-right font-mono text-[10px] tracking-[0.16em] text-[var(--color-mute)] md:block">
                    {item.tags.map((t) => (
                      <li key={t}>{t}</li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section id="lab" className="px-6 py-28 md:px-10">
          <p className="font-mono text-[10px] tracking-[0.2em] text-[var(--color-mute)]">THE LAB</p>
          <h2 className="stack-head mt-6 max-w-4xl text-[clamp(2rem,5vw,4.2rem)]">
            {"WE BUILD FILM PROTOCOLS AND SYSTEMS DESIGNED TO MOVE ATHLETES NOT SLIDES".split(" ").map((w, i) => (
              <span key={`${w}-${i}`} className="mr-[0.28em] inline-block">
                {w}
              </span>
            ))}
          </h2>
          <div className="mt-16 grid gap-px bg-[var(--color-line)] md:grid-cols-2">
            {PILLARS.map((p) => (
              <div key={p.title} className="bg-black p-8 md:p-12">
                <h3 className="font-display text-xl font-semibold tracking-tight">{p.title}</h3>
                <p className="mt-4 max-w-md text-[13px] font-light leading-6 text-[var(--color-mute)]">{p.body}</p>
                <p className="mt-6 font-mono text-[10px] tracking-[0.14em] text-[var(--color-mute)]">
                  {p.tags.join("  ·  ")}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section id="contact" className="px-6 pb-24 pt-8 md:px-10">
          <h2 className="stack-head text-[clamp(2.8rem,10vw,8rem)]">
            film the
            <br />
            stance through
            <br />
            the point
          </h2>
          <a
            href="mailto:hello@lvlitup.ai"
            className="mt-12 inline-block border border-[#eee] px-6 py-3 font-mono text-[11px] tracking-[0.18em] hover:bg-[#eee] hover:text-black"
          >
            WORK WITH US
          </a>
          <p className="mt-16 font-mono text-[10px] tracking-[0.14em] text-[var(--color-mute)]">
            FIT HUB © 2026 · DEMO FILM, NOT AN OFFICIAL TEAM PAGE
          </p>
        </section>
      </main>
    </div>
  );
}
