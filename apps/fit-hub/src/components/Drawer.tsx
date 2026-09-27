import { X } from 'lucide-react'
import type { ReactNode } from 'react'

type Props = {
  open: boolean
  title: string
  subtitle?: string
  onClose: () => void
  children: ReactNode
  footer: ReactNode
}

export default function Drawer({ open, title, subtitle, onClose, children, footer }: Props) {
  return (
    <div
      className={`fixed inset-0 z-40 transition-opacity duration-300 ${open ? 'opacity-100' : 'pointer-events-none opacity-0'}`}
      aria-hidden={!open}
    >
      <div className="absolute inset-0 bg-black/20 backdrop-blur-xs" onClick={onClose} />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={`absolute top-0 right-0 flex h-full w-full flex-col border-l border-gray-200 bg-white transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}
        style={{ maxWidth: 'var(--drawer-max)', padding: 'var(--drawer-pad)' }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="font-orbitron text-lg font-bold uppercase tracking-[0.12em]">{title}</h2>
            {subtitle && (
              <p className="mt-1 text-xs font-medium uppercase tracking-[0.2em] text-gray-500">{subtitle}</p>
            )}
          </div>
          <button type="button" onClick={onClose} aria-label="Close" className="transition-opacity hover:opacity-50">
            <X strokeWidth={1.5} style={{ width: 'var(--icon)', height: 'var(--icon)' }} />
          </button>
        </div>
        <div className="mt-8 flex-1 overflow-y-auto">{children}</div>
        <div className="mt-6 border-t border-gray-200 pt-4">{footer}</div>
      </aside>
    </div>
  )
}
