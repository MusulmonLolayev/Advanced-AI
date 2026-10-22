import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { composite, longSilences, lineAt, lineStates, ORIGINAL, sections, sourcesOf, totalSeconds } from '../model'
import { playhead } from '../playhead'
import { useStudio } from '../studio'
import type { Project } from '../types'
import { EmptyState } from './EmptyState'
import { Inspector } from './edit/Inspector'
import { Monitor } from './edit/Monitor'
import { ScriptList } from './edit/ScriptList'
import { Timeline } from './edit/Timeline'
import { usePlayer } from './edit/usePlayer'
import { useLevels } from './edit/useLevels'

export function EditMode() {
  const { project, projectError, projectLoading, build, stem, lang } = useStudio()
  if (projectLoading) return <EmptyState title="Loading the project…" />
  if (!project)
    return (
      <EmptyState title={`No editor for ${stem} · ${lang} yet`} tone={projectError?.includes('404') ? undefined : 'bad'}>
        <p className="dim">{projectError}</p>
        <p>
          {build} has no presenter page, so there is nothing to edit. Prepare it from today's module page (or build the video, for a language that has none).
        </p>
      </EmptyState>
    )
  return <EditBody p={project} />
}

type Sizes = { l?: number; r?: number; b?: number }
const LIMITS = { l: [220, 560], r: [260, 560], b: [150, 520] } as const
const readSizes = (): Sizes => {
  try {
    return JSON.parse(localStorage.getItem('studioPanels') ?? '{}') as Sizes
  } catch {
    return {}
  }
}

/** A draggable border (also arrow keys); double-click puts the panel back to its default. */
function Splitter({ cls: c, label, onDrag, onKey, onReset }: { cls: string; label: string; onDrag: (e: PointerEvent) => void; onKey: (dir: number) => void; onReset: () => void }) {
  return (
    <div
      className={'splitter ' + c}
      role="separator"
      aria-label={label}
      tabIndex={0}
      title={`${label} (drag; double-click to reset)`}
      onPointerDown={(e) => {
        e.preventDefault()
        const el = e.currentTarget
        el.setPointerCapture(e.pointerId)
        const move = (ev: PointerEvent) => onDrag(ev)
        const up = () => {
          el.removeEventListener('pointermove', move)
          el.removeEventListener('pointerup', up)
        }
        el.addEventListener('pointermove', move)
        el.addEventListener('pointerup', up)
      }}
      onDoubleClick={onReset}
      onKeyDown={(e) => {
        const dir = e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : 0
        if (dir) {
          e.preventDefault()
          e.stopPropagation()
          onKey(dir * 16)
        }
      }}
    />
  )
}

function EditBody({ p }: { p: Project }) {
  const { line, setLine, langs, setMode, build, setRecording } = useStudio()
  const videoRef = useRef<HTMLVideoElement>(null)
  const root = useRef<HTMLDivElement>(null)
  const [longSil, setLongSil] = useState(1)
  const [sizes, setSizes] = useState<Sizes>(readSizes)

  const states = useMemo(() => lineStates(p, langs), [p, langs])
  const sects = useMemo(() => sections(p, states), [p, states])
  const total = useMemo(() => totalSeconds(p), [p])
  const srcs = useMemo(() => [...new Set([...sourcesOf(p), ORIGINAL])], [p])
  const levels = useLevels(build, srcs, p.video_version)
  const ready = srcs.every((s) => levels[s])
  const comp = useMemo(() => (ready ? composite(p, levels) : null), [p, levels, ready])
  const silences = useMemo(() => (comp ? longSilences(comp, longSil) : []), [comp, longSil])
  const tr = usePlayer(p, states, videoRef, line, setLine)
  const { seek } = tr

  const pick = useCallback((k: number) => seek(states[k].a), [seek, states])
  const record = useCallback(() => {
    setMode('record')
    setRecording(false)
  }, [setMode, setRecording])

  // put the playhead on the selected line when the mode opens
  useEffect(() => {
    const T = playhead.get()
    if (lineAt(states, T) !== line || T === 0) seek(states[line].a)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const jump = (dir: 1 | -1) => {
    const T = playhead.get()
    const hit = dir > 0 ? silences.find((s) => s.a > T + 0.05) : [...silences].reverse().find((s) => s.a < T - 0.05)
    if (hit) seek(hit.a)
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const a = document.activeElement as HTMLElement | null
      if (a && (['INPUT', 'SELECT', 'TEXTAREA'].includes(a.tagName) || a.isContentEditable)) return
      if (e.ctrlKey || e.metaKey || e.altKey) return
      if (e.key === ' ') {
        e.preventDefault()
        tr.toggle()
      } else if (e.key === 'ArrowRight') {
        if (a?.getAttribute('role') === 'slider' || a?.getAttribute('role') === 'separator') return
        e.preventDefault()
        tr.playLine(Math.min(p.lines.length - 1, line + 1))
      } else if (e.key === 'ArrowLeft') {
        if (a?.getAttribute('role') === 'slider' || a?.getAttribute('role') === 'separator') return
        e.preventDefault()
        tr.playLine(Math.max(0, line - 1))
      } else if (e.key.toLowerCase() === 'l') record()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [line, p.lines.length, tr, record])

  // panel borders: script | monitor | inspector, and monitor | timeline; remembered in this browser
  const setSize = (k: keyof Sizes, v: number) =>
    setSizes((s) => {
      const [lo, hi] = LIMITS[k]
      const n = { ...s, [k]: v === 0 ? undefined : Math.round(Math.min(hi, Math.max(lo, v))) }
      try {
        localStorage.setItem('studioPanels', JSON.stringify(n))
      } catch {
        /* private window: the sizes last until the page closes */
      }
      return n
    })
  const rect = () => root.current!.getBoundingClientRect()
  const cur = (k: keyof Sizes, css: string) => sizes[k] ?? parseFloat(getComputedStyle(root.current!).getPropertyValue(css))
  const style = {
    ...(sizes.l ? { '--col-l': sizes.l + 'px' } : {}),
    ...(sizes.r ? { '--col-r': sizes.r + 'px' } : {}),
    ...(sizes.b ? { '--row-b': sizes.b + 'px' } : {}),
  } as React.CSSProperties

  return (
    <div className="edit" ref={root} style={style}>
      <div className="edit-top">
        <ScriptList p={p} states={states} line={line} onPick={pick} />
        <div className="edit-center">
          <Monitor p={p} total={total} videoRef={videoRef} tr={tr} line={line} onSeekLine={tr.playLine} silences={silences} onSilence={jump} />
        </div>
        <Inspector p={p} k={line} st={states[line]} langs={langs} levels={levels} tr={tr} onGotoLang={() => setMode('script')} onRecord={record} />
      </div>
      <Timeline p={p} states={states} sections={sects} comp={comp} total={total} line={line} onPick={pick} onSeek={seek} silences={silences} longSil={longSil} setLongSil={setLongSil} />
      <Splitter cls="sp-l" label="Script width" onDrag={(e) => setSize('l', e.clientX - rect().left)} onKey={(d) => setSize('l', cur('l', '--col-l') + d)} onReset={() => setSize('l', 0)} />
      <Splitter cls="sp-r" label="Inspector width" onDrag={(e) => setSize('r', rect().right - e.clientX)} onKey={(d) => setSize('r', cur('r', '--col-r') - d)} onReset={() => setSize('r', 0)} />
      <Splitter cls="sp-b" label="Timeline height" onDrag={(e) => setSize('b', rect().bottom - e.clientY)} onKey={(d) => setSize('b', cur('b', '--row-b') - d)} onReset={() => setSize('b', 0)} />
    </div>
  )
}
