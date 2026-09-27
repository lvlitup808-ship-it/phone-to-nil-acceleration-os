import { useState } from 'react'
import { FOOTER_FILM } from '../film'

function Still({ src, cap }: { src: string; cap: string }) {
  const [missing, setMissing] = useState(false)
  return (
    <div className="group relative overflow-hidden border border-gray-200 bg-gray-100">
      {missing ? (
        <div className="absolute inset-0 flex items-center justify-center text-[0.6rem] font-medium uppercase tracking-[0.18em] text-gray-400">
          Film pending
        </div>
      ) : (
        <img
          src={src}
          alt={`${cap.toLowerCase()} still`}
          loading="lazy"
          onError={() => setMissing(true)}
          className="absolute inset-0 h-full w-full object-cover object-center grayscale-[0.15] contrast-110 transition duration-300 group-hover:scale-[1.04] group-hover:grayscale-0"
        />
      )}
      <div
        className="absolute inset-x-0 bottom-0 bg-black/70 px-2 py-1 font-jakarta uppercase tracking-[0.18em] text-white"
        style={{ fontSize: 'var(--footer-label)' }}
      >
        {cap}
      </div>
    </div>
  )
}

export default function FooterFilmRail() {
  return (
    <footer className="relative z-20 border-t border-gray-200 bg-white">
      <div className="flex items-center justify-between" style={{ paddingInline: 'var(--pad-x)', paddingBlock: '0.55rem' }}>
        <span className="font-orbitron uppercase tracking-[0.22em]" style={{ fontSize: 'var(--footer-label)' }}>
          FIT HUB FILM // 2026
        </span>
        <span className="hidden font-jakarta uppercase tracking-[0.18em] text-gray-500 sm:inline" style={{ fontSize: 'var(--micro)' }}>
          STANCE · POINT · TUNNEL · LEAP · BELT · ROAR · LOOK
        </span>
      </div>
      <div
        className="film-strip no-scrollbar"
        style={{ height: 'var(--footer-h)', paddingInline: 'var(--pad-x)', paddingBottom: '0.65rem' }}
      >
        {FOOTER_FILM.map((f) => (
          <Still key={f.cap} src={f.src} cap={f.cap} />
        ))}
      </div>
      <p className="pb-3 text-center uppercase tracking-[0.16em] text-gray-400" style={{ fontSize: 'var(--micro)' }}>
        FIT HUB © 2026 — GAME DAY SYSTEMS · DEMO FILM, NOT AN OFFICIAL TEAM PAGE
      </p>
    </footer>
  )
}
