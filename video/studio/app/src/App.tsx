import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { fetchEditorLangs, fetchLectureLangs, fetchLectures, fetchProject } from './api'
import { DialogProvider, ToastProvider, useDialog } from './components'
import { EditMode } from './modes/Edit'
import { ExportMode } from './modes/Export'
import { RecordMode } from './modes/Record'
import { ScriptMode } from './modes/Script'
import { ProjectBrowser } from './shell/ProjectBrowser'
import { StatusBar } from './shell/StatusBar'
import { TopBar } from './shell/TopBar'
import { StudioCtx, type Mode, type Studio } from './studio'
import { busy } from './model'
import { uploads } from './upload'
import { buildName, useLive } from './util'

const MODES: Mode[] = ['record', 'edit', 'script', 'export']

/** The deep link: `#mode=edit&lecture=lecture01&lang=uz&line=14&watch=…` (line as the editor numbers it, from 1). The same
 *  names in the query (`/?mode=edit&…`, what the old pages' addresses redirect to) work too; the hash wins. */
function readUrl() {
  const q = new URLSearchParams(location.search)
  const h = new URLSearchParams(location.hash.replace(/^#\/?/, ''))
  const get = (k: string) => h.get(k) ?? q.get(k)
  const m = get('mode') as Mode | null
  return {
    mode: m && MODES.includes(m) ? m : ('edit' as Mode),
    stem: get('lecture') ?? 'lecture01',
    lang: get('lang') ?? 'uz',
    line: Math.max(0, parseInt(get('line') ?? '1', 10) - 1),
    watch: get('watch') ?? '',
    /** the address names a lecture; otherwise the app opens the first one there is */
    explicit: get('lecture') !== null,
  }
}

/** the dialog provider sits outside, because the app itself asks questions (leaving the booth while recording) */
export default function App() {
  return (
    <DialogProvider>
      <AppInner />
    </DialogProvider>
  )
}

function AppInner() {
  const { confirm } = useDialog()
  // leaving the booth (another mode, lecture or language) stops a running recording: ask first
  const askLeave = useCallback(
    () => confirm({
      title: 'Leave and stop recording?',
      body: 'A recording is running. Leaving stops it and saves what has been recorded.',
      confirmLabel: 'Leave',
      tone: 'primary',
    }),
    [confirm],
  )
  const init = useMemo(readUrl, [])
  const [mode, setMode] = useState<Mode>(init.mode)
  const [stem, setStem] = useState(init.stem)
  const [lang, setLang] = useState(init.lang)
  const [line, setLine] = useState(init.line)
  const [watch, setWatch] = useState(init.watch)
  const [collapsed, setCollapsed] = useState(window.innerWidth < 1500)
  const [recording, setRecording] = useState(false)
  const [recSeconds, setRecSeconds] = useState(0)
  const recRef = useRef(false)
  recRef.current = recording
  const stemRef = useRef(stem)
  const langRef = useRef(lang)
  stemRef.current = stem
  langRef.current = lang
  const build = buildName(stem, lang)

  const project = useLive(() => fetchProject(build), build)
  const langs = useLive(project.data ? () => fetchEditorLangs(build) : null, project.data ? build : '')
  const { reload } = project
  // the lecture's languages (counts, builds, build jobs) are needed by Script and Export only
  const lec = useLive(mode === 'script' || mode === 'export' ? () => fetchLectureLangs(stem) : null, mode === 'script' || mode === 'export' ? stem : '')
  const overview = useLive(fetchLectures, 'all')
  const noLecture = overview.data && !init.explicit && !overview.data.some((m) => m.lectures.some((l) => l.stem === stem))
  useEffect(() => {
    const first = overview.data?.flatMap((m) => m.lectures)[0]
    if (noLecture && first) {
      setStem(first.stem)
      setLang(first.langs.find((l) => l.build)?.lang ?? first.langs[0]?.lang ?? 'uz')
    }
  }, [noLecture, overview.data])
  const reloadLecture = lec.reload
  const reloadOverview = overview.reload
  const reloadLec = useCallback(async () => void (await Promise.all([reloadLecture(), reloadOverview()])), [reloadLecture, reloadOverview])
  const lecBusy = !!lec.data?.langs.some((l) => l.job && (l.job.state === 'queued' || l.job.state === 'running'))
  useEffect(() => {
    if (!lecBusy) return
    const t = setInterval(() => void reloadLec(), 2000)
    return () => clearInterval(t)
  }, [lecBusy, reloadLec])
  // a build job finished or a recording was made: the browser's counts move too
  useEffect(() => {
    if (!lecBusy) return
    return () => void reloadOverview()
  }, [lecBusy, reloadOverview])

  // while a job, a version or a recording is being made, ask again every 2 s; stop when idle
  const working = !!project.data && busy(project.data)
  useEffect(() => {
    if (!working) return
    const t = setInterval(() => void reload(), 2000)
    return () => clearInterval(t)
  }, [working, reload])

  useEffect(() => {
    history.replaceState(null, '', `${location.pathname}#mode=${mode}&lecture=${stem}&lang=${lang}&line=${line + 1}${watch && mode === 'export' ? '&watch=' + encodeURIComponent(watch) : ''}`)
  }, [mode, stem, lang, line, watch])

  // the address changed under us (typed, pasted, or an old page's redirect): follow it
  useEffect(() => {
    const apply = (u: ReturnType<typeof readUrl>) => {
      setMode(u.mode)
      setStem(u.stem)
      setLang(u.lang)
      setLine(u.line)
      setWatch(u.watch)
    }
    const follow = () => {
      const u = readUrl()
      if (recRef.current && (u.stem !== stemRef.current || u.lang !== langRef.current || u.mode !== modeRef.current)) {
        // put the old address back at once, ask, and only follow the new one when the answer is Leave
        history.replaceState(null, '', `${location.pathname}#mode=${modeRef.current}&lecture=${stemRef.current}&lang=${langRef.current}`)
        void askLeave().then((ok) => { if (ok) apply(u) })
        return
      }
      apply(u)
    }
    window.addEventListener('hashchange', follow)
    window.addEventListener('popstate', follow)
    return () => {
      window.removeEventListener('hashchange', follow)
      window.removeEventListener('popstate', follow)
    }
  }, [askLeave])

  useEffect(() => {
    if (!recording) return
    setRecSeconds(0)
    const t = setInterval(() => setRecSeconds((s) => s + 1), 1000)
    return () => clearInterval(t)
  }, [recording])

  const modeRef = useRef(mode)
  modeRef.current = mode
  const goMode = useCallback((m: Mode) => {
    if (m !== modeRef.current && modeRef.current === 'record' && recRef.current) {
      // the booth stays as it is until the answer; on Leave it unmounts and flushes chunks, events and finish
      void askLeave().then((ok) => { if (ok) setMode(m) })
      return
    }
    setMode(m)
  }, [askLeave])
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

  const open = useCallback(async (s: string, l: string) => {
    if (recRef.current && !(await askLeave())) return
    setStem(s)
    setLang(l)
    setLine(0)
  }, [askLeave])

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
    reloadLec,
    overview: overview.data,
    watch,
    setWatch,
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
