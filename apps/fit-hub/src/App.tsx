import { ArrowUpRight, Check, ChevronRight, ShoppingBag } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import Drawer from './components/Drawer'
import FooterFilmRail from './components/FooterFilmRail'
import { Bracket, Checker, Globe } from './components/Glyphs'
import ImageRevealBackground from './components/ImageRevealBackground'
import { BG_IMAGE_1, layerStyle } from './film'

type DrawerId = 'roster' | 'cycles' | 'film' | 'cart'
type Product = { title: string; price: number; tag: string }

const PRODUCTS: Product[] = [
  { title: 'AWAY STRIKE JERSEY', price: 165, tag: 'GAME WHITE' },
  { title: 'VISOR + MOUTHGUARD PACK', price: 45, tag: 'SIDELINE' },
  { title: 'RECEIVER GLOVE SET', price: 80, tag: 'IN STOCK' },
  { title: 'TUNNEL WARMUP SHELL', price: 120, tag: 'PRE-ORDER' },
]

const CYCLES = [
  { series: 'SERIES 01', title: 'STANCE', body: 'First-step hip height and hand placement. Film before you cue.' },
  { series: 'SERIES 02', title: 'RELEASE', body: 'WR stem and break. No composite score.' },
  { series: 'SERIES 03', title: 'SIGNAL', body: 'Point, celebrate, reset. Presence is a skill.' },
]

const FILM_RULES = [
  { date: 'SEP 2026', title: 'TUNNEL TO HASH', length: '3 MIN' },
  { date: 'SEP 2026', title: 'CONSENT BEFORE SHARE', length: '4 MIN' },
  { date: 'SEP 2026', title: 'GATE CLOSED ON DRILLS', length: '2 MIN' },
]

const NAV: { id: DrawerId; label: string }[] = [
  { id: 'roster', label: 'ROSTER' },
  { id: 'cycles', label: 'CYCLES' },
  { id: 'film', label: 'FILM' },
]

const DRAWER_TITLES: Record<DrawerId, { title: string; subtitle?: string }> = {
  roster: { title: 'On Field', subtitle: 'Match-Day Kits' },
  cycles: { title: 'Camp 2026', subtitle: 'Closed-Loop Sessions' },
  film: { title: 'Intake', subtitle: 'Capture Rules' },
  cart: { title: 'Kit Bag' },
}

const usd = (n: number) => `$${n}`

export default function App() {
  const [drawer, setDrawer] = useState<DrawerId | null>(null)
  const [cart, setCart] = useState<Product[]>([])
  const [toast, setToast] = useState<string | null>(null)
  const toastTimer = useRef<number | undefined>(undefined)

  const close = useCallback(() => setDrawer(null), [])

  const notify = useCallback((msg: string) => {
    setToast(msg)
    window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(null), 3000)
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && close()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [close])

  const add = (p: Product) => {
    setCart((c) => [...c, p])
    notify(`Added "${p.title}" to your kit bag.`)
  }

  const checkout = () => {
    setCart([])
    close()
    notify('Lab order submitted.')
  }

  const drawerFooter =
    drawer === 'cart' && cart.length > 0 ? (
      <button
        type="button"
        onClick={checkout}
        className="flex w-full items-center justify-center gap-2 rounded-md bg-black py-3 text-xs font-semibold uppercase tracking-[0.18em] text-white transition-opacity hover:opacity-80"
      >
        CHECK OUT THE LAB <ChevronRight className="h-4 w-4" strokeWidth={1.5} />
      </button>
    ) : (
      <p className="text-center text-[0.65rem] uppercase tracking-[0.16em] text-gray-400">
        FIT HUB © 2026 — GAME DAY SYSTEMS
      </p>
    )

  return (
    <div className="relative flex min-h-screen flex-col justify-between overflow-hidden bg-white font-jakarta text-black">
      <ImageRevealBackground />

      {/* Header */}
      <header
        className="relative z-20 flex flex-wrap items-center justify-between gap-x-6 gap-y-3"
        style={{ paddingInline: 'var(--pad-x)', paddingTop: 'var(--header-pt)', paddingBottom: 'var(--section-gap)' }}
      >
        <button
          type="button"
          onClick={close}
          className="flex shrink-0 items-start whitespace-nowrap font-orbitron font-black tracking-[0.15em] transition-opacity hover:opacity-80"
          style={{ fontSize: 'var(--logo)' }}
        >
          FIT HUB
          <span className="-mt-0.5 ml-0.5" style={{ fontSize: 'var(--logo-deg)' }}>
            ˚
          </span>
        </button>
        <nav
          className="flex items-center whitespace-nowrap font-medium uppercase tracking-[0.2em]"
          style={{ fontSize: 'var(--nav)', gap: 'var(--gap-nav)' }}
        >
          {NAV.map((n) => (
            <button key={n.id} type="button" onClick={() => setDrawer(n.id)} className="transition-opacity hover:opacity-50">
              {n.label}
            </button>
          ))}
          <span className="text-gray-400" aria-hidden="true">
            |
          </span>
          <button
            type="button"
            onClick={() => setDrawer('cart')}
            aria-label={`Kit bag, ${cart.length} items`}
            className="relative transition-opacity hover:opacity-50"
          >
            <ShoppingBag strokeWidth={1.5} style={{ width: 'var(--icon)', height: 'var(--icon)' }} />
            {cart.length > 0 && (
              <span className="absolute -top-1.5 -right-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-black px-1 text-[0.55rem] font-semibold tracking-normal text-white">
                {cart.length}
              </span>
            )}
          </button>
        </nav>
      </header>

      {/* Hero */}
      <main
        className="relative z-10 flex flex-1 flex-col justify-between gap-10 lg:flex-row"
        style={{ paddingInline: 'var(--pad-x)', paddingBlock: 'var(--main-py)' }}
      >
        <div className="flex flex-col justify-center">
          <Bracket corner="tl" className="mb-3" />
          <h1
            className="font-orbitron font-extrabold uppercase tracking-[0.08em]"
            style={{ fontSize: 'var(--headline)', lineHeight: 1.05 }}
          >
            <span className="block">GAME</span>
            <span className="block">DAY</span>
            <span className="block">
              SYSTEMS <Checker />
            </span>
          </h1>
          <Bracket corner="bl" className="mt-3" />
          <div className="mt-8">
            <button
              type="button"
              onClick={() => setDrawer('roster')}
              className="inline-flex items-center rounded-md border border-gray-400 bg-white/60 uppercase tracking-[0.18em] transition-colors hover:border-black hover:bg-black hover:text-white"
              style={{ fontSize: 'var(--body)', paddingInline: 'var(--btn-px)', paddingBlock: 'var(--btn-py)', gap: 'var(--btn-gap)' }}
            >
              ENTER THE TUNNEL <ArrowUpRight className="h-4 w-4" strokeWidth={1.5} />
            </button>
          </div>
        </div>

        <div
          className="relative flex flex-col gap-4 self-start lg:self-end"
          style={{ minWidth: 'var(--feature-min)', padding: 'var(--feature-pad)' }}
        >
          <Bracket corner="tl" className="absolute top-0 left-0" />
          <Bracket corner="tr" className="absolute top-0 right-0" />
          <Bracket corner="bl" className="absolute bottom-0 left-0" />
          <Bracket corner="br" className="absolute right-0 bottom-0" />
          <Globe />
          <p className="font-semibold uppercase leading-relaxed tracking-[0.18em]" style={{ fontSize: 'var(--body)' }}>
            STANCE. STRIKE. SIGN.
            <br />
            FILM THE FIRST STEP.
          </p>
        </div>

        {/* Below lg: static still instead of the cursor reveal */}
        <div
          className="aspect-[4/5] w-full border border-gray-200 bg-gray-100 sm:aspect-[16/9] lg:hidden"
          style={layerStyle(BG_IMAGE_1)}
          role="img"
          aria-label="Ready stance still"
        />
      </main>

      <FooterFilmRail />

      {/* Drawers */}
      {(['roster', 'cycles', 'film', 'cart'] as DrawerId[]).map((id) => (
        <Drawer
          key={id}
          open={drawer === id}
          title={DRAWER_TITLES[id].title}
          subtitle={DRAWER_TITLES[id].subtitle}
          onClose={close}
          footer={drawer === id ? drawerFooter : null}
        >
          {id === 'roster' && (
            <ul className="divide-y divide-gray-200">
              {PRODUCTS.map((p) => (
                <li key={p.title} className="flex items-center justify-between gap-4 py-4">
                  <div>
                    <p className="text-[0.6rem] font-medium uppercase tracking-[0.2em] text-gray-500">{p.tag}</p>
                    <p className="mt-1 text-sm font-semibold uppercase tracking-[0.08em]">{p.title}</p>
                    <p className="mt-0.5 text-sm text-gray-600">{usd(p.price)}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => add(p)}
                    className="rounded-md border border-gray-400 px-3 py-1.5 text-[0.65rem] font-semibold uppercase tracking-[0.18em] transition-colors hover:bg-black hover:text-white"
                  >
                    ADD
                  </button>
                </li>
              ))}
            </ul>
          )}

          {id === 'cycles' && (
            <ol className="space-y-6">
              {CYCLES.map((c) => (
                <li key={c.series}>
                  <p className="text-[0.6rem] font-medium uppercase tracking-[0.2em] text-gray-500">{c.series}</p>
                  <p className="mt-1 font-orbitron text-sm font-bold uppercase tracking-[0.12em]">{c.title}</p>
                  <p className="mt-1 text-sm text-gray-600">{c.body}</p>
                </li>
              ))}
            </ol>
          )}

          {id === 'film' && (
            <ul className="divide-y divide-gray-200">
              {FILM_RULES.map((f) => (
                <li key={f.title} className="flex items-baseline justify-between gap-4 py-4">
                  <div>
                    <p className="text-[0.6rem] font-medium uppercase tracking-[0.2em] text-gray-500">{f.date}</p>
                    <p className="mt-1 text-sm font-semibold uppercase tracking-[0.08em]">{f.title}</p>
                  </div>
                  <span className="text-[0.65rem] uppercase tracking-[0.18em] text-gray-500">{f.length}</span>
                </li>
              ))}
            </ul>
          )}

          {id === 'cart' &&
            (cart.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-3 text-gray-500">
                <ShoppingBag className="h-8 w-8" strokeWidth={1.25} />
                <p className="text-sm">Your kit bag is empty.</p>
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {cart.map((p, i) => (
                  <li key={`${p.title}-${i}`} className="flex items-center justify-between gap-4 py-4">
                    <div>
                      <p className="text-sm font-semibold uppercase tracking-[0.08em]">{p.title}</p>
                      <p className="mt-0.5 text-sm text-gray-600">{usd(p.price)}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setCart((c) => c.filter((_, j) => j !== i))}
                      className="text-[0.65rem] font-medium uppercase tracking-[0.18em] text-gray-500 transition-colors hover:text-black"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            ))}
        </Drawer>
      ))}

      {/* Toast */}
      <div
        role="status"
        aria-live="polite"
        className={`fixed z-50 flex items-center gap-2 rounded-md bg-black px-4 py-3 text-xs text-white transition-all duration-300 ${toast ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-2 opacity-0'}`}
        style={{ bottom: '1.25rem', right: 'var(--pad-x)' }}
      >
        <Check className="h-4 w-4 text-emerald-400" strokeWidth={2} />
        {toast}
      </div>
    </div>
  )
}
