// Record mode: the old presenter page and its takes panel (removed 2026-10-22) as components. The engine is booth.ts
// (playing, recording, event log) and upload.ts (the chunk queue); this file is the screen.
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from 'react'
import { useActions } from '../actions'
import { fetchLine } from '../api'
import { Button, Chip, Icon, IconButton, Meter, Panel, Timecode, useDialog, useToast } from '../components'
import { Booth, type Level, type Line, type Snap } from '../booth'
import { glue, spanOf } from '../player'
import { useStudio } from '../studio'
import type { LineInfo, Project, Take } from '../types'
import { secs, useAsync } from '../util'
import { uploads, recover } from '../upload'
import { EmptyState, NoPresenter } from './EmptyState'

const NOTES = ['below', 'right', 'hidden'] as const
type Notes = (typeof NOTES)[number]
const KEYS: [string, string][] = [
  ['Space  P', 'pause / play; starts the next line'],
  ['→', 'next line (playing: jump to its end)'],
  ['←', 'back to the line start, then the line before'],
  ['L', 'record one take of this line'],
  ['R', 'start / stop recording the session'],
  ['X', 'mistake while recording: the line starts over'],
  ['T', 'show or hide the takes'],
  ['M', 'microphone'],
  ['N', 'notes: below / right / off'],
  ['F', 'full screen'],
  ['Esc', 'stop watching a take, cancel the count-in'],
]
const NOMIC = 'Recording needs https or the ssh tunnel (http://localhost:8081)'
const DB_LO = -60 // the meter's bottom, dBFS
const pos = (db: number) => Math.min(1, Math.max(0, (db - DB_LO) / -DB_LO))
const when = (n: string) => {
  const m = /^\d+-(\d+)-(\d+)T(\d+)-(\d+)/.exec(n)
  return m ? `${m[2]}.${m[1]} ${m[3]}:${m[4]}` : n
}

const HIDE_TAKE = {
  title: 'Hide this take?',
  body: 'The take is hidden from the lecture.',
  confirmLabel: 'Hide take',
  tone: 'danger',
} as const

export function RecordMode() {
  const { project, projectLoading, build } = useStudio()
  const lines = useAsync<Line[]>(project ? () => fetch(`/${build}/presenter/lines.json`).then((r) => (r.ok ? r.json() : Promise.reject(new Error('no lines.json'))) as Promise<Line[]>) : null, project ? build : '')
  const L = useMemo<Line[]>(() => lines.data ?? (project ? project.lines.map(([t, s]) => [t, s, []] as Line) : []), [lines.data, project])
  if (projectLoading) return <EmptyState title="Loading the project…" />
  if (!project) return <NoPresenter what="recording booth" />
  if (lines.loading) return <EmptyState title="Loading the lines…" />
  // lines.json holds the narration chunks (word timings); without it the prompter lights the whole line
  return <BoothView key={build} p={project} L={L} />
}

function BoothView({ p, L }: { p: Project; L: Line[] }) {
  const { line, setLine, setRecording, recSeconds, build, reload } = useStudio()
  const toast = useToast()
  const { confirm } = useDialog()
  const act = useActions()
  const videoRef = useRef<HTMLVideoElement>(null)
  const boothRef = useRef<Booth | null>(null)
  const [snap, setSnap] = useState<Snap | null>(null)
  const [level, setLevel] = useState<Level>({ rms: -100, peak: -100, clip: false })
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [countIn, setCountIn] = useState(() => {
    try {
      const c = localStorage.getItem('studioCountIn')
      return c !== null && /^\d+$/.test(c) ? +c : 3
    } catch {
      return 3
    }
  })
  const [showTakes, setShowTakes] = useState(true)
  // where the notes (the teleprompter) go: under the picture, at its right, or hidden; remembered in this browser (the old page's key)
  const [notes, setNotes] = useState<Notes>(() => {
    try {
      const n = localStorage.getItem('presenterNotes')
      return NOTES.includes(n as Notes) ? (n as Notes) : 'below'
    } catch {
      return 'below'
    }
  })
  const nextNotes = useCallback(() => {
    setNotes((n) => {
      const m = NOTES[(NOTES.indexOf(n) + 1) % NOTES.length]
      try {
        localStorage.setItem('presenterNotes', m)
      } catch {
        /* not remembered */
      }
      return m
    })
  }, [])
  const [info, setInfo] = useState<LineInfo | null>(null)
  const [recovered, setRecovered] = useState<string[]>([])
  const secure = typeof window !== 'undefined' && window.isSecureContext && !!navigator.mediaDevices
  const up = useSyncExternalStore(uploads.subscribe, () => `${uploads.waiting()}|${uploads.error()}`)
  const cur = useRef({ p, setLine, setRecording, reload, toast, line })
  cur.current = { p, setLine, setRecording, reload, toast, line }
  const frames = useRef(0)

  // the engine, once the video element exists
  useEffect(() => {
    const v = videoRef.current
    if (!v) return
    const b = new Booth(
      v,
      build,
      L,
      {
        state: setSnap,
        level: (l) => {
          if (++frames.current % 3 === 0) setLevel(l)
        },
        setLine: (k) => k !== cur.current.line && cur.current.setLine(k),
        say: (m) => cur.current.toast(m),
        setRecording: (r) => cur.current.setRecording(r),
        recorded: () => void cur.current.reload(),
        audio: () => cur.current.p.audio,
      },
      cur.current.line,
    )
    boothRef.current = b
    setSnap(b.snap)
    if (secure) void b.openMic().then(() => Booth.devices().then(setDevices))
    void recover(build).then((names) => names.length && (setRecovered(names), void cur.current.reload()))
    return () => {
      b.dispose()
      boothRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [build, secure])
  useEffect(() => {
    if (boothRef.current) boothRef.current.L = L
  }, [L])
  useEffect(() => {
    boothRef.current?.sync(line)
  }, [line])

  // the takes of this line: the project has them; /api/line adds the ones still being processed, and the neighbours
  const sig = p.sessions.map((s) => s.name + s.state).join()
  useEffect(() => {
    let live = true
    fetchLine(build, line).then((d) => live && setInfo(d), () => {})
    return () => {
      live = false
    }
  }, [build, line, sig])

  const b = boothRef.current
  const rec = !!snap?.recording
  const watching = snap?.watching ?? ''
  const key = useCallback((e: KeyboardEvent) => {
    const b = boothRef.current
    if (!b) return
    const a = document.activeElement as HTMLElement | null
    if (a && (['INPUT', 'TEXTAREA'].includes(a.tagName) || a.isContentEditable)) return
    if (a?.tagName === 'SELECT' && e.key !== 'Escape') return
    if (e.ctrlKey || e.metaKey || e.altKey) return
    const w = b.snap.watching
    if (w) {
      // a take is playing: Space and Esc are its; the keys that move on end it first
      if (e.key === ' ') {
        e.preventDefault()
        return b.toggleWatch()
      }
      if (e.key === 'Escape') {
        e.preventDefault()
        return b.stopWatch()
      }
      if (['ArrowLeft', 'ArrowRight', 'PageUp', 'PageDown', 'l', 'L', 'r', 'R', 't', 'T'].includes(e.key)) b.stopWatch()
    }
    const k = e.key.toLowerCase()
    if (e.key === ' ' || k === 'p') {
      e.preventDefault()
      b.toggle()
    } else if (e.key === 'ArrowRight' || e.key === 'PageDown') {
      e.preventDefault()
      b.next()
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault()
      b.back()
    } else if (k === 'r') void b.toggleRec()
    else if (k === 'x') b.retake()
    else if (k === 'l') b.recordTake()
    else if (k === 't') setShowTakes((s) => !s)
    else if (k === 'n') nextNotes()
    else if (k === 'm') document.getElementById('mic-select')?.focus()
    else if (k === 'f') void (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen()).catch(() => {})
    else if (e.key === 'Escape' && b.snap.count > 0) void b.toggleRec()
  }, [nextNotes])
  useEffect(() => {
    document.addEventListener('keydown', key)
    return () => document.removeEventListener('keydown', key)
  }, [key])

  const text = L[line]?.[1] ?? p.lines[line]?.[1] ?? ''
  const nextText = L[line + 1]?.[1]
  const words = b && b.i === line ? b.words : []
  const said = snap?.said ?? 0
  const takes = p.takes[String(line)] ?? []
  const pending = (info?.line === line ? info.pending : []).filter((x) => !takes.some((t) => t.id === x.id))
  const dur = (L[line + 1]?.[0] ?? (L[line]?.[0] ?? 0) + 8) - (L[line]?.[0] ?? 0)
  const note = snap?.note
  const status = rec
    ? `● REC${b?.snap.mic ? ' — ' + b.snap.mic : ''}${snap && snap.single >= 0 ? ' — one take of line ' + (snap.single + 1) : ''}`
    : uploads.waiting() > 0
      ? 'saving…'
      : ''
  const waiting = uploads.waiting()

  const watchTake = (t: Take, ctx: boolean) => {
    const bb = boothRef.current
    if (!bb) return
    if (!ctx) return bb.watch(t.id, t.tracks, [[t.line, 0, spanOf(t.tracks), t.id]], null)
    void (info?.line === t.line ? Promise.resolve(info) : fetchLine(build, t.line)).then((d) => {
      const c = d.context
      const tracks = glue([c.before, t.tracks, c.after])
      const before = spanOf(c.before)
      bb.watch(t.id, tracks, [[t.line, 0, spanOf(tracks), t.id]], [before, before + spanOf(t.tracks)], Math.max(0, before - 1))
    })
  }

  // a long line never runs out of the prompter: the font shrinks until the whole line fits (down to 15 px), and
  // what still overflows scrolls, keeping the word being said in view
  const nowRef = useRef<HTMLParagraphElement>(null)
  const prompterRef = useRef<HTMLDivElement>(null)
  const [fitTick, setFitTick] = useState(0)
  useEffect(() => {
    const el = prompterRef.current
    if (!el || typeof ResizeObserver === 'undefined') return
    let w = el.clientWidth
    const ro = new ResizeObserver(() => { if (el.clientWidth !== w) { w = el.clientWidth; setFitTick((n) => n + 1) } })
    ro.observe(el)
    return () => ro.disconnect()
  }, [])
  useLayoutEffect(() => {
    const el = nowRef.current
    if (!el) return
    el.style.fontSize = ''
    let size = parseFloat(getComputedStyle(el).fontSize)
    while (el.scrollHeight > el.clientHeight + 1 && size > 15) {
      size -= 1
      el.style.fontSize = `${size}px`
    }
    el.scrollTop = 0
  }, [text, words.length, fitTick])
  useEffect(() => {
    const now = nowRef.current?.querySelector<HTMLElement>('.now')
    if (now) now.scrollIntoView({ block: 'nearest' })
  }, [said])

  return (
    <div className="booth">
      <div className={`booth-stage notes-${notes}`}>
        <div className="screen booth-screen">
          <video ref={videoRef} src={`${p.video}?v=${p.video_version}`} muted playsInline preload="auto" />
          <div className="screen-tag">{watching ? `WATCHING A TAKE · ${snap?.watchClock ?? ''}` : 'PICTURE · the line plays here while you speak'}</div>
          {!!snap?.count && <div className="countin" aria-live="assertive">{snap.count}</div>}
          {rec && <div className="rec-badge"><span className="dot" /> REC <span className="mono">{secs(recSeconds, 0)}</span></div>}
        </div>
        <div className="prompter" aria-label="Teleprompter" ref={prompterRef}>
          <div className="prompter-bar">
            <span className="mono">line {line + 1} / {L.length}</span>
            <span className="dim mono">≈ {secs(dur)}</span>
            {status && <span className={rec ? 'bad' : 'warn'}>{status}{waiting > 2 ? ` — ${waiting} pieces waiting for the server` : ''}</span>}
            {note && <span className="warn">{note}</span>}
            <span className="grow" />
            <IconButton icon="prev" label="Previous line (←)" disabled={rec || !!watching} onClick={() => b?.go(line - 1)} />
            <IconButton icon={snap?.playing ? 'pause' : 'play'} label={snap?.playing ? 'Pause (Space)' : 'Play the line (Space)'} on={!!snap?.playing} onClick={() => b?.toggle()} />
            <IconButton icon="next" label="Next line (→)" onClick={() => b?.next()} />
          </div>
          <p className="prompt-now" data-said={said} ref={nowRef}>
            {words.length === 0 ? (
              <span className="said">{text}</span>
            ) : (
              words.map((x, i) => (
                <span key={i} className={i < said ? 'said' : i === said && snap?.playing ? 'now' : ''}>
                  {x.w}{' '}
                </span>
              ))
            )}
          </p>
          {nextText && (
            <p className="prompt-next">
              <span className="mono">{line + 2}</span> {nextText}
            </p>
          )}
        </div>
      </div>

      <aside className="booth-side">
        <Panel title="Input" actions={level.clip ? <Chip tone="bad" plain>CLIP</Chip> : snap?.mic ? <Chip tone="good" plain>live</Chip> : undefined} className="input-panel">
          <div className="input-box">
            <div className="vmeter">
              <div className="meter-wrap">
                <Meter level={pos(level.rms)} peak={pos(level.peak)} label="Input level" />
              </div>
              <div className="scale mono dim" aria-hidden>
                {[0, -6, -18, -40].map((d) => <span key={d} style={{ bottom: `${pos(d) * 100}%` }}>{d}</span>)}
              </div>
            </div>
            <div className="input-fields">
              <label className="label" htmlFor="mic-select">Microphone</label>
              <select
                id="mic-select"
                value={b?.currentDeviceId ?? ''}
                disabled={rec || !secure}
                onChange={(e) => {
                  e.target.blur()
                  void b?.setMic(e.target.value).then(() => Booth.devices().then(setDevices))
                }}
              >
                {devices.length === 0 && <option value="">{secure ? 'no microphone found' : 'not available'}</option>}
                {devices.map((d, k) => <option key={d.deviceId} value={d.deviceId}>{d.label || `microphone ${k + 1}`}</option>)}
              </select>
              <label className="label" htmlFor="cin">Count-in</label>
              <select id="cin" value={countIn} onChange={(e) => {
                setCountIn(+e.target.value)
                b?.setCountIn(+e.target.value)
                e.target.blur()
              }}>
                <option value={0}>off</option>
                <option value={1}>1 second</option>
                <option value={2}>2 seconds</option>
                <option value={3}>3 seconds</option>
                <option value={5}>5 seconds</option>
              </select>
              <div className="dim label mono" aria-live="off" data-testid="db">
                {level.rms > -100 ? `${level.rms.toFixed(0)} dBFS rms · peak ${level.peak.toFixed(0)}` : '— dBFS'}
              </div>
              {snap?.micError && <div className="bad label">{snap.micError}</div>}
            </div>
          </div>
        </Panel>

        {secure ? (
          <div className="rec-controls">
            <button type="button" className={'rec-big' + (rec ? ' on' : '')} onClick={() => b?.recordTake()} aria-pressed={rec} id="rec-take">
              <span className="rec-ico">{rec ? <Icon name="stop" size={22} /> : <Icon name="rec" size={26} />}</span>
              <span>
                <b>{rec ? (snap && snap.single >= 0 ? 'Stop the take' : 'Stop (L)') : 'Record a take of this line'}</b>
                <small>{rec ? 'it also stops 1 s after the line ends' : <><kbd>L</kbd> the picture plays the line</>}</small>
              </span>
              {rec && <Timecode seconds={recSeconds} rec />}
            </button>
            <div className="btn-row">
              <Button small id="rec-session" onClick={() => void b?.toggleRec()} icon={rec && snap && snap.single < 0 ? 'stop' : 'rec'}>
                {rec && snap && snap.single < 0 ? 'Stop session' : 'Record the whole session'} (R)
              </Button>
              <Button small variant="ghost" onClick={() => b?.retake()} title="the take of the line on screen is a mistake; the line starts over">Mistake (X)</Button>
            </div>
            {snap?.saved && !rec && <div className="good label">saved: <span className="mono">{snap.saved}</span></div>}
            {up.includes('NOT saved') && (
              <div className="bad label">
                {uploads.error()} <button type="button" className="link" onClick={() => uploads.clearError()}>dismiss</button>
              </div>
            )}
            {recovered.length > 0 && <div className="warn label">recovered an unsent recording: {recovered.join(', ')}</div>}
          </div>
        ) : (
          <div className="rec-controls"><p className="bad no-mic" role="alert">{NOMIC}</p></div>
        )}

        {showTakes && (
          <Panel title={<>Takes of line {line + 1}</>} actions={<span className="mono dim">T hides</span>} className="takes-panel">
            <div className="take-strip">
              {takes.length === 0 && pending.length === 0 && <p className="dim pad">No take yet. Press <kbd>L</kbd> to record one; it shows here when processed.</p>}
              {takes.map((t, n) => {
                const used = p.used.includes(t.id)
                const w = watching === t.id
                return (
                  <div key={t.id} className={'strip-take' + (used ? ' used' : '') + (t.rejected ? ' bad' : '')} data-take={t.id}>
                    <b>T{n + 1}</b>
                    <span className="mono">{secs(t.length)}</span>
                    <span className="mono dim" title={t.id}>{when(t.session)}</span>
                    {used && <Chip tone="you">used</Chip>}
                    <span className="grow" />
                    {w ? (
                      <>
                        <span className="mono dim">{snap?.watchClock}</span>
                        <IconButton icon="stop" label="Stop watching" onClick={() => b?.stopWatch()} />
                      </>
                    ) : (
                      <>
                        <IconButton icon="play" label={`Watch T${n + 1}`} disabled={rec} onClick={() => watchTake(t, false)} />
                        <Button small variant="ghost" disabled={rec} onClick={() => watchTake(t, true)} title="the end of the line before, this take, the start of the line after">in context</Button>
                      </>
                    )}
                    {!used && <Button small onClick={() => void act.choose(line, t.id)}>use</Button>}
                    <Button small variant="ghost" onClick={() => void act.edit(t.id, { rejected: !t.rejected })}>{t.rejected ? 'not a mistake' : 'mistake'}</Button>
                    <IconButton icon="trash" label={`Hide T${n + 1}`} onClick={async () => { if (await confirm(HIDE_TAKE)) { if (w) b?.stopWatch(); void act.edit(t.id, { deleted: true }) } }} />
                  </div>
                )
              })}
              {pending.map((x) => (
                <div key={x.id} className="strip-take" data-pending={x.state}>
                  <b>…</b>
                  <span className={x.state === 'failed' ? 'bad' : 'warn'}>
                    {({ recording: 'recording…', recorded: 'waiting…', processing: 'cleaning the voice, converting it to the cloned voice…', failed: 'failed' } as Record<string, string>)[x.state] ?? x.state}
                    {x.state === 'failed' ? ' ' + x.error : ''}
                  </span>
                  <span className="grow" />
                  <span className="dim mono">{when(x.session)} · {secs(x.seconds)}</span>
                </div>
              ))}
            </div>
          </Panel>
        )}

        <Panel title="Recordings of this lecture" className="sessions-panel">
          <ul className="plain pad">
            {p.sessions.map((s) => (
              <li key={s.name}>
                <span className="mono">{s.name}</span>{' '}
                <span className="dim">{s.stale ? 'earlier build of the video: not used' : s.state === 'ready' ? `${(s.seconds / 60).toFixed(1)} min · ${s.clean}` : s.state === 'processing' ? 'cleaning the voice, converting it to the cloned voice…' : s.state === 'recorded' ? 'waiting…' : s.state === 'failed' ? 'failed ' + s.error : `recording… ${s.chunks} s`}</span>
              </li>
            ))}
            {!p.sessions.length && <li className="dim">none yet</li>}
          </ul>
        </Panel>

        <Panel title="Keys" className="keys-panel">
          <dl className="keys">
            {KEYS.map(([k, d]) => (
              <div key={k}><dt><kbd>{k}</kbd></dt><dd>{d}</dd></div>
            ))}
          </dl>
        </Panel>
      </aside>
    </div>
  )
}
