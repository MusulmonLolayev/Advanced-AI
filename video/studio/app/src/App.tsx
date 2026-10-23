import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { fetchEditorLangs, fetchLectureLangs, fetchLectures, fetchProject } from './api'
import { DialogProvider, Drawer, ToastProvider, useDialog } from './components'
import { ExportMode } from './modes/Export'
import { ScriptMode } from './modes/Script'
import { Workspace } from './modes/Workspace'
import { ProjectBrowser } from './shell/ProjectBrowser'
import { StatusBar } from './shell/StatusBar'
import { TopBar } from './shell/TopBar'
import { StudioCtx, type Panel, type Studio } from './studio'
import { busy } from './model'
import { uploads } from './upload'
import { buildName, useLive } from './util'

/** The deep link: `#lecture=lecture01&lang=uz&line=14&rec=1&panel=export&watch=…` (line as the editor numbers it, from 1; `rec=1` the booth
 *  is on; `panel=script|export` a panel is open). The old `mode=` names still work: record = rec=1, edit = the plain workspace, script and
 *  export = that panel. The same names in the query (`/?mode=edit&…`, what the old pages' addresses redirect to) work too; the hash wins. */
function readUrl() {
  const q = new URLSearchParams(location.search)
  const h = new URLSearchParams(location.hash.replace(/^#\/?/, ''))
  const get = (k: string) => h.get(k) ?? q.get(k)
  const m = get('mode')
  const p = get('panel') ?? (m === 'script' || m === 'export' ? m : null)
  return {
    rec: get('rec') === '1' || m === 'record',
    panel: (p === 'script' || p === 'export' ? p : null) as Panel,
    stem: get('lecture') ?? 'lecture01',
    lang: get('lang') ?? 'uz',
    line: Math.max(0, parseInt(get('line') ?? '1', 10) - 1),
    watch: get('watch') ?? '',
    /** the address names a lecture; otherwise the app opens the first one there is */
    explicit: get('lecture') !== null,
  }
}

const hashOf = (rec: boolean, panel: Panel, stem: string, lang: string, line: number, watch: string) =>
  `#lecture=${stem}&lang=${lang}&line=${line + 1}${rec ? '&rec=1' : ''}${panel ? '&panel=' + panel : ''}${watch && panel === 'export' ? '&watch=' + encodeURIComponent(watch) : ''}`

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
  const [boothOn, setBoothNow] = useState(init.rec)
  const [panel, setPanel] = useState<Panel>(init.panel)
  const takeOnOpen = useRef(false)
  const [rewriteLine, setRewriteLine] = useState<number | null>(null)
  const [stem, setStem] = useState(init.stem)
  const [lang, setLang] = useState(init.lang)
  const [line, setLine] = useState(init.line)
  const [watch, setWatch] = useState(init.watch)
  // the project browser starts as the icon rail; the last choice is kept in this browser
  const [collapsed, setCollapsedNow] = useState(() => {
    try {
      return localStorage.getItem('studioBrowser') !== 'open'
    } catch {
      return true
    }
  })
  const setCollapsed = useCallback((f: boolean | ((c: boolean) => boolean)) => {
    setCollapsedNow((c) => {
      const n = typeof f === 'function' ? f(c) : f
      try {
        localStorage.setItem('studioBrowser', n ? 'closed' : 'open')
      } catch {
        /* private window: the choice lasts until the page closes */
      }
      return n
    })
  }, [])
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
  const lec = useLive(panel ? () => fetchLectureLangs(stem) : null, panel ? stem : '')
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
    history.replaceState(null, '', location.pathname + hashOf(boothOn, panel, stem, lang, line, watch))
  }, [boothOn, panel, stem, lang, line, watch])

  // the address changed under us (typed, pasted, or an old page's redirect): follow it
  useEffect(() => {
    const apply = (u: ReturnType<typeof readUrl>) => {
      setBoothNow(u.rec)
      setPanel(u.panel)
      setStem(u.stem)
      setLang(u.lang)
      setLine(u.line)
      setWatch(u.watch)
    }
    const follow = () => {
      const u = readUrl()
      if (recRef.current && (u.stem !== stemRef.current || u.lang !== langRef.current || !u.rec)) {
        // put the old address back at once, ask, and only follow the new one when the answer is Leave
        history.replaceState(null, '', location.pathname + hashOf(true, panelRef.current, stemRef.current, langRef.current, lineRef.current, ''))
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

  const panelRef = useRef(panel)
  panelRef.current = panel
  const lineRef = useRef(line)
  lineRef.current = line
  const boothRef = useRef(boothOn)
  boothRef.current = boothOn
  /** Record on or off. Off while a recording runs asks first; the booth stays as it is until the answer, and on Leave it unmounts and
   *  flushes chunks, events and finish. `take` (L from the plain workspace) records one take of the selected line when it is up. */
  const setBoothOn = useCallback((on: boolean, opts?: { take?: boolean }) => {
    if (on) {
      if (opts?.take && !boothRef.current) takeOnOpen.current = true
      setBoothNow(true)
    } else if (recRef.current) void askLeave().then((ok) => { if (ok) setBoothNow(false) })
    else setBoothNow(false)
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

  // the studio's own keys: B Record on / off, S the Script & languages drawer, E the Export dialog (the booth's and the editor's keys are
  // listed in the README; nothing here clashes with them, and Alt / Ctrl / Meta combinations are left to the browser)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const a = document.activeElement as HTMLElement | null
      if (a && (['INPUT', 'SELECT', 'TEXTAREA'].includes(a.tagName) || a.isContentEditable)) return
      if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return
      const k = e.key.toLowerCase()
      if (k === 'b') setBoothOn(!boothRef.current)
      else if (k === 's') setPanel((p) => (p === 'script' ? null : 'script'))
      else if (k === 'e') setPanel((p) => (p === 'export' ? null : 'export'))
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [setBoothOn])

  const nLines = project.data?.lines.length ?? 0
  const ctx: Studio = {
    boothOn, setBoothOn, takeOnOpen, rewriteLine, setRewriteLine, panel, setPanel, stem, lang, open, build,
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
            <main className="main" aria-label="Workspace">
              <Workspace key={build} />
            </main>
          </div>
          <StatusBar />
          {panel === 'script' && <Drawer title="Script & languages" onClose={() => setPanel(null)}><ScriptMode /></Drawer>}
          {panel === 'export' && <Drawer dialog title="Export" onClose={() => setPanel(null)}><ExportMode /></Drawer>}
        </div>
      </ToastProvider>
    </StudioCtx.Provider>
  )
}
