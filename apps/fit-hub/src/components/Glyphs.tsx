type Corner = 'tl' | 'tr' | 'bl' | 'br'

const BRACKET: Record<Corner, string> = {
  tl: 'M0 11.5V0.5H11.5',
  tr: 'M0.5 0.5H11.5V11.5',
  bl: 'M0 0.5V11.5H11.5',
  br: 'M0.5 11.5H11.5V0.5',
}

export function Bracket({ corner, className = '' }: { corner: Corner; className?: string }) {
  return (
    <svg viewBox="0 0 12 12" className={`h-3 w-3 ${className}`} fill="none" aria-hidden="true">
      <path d={BRACKET[corner]} stroke="currentColor" strokeWidth={1} />
    </svg>
  )
}

/** 36×18 checker: 4 rows × 8 squares of 4.5, alternating per row. */
export function Checker() {
  const s = 4.5
  const squares = []
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 8; c++) {
      if ((r + c) % 2 === 0) squares.push(<rect key={`${r}-${c}`} x={c * s} y={r * s} width={s} height={s} />)
    }
  }
  return (
    <svg
      viewBox="0 0 36 18"
      aria-hidden="true"
      className="inline-block align-baseline"
      style={{ width: 'var(--checker-w)', height: 'var(--checker-h)', transform: 'translateY(2px)' }}
      fill="currentColor"
    >
      {squares}
    </svg>
  )
}

export function Globe() {
  return (
    <svg
      viewBox="0 0 64 64"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.2}
      aria-hidden="true"
      style={{ width: 'var(--globe)', height: 'var(--globe)' }}
    >
      <circle cx={32} cy={32} r={28} />
      <path d="M4 32H60" />
      <ellipse cx={32} cy={32} rx={28} ry={10} />
      <ellipse cx={32} cy={32} rx={28} ry={20} />
      <path d="M32 4V60" />
      <ellipse cx={32} cy={32} rx={10} ry={28} />
      <ellipse cx={32} cy={32} rx={20} ry={28} />
    </svg>
  )
}
