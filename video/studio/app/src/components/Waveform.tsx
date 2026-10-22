import { useEffect, useRef, type RefObject } from 'react'

/** Redraw `draw` into a canvas as big as the visible part of `scroller`, whenever it scrolls or resizes. */
export function useViewportCanvas(scroller: RefObject<HTMLElement | null>, draw: (g: CanvasRenderingContext2D, x0: number, w: number, h: number) => void, deps: unknown[]) {
  const cv = useRef<HTMLCanvasElement>(null)
  const drawRef = useRef(draw)
  drawRef.current = draw
  useEffect(() => {
    const el = scroller.current
    const c = cv.current
    if (!el || !c) return
    let raf = 0
    const paint = () => {
      raf = 0
      const dpr = window.devicePixelRatio || 1
      const w = c.clientWidth
      const h = c.clientHeight
      if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
        c.width = Math.round(w * dpr)
        c.height = Math.round(h * dpr)
      }
      const g = c.getContext('2d')!
      g.setTransform(dpr, 0, 0, dpr, 0, 0)
      g.clearRect(0, 0, w, h)
      drawRef.current(g, el.scrollLeft, w, h)
    }
    const queue = () => {
      if (!raf) raf = requestAnimationFrame(paint)
    }
    paint()
    el.addEventListener('scroll', queue, { passive: true })
    const ro = new ResizeObserver(queue)
    ro.observe(el)
    return () => {
      el.removeEventListener('scroll', queue)
      ro.disconnect()
      if (raf) cancelAnimationFrame(raf)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scroller, ...deps])
  return cv
}

/** Draw a level array (dB, `rate` values a second) as a mirrored waveform between time t0..t1 into [x, x+w). */
export function drawEnvelope(g: CanvasRenderingContext2D, db: ArrayLike<number>, rate: number, tStart: number, pps: number, x0: number, w: number, h: number, color: string, floor = -60, offset = 0, ceil = -8, tEnd = Infinity) {
  g.fillStyle = color
  const mid = h / 2
  const tA = Math.max(0, x0 / pps)
  const tB = Math.min(tEnd, (x0 + w) / pps)
  const step = Math.max(1, Math.floor(rate / pps / 2))
  for (let px = Math.floor(tA * pps); px < tB * pps; px++) {
    const t = px / pps
    const i0 = Math.floor((t - tStart) * rate + offset * rate)
    if (i0 < 0) continue
    let m = floor
    const span = Math.max(step, Math.ceil(rate / pps))
    for (let i = i0; i < i0 + span && i < db.length; i++) if (db[i] > m) m = db[i]
    if (m <= floor + 1) continue
    const a = Math.min(1, Math.max(0.05, (m - floor) / (ceil - floor)))
    const hh = Math.max(1, a * (mid - 1))
    g.fillRect(px - x0, mid - hh, 1, hh * 2)
  }
}
