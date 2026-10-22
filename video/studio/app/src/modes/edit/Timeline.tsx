import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { Button, Clip, Icon, IconButton, Marker, Playhead, Track, drawEnvelope, useViewportCanvas } from '../../components'
import { useActions } from '../../actions'
import type { Composite, LineState, Section } from '../../model'
import type { Project } from '../../types'
import { clamp, timecode } from '../../util'

/** "keep … s at line ends": the margin, saved with the lecture. Saved when the field is left, on Enter, or 0.6 s after the last keystroke. */
function MarginField({ value, onSave }: { value: string; onSave: (v: number) => void }) {
  const [v, setV] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const save = (raw: string) => {
    clearTimeout(timer.current)
    const x = Math.min(5, Math.max(0, parseFloat(raw)))
    if (Number.isFinite(x) && x !== parseFloat(value)) onSave(Math.round(x * 100) / 100)
    setV(null)
  }
  return (
    <label className="tl-field" title="the silence kept before the first word and after the last when a take's ends are fitted; saved with the lecture">
      keep{' '}
      <input
        type="number"
        min={0}
        max={5}
        step={0.05}
        aria-label="margin at line ends, seconds"
        value={v ?? value}
        onChange={(e) => {
          setV(e.target.value)
          clearTimeout(timer.current)
          const raw = e.target.value
          timer.current = setTimeout(() => save(raw), 600)
        }}
        onBlur={(e) => save(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && save(e.currentTarget.value)}
      />{' '}
      s at line ends
    </label>
  )
}

const HEAD = 100
const H = { ruler: 24, markers: 24, picture: 52, you: 58, clone: 58 }
const STEPS = [0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600]

export function Timeline({
  p, states, sections, comp, total, line, onPick, onSeek, silences, longSil, setLongSil,
}: {
  p: Project
  states: LineState[]
  sections: Section[]
  comp: Composite | null
  total: number
  line: number
  onPick: (k: number) => void
  onSeek: (T: number) => void
  silences: { a: number; b: number }[]
  longSil: number
  setLongSil: (x: number) => void
}) {
  const act = useActions()
  const scroller = useRef<HTMLDivElement>(null)
  const [viewW, setViewW] = useState(900)
  const [pps, setPps] = useState(6)
  const [fitted, setFitted] = useState(false)
  const W = Math.ceil(total * pps)

  useLayoutEffect(() => {
    const el = scroller.current
    if (!el) return
    const ro = new ResizeObserver(() => setViewW(Math.max(200, el.clientWidth - HEAD)))
    ro.observe(el)
    setViewW(Math.max(200, el.clientWidth - HEAD))
    return () => ro.disconnect()
  }, [])

  const minPps = Math.max(0.05, viewW / total)
  const zoomTo = useCallback(
    (next: number, anchorPx?: number) => {
      const el = scroller.current
      const n = clamp(next, minPps, 80)
      if (el) {
        const a = anchorPx ?? viewW / 3
        const t = (el.scrollLeft + a) / pps
        setPps(n)
        requestAnimationFrame(() => {
          el.scrollLeft = t * n - a
        })
      } else setPps(n)
      setFitted(n <= minPps + 1e-6)
    },
    [pps, viewW, minPps],
  )

  // keep the selected line in view
  const lastLine = useRef(-1)
  useEffect(() => {
    const el = scroller.current
    if (!el || !states[line]) return
    const x = states[line].a * pps
    const b = states[line].b * pps
    if (lastLine.current === line && x >= el.scrollLeft && b <= el.scrollLeft + viewW) return
    lastLine.current = line
    if (x < el.scrollLeft + 20 || b > el.scrollLeft + viewW - 20) el.scrollLeft = Math.max(0, x - viewW * 0.25)
  }, [line, pps, viewW, states])

  const onWheel = (e: React.WheelEvent) => {
    if (!(e.ctrlKey || e.metaKey)) return
    e.preventDefault()
    const r = scroller.current!.getBoundingClientRect()
    zoomTo(pps * (e.deltaY < 0 ? 1.25 : 0.8), e.clientX - r.left - HEAD)
  }

  // canvases: ruler and the two waveforms draw only what is visible
  const step = STEPS.find((s) => s * pps >= 84) ?? 600
  const rulerCv = useViewportCanvas(
    scroller,
    (g, x0, w, h) => {
      const css = getComputedStyle(document.documentElement)
      g.fillStyle = css.getPropertyValue('--dim').trim()
      g.strokeStyle = css.getPropertyValue('--line-strong').trim()
      g.font = '11px ui-monospace, Menlo, Consolas, monospace'
      g.textBaseline = 'top'
      const t0 = Math.floor(x0 / pps / step) * step
      for (let t = t0; t * pps < x0 + w; t += step) {
        const x = Math.round(t * pps - x0) + 0.5
        g.beginPath()
        g.moveTo(x, h - 9)
        g.lineTo(x, h)
        g.stroke()
        g.fillText(timecode(t, false), x + 4, 5)
        for (let i = 1; i < 5; i++) {
          const xs = Math.round((t + (step * i) / 5) * pps - x0) + 0.5
          g.beginPath()
          g.moveTo(xs, h - 4)
          g.lineTo(xs, h)
          g.stroke()
        }
      }
    },
    [pps, step],
  )
  const wave = (arr: Int8Array | null, color: string) => (g: CanvasRenderingContext2D, x0: number, w: number, h: number) => {
    if (!arr) return
    drawEnvelope(g, arr, 50, 0, pps, x0, w, h, getComputedStyle(document.documentElement).getPropertyValue(color).trim())
  }
  const youCv = useViewportCanvas(scroller, wave(comp?.you ?? null, '--track-you'), [comp, pps])
  const cloneCv = useViewportCanvas(scroller, wave(comp?.clone ?? null, '--track-clone'), [comp, pps])

  const seekFromEvent = (e: React.PointerEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    onSeek(clamp((e.clientX - r.left) / pps, 0, total))
  }
  const drag = useRef(false)

  const pxl = (t: number) => t * pps
  const showText = pps >= 5
  const showNums = pps >= 12
  const marks = useMemo(() => states.map((s, k) => ({ s, k })).filter(({ s }) => s.voice || s.lang === 'needs_update'), [states])
  const lanes = H.ruler + H.markers + H.picture + H.you + H.clone

  return (
    <section className="timeline panel" aria-label="Timeline">
      <header className="tl-bar">
        <span className="tl-title">Timeline</span>
        <IconButton icon="minus" label="Zoom out" onClick={() => zoomTo(pps * 0.7)} />
        <input type="range" min={0} max={100} value={Math.round((100 * Math.log(pps / minPps)) / Math.log(80 / minPps))} aria-label="Zoom" className="zoom" onChange={(e) => zoomTo(minPps * Math.pow(80 / minPps, +e.target.value / 100))} />
        <IconButton icon="plus" label="Zoom in" onClick={() => zoomTo(pps * 1.4)} />
        <IconButton icon="fit" label="Fit the whole lecture" on={fitted} onClick={() => zoomTo(minPps)} />
        <span className="mono dim tl-zoom">{pps.toFixed(1)} px/s</span>
        <span className="tl-sep" />
        <label className="tl-field" title="silences this long or longer are marked in amber">long silence ≥ <input type="number" min={0.2} step={0.1} value={longSil} onChange={(e) => setLongSil(Math.max(0.2, +e.target.value || 1))} /> s</label>
        <MarginField value={p.settings.margin} onSave={(v) => void act.setting('margin', v)} />
        <Button small onClick={() => void act.shrinkAll()} icon="scissors" title="Optional. Shortens the long pauses inside each chosen take and trims the line ends to the margin (a trim you set by hand stays). Each take can be put back, or fitted by itself.">Tighten all</Button>
        <Button small onClick={() => void act.words()} title="Transcribe the chosen takes and compare them with the approved text">Check all against the script</Button>
        <span className="grow" />
        <span className="legend">
          <i style={{ background: 'var(--track-you)' }} /> your voice
          <i style={{ background: 'var(--track-clone)' }} /> cloned voice
          <i className="lg-sil" /> long silence
          <Icon name="mark" size={10} style={{ color: 'var(--bad)' }} /> check failed
          <Icon name="ear" size={11} style={{ color: 'var(--warn)' }} /> listen
        </span>
      </header>
      <div className="tl-scroll" ref={scroller} onWheel={onWheel} tabIndex={0} aria-label="Timeline tracks">
        <div className="tl-inner" style={{ width: HEAD + W, height: lanes, ['--track-head-w' as string]: HEAD + 'px' }}>
          <Track label="TIME" height={H.ruler} width={W}>
            <div
              className="ruler-hit"
              onPointerDown={(e) => {
                drag.current = true
                e.currentTarget.setPointerCapture(e.pointerId)
                seekFromEvent(e)
              }}
              onPointerMove={(e) => drag.current && seekFromEvent(e)}
              onPointerUp={() => (drag.current = false)}
            />
            <canvas ref={rulerCv} className="vcanvas" style={{ width: viewW, height: H.ruler }} />
          </Track>
          <Track label="MARKS" height={H.markers} width={W}>
            {showNums && states.map((_, k) => <Marker key={'l' + k} kind="line" left={pxl(states[k].a)} title={`line ${k + 1}`} onClick={() => onPick(k)} />)}
            {silences.map((s, i) => (
              <Marker key={'s' + i} kind="silence" left={pxl(s.a)} width={pxl(s.b - s.a)} title={`silence ${(s.b - s.a).toFixed(1)} s at ${timecode(s.a)}`} onClick={() => onSeek(s.a)} />
            ))}
            {marks.map(({ s, k }) => (
              <Marker
                key={'m' + k}
                kind={s.voice === 'fail' ? 'fail' : s.voice === 'listen' ? 'listen' : 'update'}
                left={pxl(s.a)}
                title={`line ${k + 1}: ${s.voice === 'fail' ? 'voice check failed' : s.voice === 'listen' ? 'listen' : 'needs update'}`}
                onClick={() => onPick(k)}
              />
            ))}
          </Track>
          <Track label="PICTURE" sub="video" color="var(--track-picture)" height={H.picture} width={W}>
            {sections.map((sec) => (
              <Clip key={sec.from} section left={pxl(sec.a)} width={pxl(sec.b - sec.a) - 1} top={2} bottom={H.picture - 20} title={`${sec.scene} · lines ${sec.from + 1}–${sec.to + 1}`} onClick={() => onPick(sec.from)}>
                <span>{sec.scene}</span>
              </Clip>
            ))}
            {states.map((s, k) => (
              <Clip
                key={k}
                left={pxl(s.a)}
                width={pxl(s.b - s.a) - 1}
                top={H.picture - 26}
                bottom={2}
                color="var(--track-picture)"
                muted={s.kind !== 'take'}
                selected={k === line}
                title={`${k + 1}. ${p.lines[k][1].slice(0, 90)}`}
                onClick={() => onPick(k)}
              >
                <span className="mono">{k + 1}</span>
                {showText && <span className="clip-text">{p.lines[k][1]}</span>}
              </Clip>
            ))}
          </Track>
          <Track label="YOU" sub="recorded" color="var(--track-you)" height={H.you} width={W}>
            {states.map((s, k) =>
              s.kind === 'take' ? (
                <Clip key={k} left={pxl(s.a)} width={pxl(s.b - s.a) - 1} color="var(--track-you)" selected={k === line} onClick={() => onPick(k)} title={`line ${k + 1}: your take, ${(s.b - s.a).toFixed(1)} s`} muted>
                </Clip>
              ) : null,
            )}
            <canvas ref={youCv} className="vcanvas wavecv" style={{ width: viewW, height: H.you }} />
          </Track>
          <Track label="CLONE" sub="own voice" color="var(--track-clone)" height={H.clone} width={W}>
            {states.map((s, k) =>
              s.kind === 'clone' ? (
                <Clip key={k} left={pxl(s.a)} width={pxl(s.b - s.a) - 1} color="var(--track-clone)" selected={k === line} onClick={() => onPick(k)} title={`line ${k + 1}: cloned voice`} muted />
              ) : null,
            )}
            <canvas ref={cloneCv} className="vcanvas wavecv" style={{ width: viewW, height: H.clone }} />
          </Track>
          <Playhead pps={pps} offset={HEAD} />
        </div>
      </div>
    </section>
  )
}

