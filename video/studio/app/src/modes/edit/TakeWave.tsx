import { useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { Button, drawEnvelope, useViewportCanvas } from '../../components'
import { cutsLabel, selection, xToTake, type Span } from '../../cuts'
import type { Levels } from '../../types'
import { clamp, secs } from '../../util'

const SNAP = 0.05 // handles snap to 0.05 s (as the old level strip did)
const r2 = (x: number) => Math.round(x * 100) / 100
const DRAG_PX = 4 // a pointer that moves less than this between down and up is a click, not a selection
const SELECT_EVENT = 'takewave-select' // a new selection in one wave clears the others (Delete cuts only the one you see)
export type TrimChange = { trim_in?: number | null; trim_out?: number | null }

/** A take's (or the original voice's) waveform with long silences shaded, trim handles and the fit marks. Dragging a
 *  handle (or arrow keys on it) calls `onTrim` with only the handle that moved; a trim of 0 is sent as null.
 *  Dragging on the wave itself selects a part (take seconds, snapped to 0.01 s, inside the trims); the bar under the wave
 *  plays it (`onPlaySelection`) or cuts it (`onCut`, also Delete / Backspace); Esc clears it. Hand cuts (`cuts`) and the
 *  tightening tool's (`autoCuts`) are drawn hatched in two shades; a click on a hand cut offers `onRestore`. */
export function TakeWave({
  levels, from, to, pauses, trimIn, trimOut, fit, color, handles = true, height = 64, cuts = [], autoCuts = [], onTrim, onPlayFrom, onCut, onRestore, onClearCuts, onPlaySelection, playhead, bigHandles,
}: {
  levels: Levels | undefined
  from: number
  to: number
  pauses?: [number, number][]
  trimIn?: number
  trimOut?: number
  fit?: [number, number]
  color: string
  handles?: boolean
  height?: number
  onTrim?: (c: TrimChange) => void
  /** a click on the strip (not on a handle): the take's own second there, to play from */
  onPlayFrom?: (t: number) => void
  /** the hand cuts and the tool's cuts, in the take's own seconds (the clock of the trims and of this strip) */
  cuts?: Span[]
  autoCuts?: Span[]
  /** cut this selected part (the caller merges it into the cuts) */
  onCut?: (span: Span) => void
  /** put the i-th hand cut back */
  onRestore?: (i: number) => void
  onClearCuts?: () => void
  onPlaySelection?: (span: Span) => void
  /** a moving line at this take second (the wide editor shows where the playing take is) */
  playhead?: number | null
  /** the wide editor: wide, labelled trim handles that show their time while dragged */
  bigHandles?: boolean
}) {
  const len = Math.max(0.01, to - from)
  const box = useRef<HTMLDivElement>(null)
  const cv = useViewportCanvas(
    box,
    (g, _x0, w, h) => {
      if (!levels) return
      const pps = w / len
      const css = getComputedStyle(document.documentElement)
      g.globalAlpha = 0.9
      drawEnvelope(g, levels.db, 1 / levels.step, 0, pps, 0, w, h, css.getPropertyValue(color).trim() || color, -60, from)
      g.globalAlpha = 1
      g.fillStyle = 'rgba(233,180,76,0.13)'
      for (const [a, b] of pauses ?? []) if (b - a >= 0.5) g.fillRect(a * pps, 0, (b - a) * pps, h)
    },
    [levels, from, to, color, pauses],
  )
  const pct = (t: number) => `${(100 * t) / len}%`
  // a handle being dragged shows its live position; the saved one comes back from the server
  const [drag, setDrag] = useState<{ which: 0 | 1; tin: number; tout: number } | null>(null)
  const dragRef = useRef<typeof drag>(null)
  const saved = { tin: trimIn ?? 0, tout: trimOut ?? 0 }
  const live = drag ?? { ...saved, which: 0 }
  const a = live.tin
  const b = len - live.tout
  const room = Math.max(len - 0.1, 0) // the two handles never cross
  const move = (which: 0 | 1, tt: number, from: { tin: number; tout: number }) => {
    const t = clamp(Math.round(tt / SNAP) * SNAP, 0, len)
    return which === 0 ? { which, tin: Math.min(t, Math.max(room - from.tout, 0)), tout: from.tout } : { which, tin: from.tin, tout: Math.min(len - t, Math.max(room - from.tin, 0)) }
  }
  const commit = (d: { tin: number; tout: number }) => {
    const ch: TrimChange = {}
    if (r2(d.tin) !== r2(saved.tin)) ch.trim_in = r2(d.tin) || null
    if (r2(d.tout) !== r2(saved.tout)) ch.trim_out = r2(d.tout) || null
    if (!Object.keys(ch).length) return false
    onTrim?.(ch)
    return true
  }
  // after a release the handle stays where it was dropped until the saved trim arrives (or 1.5 s, if the save failed)
  useEffect(() => {
    if (!dragRef.current) setDrag(null)
  }, [trimIn, trimOut])
  const down = (which: 0 | 1) => (e: React.PointerEvent<HTMLSpanElement>) => {
    if (!onTrim) return
    e.preventDefault()
    e.currentTarget.setPointerCapture(e.pointerId)
    dragRef.current = { which, ...saved }
    setDrag(dragRef.current)
  }
  const onMove = (e: React.PointerEvent<HTMLSpanElement>) => {
    const d = dragRef.current
    if (!d || !box.current) return
    const r = box.current.getBoundingClientRect()
    dragRef.current = move(d.which, ((e.clientX - r.left) / r.width) * len, d)
    setDrag(dragRef.current)
  }
  const up = () => {
    const d = dragRef.current
    dragRef.current = null
    if (d && commit(d)) setTimeout(() => !dragRef.current && setDrag(null), 1500)
    else setDrag(null)
  }
  const key = (which: 0 | 1) => (e: React.KeyboardEvent<HTMLSpanElement>) => {
    const dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0
    if (!dir || !onTrim) return
    e.preventDefault()
    const at = which === 0 ? saved.tin : len - saved.tout
    commit(move(which, at + dir * SNAP, saved))
  }
  const grip = (which: 0 | 1) => ({
    onPointerDown: down(which),
    onPointerMove: onMove,
    onPointerUp: up,
    onPointerCancel: up,
    onKeyDown: key(which),
    role: onTrim ? 'slider' : undefined,
    tabIndex: onTrim ? 0 : undefined,
    'aria-label': which === 0 ? 'trim start' : 'trim end',
    'aria-valuemin': 0,
    'aria-valuemax': r2(len),
    'aria-valuenow': r2(which === 0 ? a : b),
  })
  // ─── selecting a part ───
  const id = useId()
  const [sel, setSel] = useState<Span | null>(null)
  const [picked, setPicked] = useState<number | null>(null) // a hand cut that was clicked: the bar offers to restore it
  const selRef = useRef<{ t0: number; x0: number; moved: boolean } | null>(null)
  const swallow = useRef(false) // the click that follows a drag must not play the take
  const selectable = handles && !!onCut
  const select = (v: Span | null) => {
    setSel(v)
    if (v) {
      setPicked(null)
      window.dispatchEvent(new CustomEvent(SELECT_EVENT, { detail: id }))
    }
  }
  const timeOf = (clientX: number) => {
    const r = box.current!.getBoundingClientRect()
    return xToTake(clientX, r.left, r.width, len)
  }
  const onBodyDown = (e: React.PointerEvent<HTMLDivElement>) => {
    const el = e.target as HTMLElement
    if (!selectable || e.button !== 0 || el.closest('.trim-handle, .cut-hand, .wave-tools') || !box.current) return
    box.current.setPointerCapture(e.pointerId)
    selRef.current = { t0: timeOf(e.clientX), x0: e.clientX, moved: false }
  }
  const onBodyMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const d = selRef.current
    if (!d || !box.current) return
    if (!d.moved && Math.abs(e.clientX - d.x0) < DRAG_PX) return
    d.moved = true
    select(selection(d.t0, timeOf(e.clientX), len, saved.tin, saved.tout))
  }
  const onBodyUp = () => {
    if (selRef.current?.moved) swallow.current = true
    selRef.current = null
  }
  useEffect(() => {
    const other = (e: Event) => (e as CustomEvent).detail !== id && setSel(null)
    window.addEventListener(SELECT_EVENT, other)
    return () => window.removeEventListener(SELECT_EVENT, other)
  }, [id])
  // a new selection brings its take card into view (the inspector can be scrolled so the wave is half hidden)
  const has = sel !== null
  useEffect(() => {
    if (has) ((box.current?.closest('.take, .te-body') as HTMLElement | null) ?? box.current)?.scrollIntoView({ block: 'nearest' })
  }, [has])
  // the floating toolbar sits over the top of the selection (or of the picked cut), kept inside the wave
  const tools = useRef<HTMLDivElement>(null)
  const anchor = sel ?? (picked !== null ? cuts[picked] ?? null : null)
  const anchorKey = anchor ? `${anchor[0]}-${anchor[1]}` : ''
  useLayoutEffect(() => {
    const el = tools.current
    const b = box.current
    if (!el || !b || !anchor) return
    const w = b.clientWidth
    const mid = ((anchor[0] + anchor[1]) / 2 / len) * w
    el.style.left = `${Math.max(2, Math.min(mid - el.offsetWidth / 2, w - el.offsetWidth - 2))}px`
  }, [anchorKey, len, picked, sel === null])
  const doCut = () => {
    if (!sel || !onCut) return
    onCut(sel)
    setSel(null)
  }
  const doCutRef = useRef(doCut)
  doCutRef.current = doCut
  useEffect(() => {
    if (!sel) return
    const onKey = (e: KeyboardEvent) => {
      const a = document.activeElement as HTMLElement | null
      if (a && (['INPUT', 'SELECT', 'TEXTAREA'].includes(a.tagName) || a.isContentEditable)) return
      if (e.ctrlKey || e.metaKey || e.altKey) return
      if (e.key === 'Delete' || e.key === 'Backspace') {
        e.preventDefault()
        doCutRef.current()
      } else if (e.key === 'Escape') {
        e.preventDefault()
        e.stopPropagation()
        setSel(null)
      }
    }
    // captured on the window: it comes before the app's own single-key shortcuts, and before a wide editor's <dialog> closes on Esc
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [sel])
  // the saved cuts changed (a cut was made or restored): the selection and the picked cut are stale
  const cutsKey = JSON.stringify(cuts)
  useEffect(() => {
    setSel(null)
    setPicked(null)
  }, [cutsKey])

  return (
    <div className="takewave-wrap">
    <div
      className={'takewave' + (bigHandles ? ' big' : '')}
      ref={box}
      style={{ height, cursor: onPlayFrom ? 'pointer' : undefined }}
      title={onPlayFrom ? (selectable ? 'click to play the take from there; drag on the wave to select a part to cut; drag the two handles to trim' : 'click to play the take from there; drag the two handles to trim') : undefined}
      onPointerDown={onBodyDown}
      onPointerMove={onBodyMove}
      onPointerUp={onBodyUp}
      onPointerCancel={onBodyUp}
      onClick={(e) => {
        if ((e.target as HTMLElement).closest('.wave-tools')) return
        if (swallow.current) {
          swallow.current = false
          return
        }
        if ((e.target as HTMLElement).classList.contains('trim-handle') || !onPlayFrom || !box.current) return
        const r = box.current.getBoundingClientRect()
        onPlayFrom(clamp(((e.clientX - r.left) / r.width) * len, 0, len))
      }}
    >
      <canvas ref={cv} className="takewave-canvas" />
      {!levels && <span className="takewave-wait dim">loading levels…</span>}
      {handles && (
        <>
          {autoCuts.map(([x, y], i) => (
            <div key={'a' + i} className="cut-auto" style={{ left: pct(x), width: pct(y - x) }} title={`cut by the tightening tool: ${x.toFixed(2)}–${y.toFixed(2)} s (managed by “undo tightening”)`} />
          ))}
          {cuts.map(([x, y], i) => (
            <div key={'h' + i} className={'cut-hand' + (picked === i ? ' picked' : '')} data-cut={i} style={{ left: pct(x), width: pct(y - x) }} title={`your cut: ${x.toFixed(2)}–${y.toFixed(2)} s (click to restore)`} onClick={(ev) => { ev.stopPropagation(); setSel(null); setPicked(picked === i ? null : i) }} />
          ))}
          {sel && <div className="wave-sel" style={{ left: pct(sel[0]), width: pct(sel[1] - sel[0]) }} />}
          <div className="trim-shade" style={{ left: 0, width: pct(a) }} />
          <div className="trim-shade" style={{ right: 0, width: pct(len - b) }} />
          {fit && <i className="fit-mark" style={{ left: pct(fit[0]) }} title={`fit start: ${secs(fit[0], 2)}`} />}
          {fit && <i className="fit-mark" style={{ left: pct(len - fit[1]) }} title={`fit end: ${secs(fit[1], 2)} trimmed`} />}
          <span className="trim-handle in" style={{ left: pct(a) }} title="start handle (drag to trim)" {...grip(0)}>{bigHandles && <b className="trim-label">{drag?.which === 0 ? `start ${a.toFixed(2)} s` : 'start'}</b>}</span>
          <span className="trim-handle out" style={{ left: pct(b) }} title="end handle (drag to trim)" {...grip(1)}>{bigHandles && <b className="trim-label">{drag?.which === 1 ? `end ${b.toFixed(2)} s` : 'end'}</b>}</span>
          {playhead != null && <i className="wave-playhead" style={{ left: pct(clamp(playhead, 0, len)) }} />}
          {anchor && (
            <div className="wave-tools" ref={tools} data-bar={sel ? 'selection' : 'cut'}>
              {sel ? (
                <>
                  {onPlaySelection && <Button small icon="play" aria-label="play selection" onClick={() => onPlaySelection(sel)} title="play only the selected part" />}
                  <Button small variant="primary" aria-label="cut this part" onClick={doCut} title="remove the selected part from the take (Delete)">✂ cut {(sel[1] - sel[0]).toFixed(2)} s</Button>
                  <Button small variant="ghost" aria-label="clear selection" onClick={() => setSel(null)} title="clear the selection (Esc)">✕</Button>
                </>
              ) : (
                <>
                  <span className="mono dim">{anchor[0].toFixed(2)}–{anchor[1].toFixed(2)}</span>
                  <Button small variant="primary" aria-label="restore" onClick={() => onRestore?.(picked!)} title="put this part back">restore</Button>
                  <Button small variant="ghost" aria-label="keep it cut" onClick={() => setPicked(null)} title="keep it cut">✕</Button>
                </>
              )}
            </div>
          )}
        </>
      )}
    </div>
    {selectable && (cuts.length > 0 || autoCuts.length > 0) && (
      <div className="wave-bar">
        {(cuts.length > 0 || autoCuts.length > 0) && (
          <div className="wave-cuts mono dim" data-bar="cuts">
            {cuts.length > 0 && <span>{cutsLabel(cuts)}</span>}
            {autoCuts.length > 0 && <span>{cuts.length ? ' · ' : ''}tool: {autoCuts.length} pause{autoCuts.length === 1 ? '' : 's'} cut</span>}
            {cuts.length > 0 && onClearCuts && <button type="button" className="link" onClick={onClearCuts}>clear cuts</button>}
          </div>
        )}
      </div>
    )}
    </div>
  )
}
