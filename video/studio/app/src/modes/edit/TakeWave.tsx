import { useEffect, useRef, useState } from 'react'
import { drawEnvelope, useViewportCanvas } from '../../components'
import type { Levels } from '../../types'
import { clamp, secs } from '../../util'

const SNAP = 0.05 // handles snap to 0.05 s (levels.js)
const r2 = (x: number) => Math.round(x * 100) / 100
export type TrimChange = { trim_in?: number | null; trim_out?: number | null }

/** A take's (or the original voice's) waveform with long silences shaded, trim handles and the fit marks. Dragging a
 *  handle (or arrow keys on it) calls `onTrim` with only the handle that moved; a trim of 0 is sent as null. */
export function TakeWave({
  levels, from, to, pauses, trimIn, trimOut, fit, color, handles = true, height = 64, onTrim,
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
  return (
    <div className="takewave" ref={box} style={{ height }}>
      <canvas ref={cv} className="takewave-canvas" />
      {!levels && <span className="takewave-wait dim">loading levels…</span>}
      {handles && (
        <>
          <div className="trim-shade" style={{ left: 0, width: pct(a) }} />
          <div className="trim-shade" style={{ right: 0, width: pct(len - b) }} />
          {fit && <i className="fit-mark" style={{ left: pct(fit[0]) }} title={`fit start: ${secs(fit[0], 2)}`} />}
          {fit && <i className="fit-mark" style={{ left: pct(len - fit[1]) }} title={`fit end: ${secs(fit[1], 2)} trimmed`} />}
          <span className="trim-handle in" style={{ left: pct(a) }} title="start handle (drag to trim)" {...grip(0)} />
          <span className="trim-handle out" style={{ left: pct(b) }} title="end handle (drag to trim)" {...grip(1)} />
        </>
      )}
    </div>
  )
}
