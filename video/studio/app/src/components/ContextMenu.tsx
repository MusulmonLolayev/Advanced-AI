import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

export type MenuItem = {
  label: string
  onSelect?: () => void
  /** a submenu (opens on hover, → or Enter) */
  items?: MenuItem[]
  checked?: boolean
  danger?: boolean
  disabled?: boolean
  /** dim text at the right (a length, a key) */
  hint?: string
  /** a line above this item */
  sep?: boolean
}

const GAP = 4
type Anchor = { x: number; y: number; flipX?: number }

function Menu({ items, at, onPick, onBack, sub, label }: { items: MenuItem[]; at: Anchor; onPick: () => void; onBack: () => void; sub?: boolean; label: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [pos, setPos] = useState({ left: at.x, top: at.y, ready: false })
  const [active, setActive] = useState(-1)
  const [open, setOpen] = useState<number | null>(null)
  const rows = useRef<(HTMLButtonElement | null)[]>([])
  // measured once: it flips to the left (or up) when it would leave the screen
  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    const w = el.offsetWidth
    const h = el.offsetHeight
    const vw = window.innerWidth
    const vh = window.innerHeight
    const left = at.x + w > vw - GAP ? (at.flipX !== undefined ? at.flipX - w : vw - w - GAP) : at.x
    const top = at.y + h > vh - GAP ? Math.max(GAP, vh - h - GAP) : at.y
    setPos({ left: Math.max(GAP, left), top, ready: true })
    el.focus({ preventScroll: true })
  }, [at.x, at.y, at.flipX])
  useEffect(() => {
    if (active >= 0) rows.current[active]?.scrollIntoView({ block: 'nearest' })
  }, [active])
  const ok = (i: number) => !!items[i] && !items[i].disabled
  const step = (d: 1 | -1) => {
    let i = active
    for (let n = 0; n < items.length; n++) {
      i = (i + d + items.length) % items.length
      if (ok(i)) return setActive(i)
    }
  }
  const run = (i: number) => {
    const it = items[i]
    if (!it || it.disabled) return
    if (it.items) setOpen(i)
    else {
      it.onSelect?.()
      onPick()
    }
  }
  const onKeyDown = (e: React.KeyboardEvent) => {
    e.nativeEvent.stopPropagation() // the app's single-key shortcuts stay out while a menu is open
    const k = e.key
    if (open !== null) return // the submenu has the keys
    if (k === 'ArrowDown') step(1)
    else if (k === 'ArrowUp') step(-1)
    else if (k === 'Home') setActive(items.findIndex((_, i) => ok(i)))
    else if (k === 'End') setActive(items.map((_, i) => i).reverse().find(ok) ?? -1)
    else if (k === 'Enter' || k === ' ' || (k === 'ArrowRight' && items[active]?.items)) {
      if (active < 0) return
      run(active)
    } else if (k === 'ArrowLeft' && sub) onBack()
    else if (k === 'Escape') onBack()
    else if (k !== 'Tab') return
    e.preventDefault()
  }
  return (
    <div ref={ref} className="ctxmenu" role="menu" aria-label={label} tabIndex={-1} style={{ left: pos.left, top: pos.top, opacity: pos.ready ? 1 : 0 }} onKeyDown={onKeyDown} onContextMenu={(e) => e.preventDefault()}>
      {items.map((it, i) => (
        <div key={i} className="ctx-slot">
          {it.sep && <hr className="ctx-sep" />}
          <button
            ref={(el) => { rows.current[i] = el }}
            type="button"
            role={it.checked !== undefined ? 'menuitemradio' : 'menuitem'}
            aria-checked={it.checked}
            aria-haspopup={it.items ? 'menu' : undefined}
            aria-disabled={it.disabled || undefined}
            tabIndex={-1}
            className={'ctx-item' + (it.danger ? ' danger' : '') + (it.disabled ? ' disabled' : '') + (active === i ? ' active' : '')}
            onPointerEnter={() => { setActive(i); setOpen(it.items && !it.disabled ? i : null) }}
            onClick={() => run(i)}
          >
            <span className="ctx-check">{it.checked ? '✓' : ''}</span>
            <span className="ctx-label">{it.label}</span>
            {it.hint && <span className="ctx-hint mono">{it.hint}</span>}
            {it.items && <span className="ctx-arrow">▸</span>}
          </button>
          {open === i && it.items && (() => {
            const r = rows.current[i]?.getBoundingClientRect()
            return r ? <Menu items={it.items} at={{ x: r.right - 2, y: r.top - 4, flipX: r.left + 2 }} sub label={it.label} onPick={onPick} onBack={() => { setOpen(null); ref.current?.focus() }} /> : null
          })()}
        </div>
      ))}
    </div>
  )
}

/** A context menu at the pointer (or at an element, for the keyboard): ↑ ↓ Home End move, Enter or → run / open a submenu,
 *  ← or Esc go back, an outside click, a scroll or a resize close it. It flips at the screen's edges and gives the focus back. */
export function ContextMenu({ x, y, items, label = 'actions', onClose }: { x: number; y: number; items: MenuItem[]; label?: string; onClose: () => void }) {
  const was = useRef<HTMLElement | null>(document.activeElement as HTMLElement | null)
  useEffect(() => {
    const out = (e: Event) => {
      if (!(e.target as HTMLElement | null)?.closest?.('.ctxmenu')) onClose()
    }
    const away = () => onClose()
    document.addEventListener('pointerdown', out, true)
    document.addEventListener('wheel', out, true)
    document.addEventListener('scroll', out, true)
    window.addEventListener('resize', away)
    window.addEventListener('blur', away)
    return () => {
      document.removeEventListener('pointerdown', out, true)
      document.removeEventListener('wheel', out, true)
      document.removeEventListener('scroll', out, true)
      window.removeEventListener('resize', away)
      window.removeEventListener('blur', away)
      try {
        was.current?.focus({ preventScroll: true })
      } catch {
        /* the element is gone */
      }
    }
  }, [onClose])
  return createPortal(<Menu items={items} at={{ x, y }} label={label} onPick={onClose} onBack={onClose} />, document.body)
}
