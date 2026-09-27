import { useEffect, useRef } from 'react'
import { BG_IMAGE_1, BG_IMAGE_2, layerStyle } from '../film'

const STOPS: [number, number][] = [
  [0, 1],
  [0.4, 1],
  [0.6, 0.75],
  [0.75, 0.4],
  [0.88, 0.12],
  [1, 0],
]

const spotlightRadius = () => Math.round(Math.min(420, Math.max(160, window.innerWidth * 0.16)))
const gridCell = () => Math.round(Math.min(64, Math.max(36, window.innerWidth * 0.028)))

export default function ImageRevealBackground() {
  const revealRef = useRef<HTMLDivElement>(null)
  const patternRef = useRef<SVGPatternElement>(null)
  const gridPathRef = useRef<SVGPathElement>(null)

  useEffect(() => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 }
    const smooth = { ...mouse }
    const offset = { x: 0, y: 0 }
    let last = { x: NaN, y: NaN, w: 0, h: 0 }
    let raf = 0

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      const cell = gridCell()
      patternRef.current?.setAttribute('width', String(cell))
      patternRef.current?.setAttribute('height', String(cell))
      gridPathRef.current?.setAttribute('d', `M ${cell} 0 L 0 0 0 ${cell}`)
      last = { x: NaN, y: NaN, w: 0, h: 0 }
    }

    const onMove = (e: MouseEvent) => {
      mouse.x = e.clientX
      mouse.y = e.clientY
    }

    const paintMask = () => {
      const r = spotlightRadius()
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const g = ctx.createRadialGradient(smooth.x, smooth.y, 0, smooth.x, smooth.y, r)
      for (const [at, a] of STOPS) g.addColorStop(at, `rgba(255,255,255,${a})`)
      ctx.fillStyle = g
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      const url = `url(${canvas.toDataURL()})`
      const el = revealRef.current
      if (el) {
        el.style.maskImage = url
        el.style.setProperty('-webkit-mask-image', url)
      }
    }

    const tick = () => {
      smooth.x += (mouse.x - smooth.x) * 0.1
      smooth.y += (mouse.y - smooth.y) * 0.1

      const cx = mouse.x / window.innerWidth - 0.5
      const cy = mouse.y / window.innerHeight - 0.5
      offset.x += (cx * 16 - offset.x) * 0.06
      offset.y += (cy * 16 - offset.y) * 0.06
      patternRef.current?.setAttribute('patternTransform', `translate(${offset.x} ${offset.y})`)

      // Re-encode the mask only when the spotlight actually moved.
      if (
        Math.abs(smooth.x - last.x) > 0.25 ||
        Math.abs(smooth.y - last.y) > 0.25 ||
        last.w !== canvas.width ||
        last.h !== canvas.height ||
        Number.isNaN(last.x)
      ) {
        paintMask()
        last = { x: smooth.x, y: smooth.y, w: canvas.width, h: canvas.height }
      }
      raf = requestAnimationFrame(tick)
    }

    resize()
    window.addEventListener('resize', resize)
    window.addEventListener('mousemove', onMove)
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', onMove)
    }
  }, [])

  return (
    <div className="pointer-events-none fixed inset-0 z-0 hidden overflow-hidden lg:block" aria-hidden="true">
      <div className="absolute inset-0" style={layerStyle(BG_IMAGE_1)} />
      <div
        ref={revealRef}
        className="absolute inset-0"
        style={{ ...layerStyle(BG_IMAGE_2), maskSize: '100% 100%', WebkitMaskSize: '100% 100%', maskRepeat: 'no-repeat', WebkitMaskRepeat: 'no-repeat' }}
      />
      <svg className="absolute inset-0 h-full w-full" style={{ opacity: 0.1 }}>
        <defs>
          <pattern id="fh-grid" ref={patternRef} width={48} height={48} patternUnits="userSpaceOnUse">
            <path ref={gridPathRef} d="M 48 0 L 0 0 0 48" fill="none" stroke="#64748b" strokeWidth={0.6} />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#fh-grid)" />
      </svg>
    </div>
  )
}
