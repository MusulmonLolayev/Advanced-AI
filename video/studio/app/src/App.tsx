import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { fetchEditorLangs, fetchLectureLangs, fetchProject } from './api'
import { ToastProvider } from './components'
import { EditMode } from './modes/Edit'
import { ExportMode } from './modes/Export'
import { RecordMode } from './modes/Record'
import { ScriptMode } from './modes/Script'
import { ProjectBrowser } from './shell/ProjectBrowser'
import { StatusBar } from './shell/StatusBar'
import { TopBar } from './shell/TopBar'
import { buildName } from './snapshot'
import { StudioCtx, type Mode, type Studio } from './studio'
import { busy } from './model'
import { uploads } from './upload'
import { useLive } from './util'

const MODES: Mode[] = ['record', 'edit', 'script', 'export']

/** #mode=edit&lecture=lecture01&lang=uz&line=14 (line as the editor numbers it, from 1) */
function readHash() {
  const p = new URLSearchParams(location.hash.replace(/^#\/?/, ''))
  const m = p.get('mode') as Mode | null
  return {
    mode: m && MODES.includes(m) ? m : ('edit' as Mode),
    stem: p.get('lecture') ?? 'lecture01',
    lang: p.get('lang') ?? 'uz',
    line: Math.max(0, parseInt(p.get('line') ?? '1', 10) - 1),
  }
}

export default function App() {
  const init = useMemo(readHash, [])
  const [mode, setMode] = useState<Mode>(init.mode)
  const [stem, setStem] = useState(init.stem)
  const [lang, setLang] = useState(init.lang)
  const [line, setLine] = useState(init.line)
  const [collapsed, setCollapsed] = useState(window.innerWidth < 1500)
  const [recording, setRecording] = useState(false)
  const [recSeconds, setRecSeconds] = useState(0)
  const recRef = useRef(false)
  recRef.current = recording
  const build = buildName(stem, lang)

  const project = useLive(() => fetchProject(build), build)
  const langs = useLive(project.data ? () => fetchEditorLangs(build) : null, project.data ? build : '')
  const { reload } = project
  // the lecture's languages (counts, builds, build jobs) are needed by Script and Export only
  const lec = useLive(mode === 'script' || mode === 'export' ? () => fetchLectureLangs(stem) : null, mode === 'script' || mode === 'export' ? stem : '')
  const reloadLec = lec.reload
  const lecBusy = !!lec.data?.langs.some((l) => l.job && (l.job.state === 'queued' || l.job.state === 'running'))
  useEffect(() => {
    if (!lecBusy) return
    const t = setInterval(() => void reloadLec(), 2000)
    return () => clearInterval(t)
  }, [lecBusy, reloadLec])

  // while a job, a version or a recording is being made, ask again every 2 s; stop when idle
  const working = !!project.data && busy(project.data)
  useEffect(() => {
    if (!working) return
    const t = setInterval(() => void reload(), 2000)
    return () => clearInterval(t)
  }, [working, reload])

  useEffect(() => {
    history.replaceState(null, '', `#mode=${mode}&lecture=${stem}&lang=${lang}&line=${line + 1}`)
  }, [mode, stem, lang, line])

  useEffect(() => {
    if (!recording) return
    setRecSeconds(0)
    const t = setInterval(() => setRecSeconds((s) => s + 1), 1000)
    return () => clearInterval(t)
  }, [recording])

  // leaving the booth (another mode, lecture or language) stops a running recording: ask first
  const leave = () => !recRef.current || window.confirm('A recording is running. Leaving stops it and saves what has been recorded. Leave?')
  const modeRef = useRef(mode)
  modeRef.current = mode
  const goMode = useCallback((m: Mode) => {
    if (m !== modeRef.current && modeRef.current === 'record' && recRef.current && !window.confirm('A recording is running. Leaving stops it and saves what has been recorded. Leave?')) return
    setMode(m)
  }, [])
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (uploads.unsaved()) {
        e.preventDefault()
        e.returnValue = ''
      }
    }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [])

  const open = useCallback((s: string, l: string) => {
    if (!leave()) return
    setStem(s)
    setLang(l)
    setLine(0)
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const a = document.activeElement as HTMLElement | null
      if (a && (['INPUT', 'SELECT', 'TEXTAREA'].includes(a.tagName) || a.isContentEditable)) return
      if (e.ctrlKey || e.metaKey || e.altKey) return
      const i = '1234'.indexOf(e.key)
      if (i >= 0 && e.key.length === 1) goMode(MODES[i])
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [goMode])

  const nLines = project.data?.lines.length ?? 0
  const ctx: Studio = {
    mode, setMode: goMode, stem, lang, open, build,
    line: Math.min(line, Math.max(0, nLines - 1)),
    setLine,
    project: project.data,
    projectError: project.error,
    projectLoading: project.loading,
    langs: langs.data,
    reload: project.reload,
    lec: lec.data,
    reloadLec: lec.reload,
    reloadLangs: langs.reload,
    recording, setRecording, recSeconds,
  }

  return (
    <StudioCtx.Provider value={ctx}>
      <ToastProvider>
        <div className="app">
          <TopBar toggleBrowser={() => setCollapsed((c) => !c)} />
          <div className="body" data-collapsed={collapsed}>
            <ProjectBrowser collapsed={collapsed} onExpand={() => setCollapsed(false)} />
            <main className="main" aria-label={mode}>
              {mode === 'edit' && <EditMode key={build} />}
              {mode === 'record' && <RecordMode />}
              {mode === 'script' && <ScriptMode />}
              {mode === 'export' && <ExportMode />}
            </main>
          </div>
          <StatusBar />
        </div>
      </ToastProvider>
    </StudioCtx.Provider>
  )
}
