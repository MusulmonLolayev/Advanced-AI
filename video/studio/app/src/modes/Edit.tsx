import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useActions } from '../actions'
import { ContextMenu, PanelDialog, useDialog, useToast } from '../components'
import { composite, longSilences, lineAt, lineStates, ORIGINAL, sections, sourcesOf, totalSeconds } from '../model'
import { playhead } from '../playhead'
import { useStudio } from '../studio'
import type { Project } from '../types'
import { secs } from '../util'
import { EmptyState, NoPresenter } from './EmptyState'
import { menuItems, type ClipKind, type Dlg } from './edit/clipMenu'
import { LanguagesPanel, RecordingsPanel, ScriptCheckPanel, TightenPanel, VersionsPanel } from './edit/panels'
import { TakeEditor } from './edit/TakeEditor'
import { Monitor } from './edit/Monitor'
import { ScriptList } from './edit/ScriptList'
import { Timeline } from './edit/Timeline'
import { usePlayer } from './edit/usePlayer'
import { useLevels } from './edit/useLevels'

export function EditMode() {
  const { project, projectLoading } = useStudio()
  if (projectLoading) return <EmptyState title="Loading the project…" />
  if (!project) return <NoPresenter what="editor" />
  return <EditBody p={project} />
}

type Sizes = { l?: number; b?: number }
const LIMITS = { l: [220, 560], b: [150, 520] } as const
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
  const act = useActions()
  const { confirm } = useDialog()
  const toast = useToast()
  const [menu, setMenu] = useState<{ kind: ClipKind; k: number; x: number; y: number } | null>(null)
  const [dlg, setDlg] = useState<Dlg | null>(null)
  const closeMenu = useCallback(() => setMenu(null), [])

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

  const items = menu ? menuItems(menu.kind, { p, k: menu.k, st: states[menu.k], tr, act, confirm, toast, open: setDlg, record }) : []

  // the one-line strip under the transport: what the selected line is playing from (no buttons: the clips have them)
  const st = states[line]
  const takes = p.takes[String(line)] ?? []
  const strip = (
    <>
      <span>line <b className="mono">{line + 1}</b></span>
      {st.take ? (
        <>
          <span>T{takes.findIndex((t) => t.id === st.take?.id) + 1} <span className="mono">{secs(st.take.length)}</span>{takes.length > 1 ? ` of ${takes.length}` : ''}</span>
          <span>used in your edit</span>
        </>
      ) : (
        <span>{st.kind === 'mistake' ? 'every take is a mistake' : st.kind === 'silent' ? 'silent in the export' : takes.length ? 'cloned voice (no take chosen)' : 'cloned voice'}</span>
      )}
      {st.voice && <span className={st.voice === 'fail' ? 'bad' : 'warn'}>voice check {st.voice === 'fail' ? 'failed' : 'passes, listen'}</span>}
      <span>{p.scenes[line]}</span>
    </>
  )

  const closeDlg = () => setDlg(null)
  const dialogs = (d: Dlg) => {
    const s = states[d.k]
    const ts = p.takes[String(d.k)] ?? []
    const title = (what: string) => <>{what} · line {d.k + 1}</>
    const wordsTake = s.take ?? ts[ts.length - 1]
    if (d.kind === 'recordings') return <PanelDialog title="Recordings" sub={`${p.sessions.length || 'none'}`} wide onClose={closeDlg}><RecordingsPanel p={p} act={act} /></PanelDialog>
    if (d.kind === 'versions') return <PanelDialog title={title('Rewrite in the cloned voice')} wide onClose={closeDlg}><VersionsPanel p={p} k={d.k} tr={tr} act={act} /></PanelDialog>
    if (d.kind === 'langs') return <PanelDialog title={title('Other languages')} onClose={closeDlg}><LanguagesPanel k={d.k} langs={langs} act={act} onGotoLang={() => { closeDlg(); setMode('script') }} /></PanelDialog>
    if (d.kind === 'check' && wordsTake) return <PanelDialog title={title('Script check')} sub={wordsTake.words ? `${wordsTake.words.heard.length} words heard` : 'not transcribed'} wide onClose={closeDlg}><ScriptCheckPanel p={p} wordsTake={wordsTake} act={act} /></PanelDialog>
    if (d.kind === 'tighten' && s.take) return <PanelDialog title={title('Tighten & nudge')} onClose={closeDlg}><TightenPanel chosen={s.take} act={act} /></PanelDialog>
    if (d.kind === 'parts' && s.take) return <TakeEditor t={s.take} n={ts.findIndex((t) => t.id === s.take?.id) + 1} levels={levels[s.take.session]} tr={tr} onClose={closeDlg} />
    return null
  }

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
      if (e.key === 'ContextMenu' || (e.key === 'F10' && e.shiftKey)) {
        // the menu key / Shift+F10: the menu of the selected clip, opened on the clip
        e.preventDefault()
        const k = line
        const el = document.querySelector<HTMLElement>(`[data-line="${k}"][data-lane="you"], [data-line="${k}"][data-lane="clone"], [data-line="${k}"][data-lane="picture"]`)
        const r = el?.getBoundingClientRect()
        setMenu({ kind: states[k]?.kind === 'take' ? 'take' : 'line', k, x: (r?.left ?? 200) + 8, y: (r?.bottom ?? 200) - 6 })
      } else if (e.key === ' ') {
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
  }, [line, p.lines.length, tr, record, states])

  // panel borders: script | monitor, and monitor | timeline; remembered in this browser
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
    ...(sizes.b ? { '--row-b': sizes.b + 'px' } : {}),
  } as React.CSSProperties

  return (
    <div className="edit" ref={root} style={style}>
      <div className="edit-top">
        <ScriptList p={p} states={states} line={line} onPick={pick} />
        <div className="edit-center">
          <Monitor p={p} total={total} videoRef={videoRef} tr={tr} line={line} onSeekLine={tr.playLine} silences={silences} onSilence={jump} strip={strip} />
        </div>
      </div>
      <Timeline p={p} states={states} sections={sects} comp={comp} total={total} line={line} onPick={pick} onSeek={seek} silences={silences} longSil={longSil} setLongSil={setLongSil} onMenu={(kind, k, x, y) => setMenu({ kind, k, x, y })} onRecordings={() => setDlg({ kind: 'recordings', k: line })} />
      {menu && <ContextMenu x={menu.x} y={menu.y} items={items} label={`actions for line ${menu.k + 1}`} onClose={closeMenu} />}
      {dlg && dialogs(dlg)}
      <Splitter cls="sp-l" label="Script width" onDrag={(e) => setSize('l', e.clientX - rect().left)} onKey={(d) => setSize('l', cur('l', '--col-l') + d)} onReset={() => setSize('l', 0)} />
      <Splitter cls="sp-b" label="Timeline height" onDrag={(e) => setSize('b', rect().bottom - e.clientY)} onKey={(d) => setSize('b', cur('b', '--row-b') - d)} onReset={() => setSize('b', 0)} />
    </div>
  )
}
