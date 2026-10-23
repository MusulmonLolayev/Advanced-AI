import { useMemo, useState } from 'react'
import { useActions } from '../actions'
import { Button, Chip, Icon, Panel } from '../components'
import { makeup } from '../makeup'
import { lineStates } from '../model'
import { useStudio } from '../studio'
import { cls, mb, secs, timecode } from '../util'
import { EmptyState } from './EmptyState'
import { LanguageBuilds } from './LanguageBuilds'

const CLEAN: [string, string][] = [
  ['cloned', 'Your take re-spoken in the cloned voice: your timing and pronunciation, the cloned voice\'s clean sound. Needs the voice server (GPU); about 6 times faster than real time (1 min of speech takes about 10 s). The default.'],
  ['deepfilter', 'Neural denoiser, the cleanest of the filters (DNSMOS 3.2 vs 2.2 for voice on your first recording; about 5 min per 30 min).'],
  ['voice', 'Filters tuned for speech.'],
  ['mild', 'Lighter cleaning.'],
  ['strong', 'For a noisy room.'],
  ['off', 'Low cut only.'],
]
const when = (s: number) => new Date(s * 1000).toLocaleString([], { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false })

/** the voice cleaning chosen last is remembered in this browser (the old editor's key) */
const readClean = () => {
  try {
    const c = localStorage.getItem('studioClean')
    return CLEAN.some(([k]) => k === c) ? (c as string) : 'cloned'
  } catch {
    return 'cloned'
  }
}

export function ExportMode() {
  const { project, projectLoading, build, setMode, watch, setWatch } = useStudio()
  const act = useActions()
  const [clean, setCleanState] = useState(readClean)
  const setClean = (c: string) => {
    setCleanState(c)
    try {
      localStorage.setItem('studioClean', c)
    } catch {
      /* not remembered */
    }
  }
  const missing = project?.settings.missing ?? 'original'
  const m = useMemo(() => (project ? makeup(project) : null), [project])
  const exporting = !!project?.jobs.some((j) => j.kind === 'export' && (j.state === 'queued' || j.state === 'running'))
  const lectureUrl = project ? `/${build}/${build}.mp4?v=${project.video_version}` : ''
  // what plays inline: the lecture video, a finished export (its URL), or a recording built the old way (its name)
  const watching = !watch ? null : watch === 'lecture' ? { url: lectureUrl, title: `the lecture video ${build}` } : watch.startsWith('/') ? { url: watch, title: watch.split('/').pop() ?? watch } : { url: `/${build}/presenter/recordings/${watch}.mp4`, title: `recording ${watch}` }

  return (
    <div className="export">
      <div className="export-col">
        <Panel title="Export settings" className="settings-panel">
          <div className="pad stack">
            <fieldset className="radio-cards">
              <legend className="label">Voice cleaning</legend>
              {CLEAN.map(([k, d]) => (
                <label key={k} className={cls('rcard', clean === k && 'on')}>
                  <input type="radio" name="clean" checked={clean === k} onChange={() => setClean(k)} />
                  <span><b>{k}</b>{k === 'cloned' && <Chip tone="accent" plain>default</Chip>}<small>{d}</small></span>
                </label>
              ))}
            </fieldset>
            <fieldset className="radio-cards">
              <legend className="label">Lines you have not recorded</legend>
              {([['original', 'Original voice', 'The lecture video’s own narration (cloned or synthetic), brought to −19 LUFS like your takes.'], ['silent', 'Silent', 'Nothing plays; the picture runs on.']] as const).map(([k, t, d]) => (
                <label key={k} className={cls('rcard', missing === k && 'on')}>
                  <input type="radio" name="missing" checked={missing === k} disabled={!project} onChange={() => void act.setting('missing', k)} />
                  <span><b>{t}</b><small>{d}</small></span>
                </label>
              ))}
            </fieldset>
            <p className="dim sub">Line ends keep {project?.settings.margin ?? '0.3'} s around the voice (set in Edit). One fixed gain to −19 LUFS plus a peak limiter, picture via NVENC.</p>
          </div>
        </Panel>
      </div>

      <div className="export-col wide">
        <Panel title="What the export will contain" actions={<span className="mono dim">{project?.build}</span>} className="makeup-panel">
          {projectLoading && <EmptyState title="Loading…" />}
          {!projectLoading && !m && <EmptyState title="Nothing to export yet"><p className="dim">There is no presenter page for this build.</p></EmptyState>}
          {project && m && (
            <div className="pad stack">
              <div className="stats">
                <div className="stat"><span className="n you" data-testid="n-you">{m.you}</span><span>lines are <b>your takes</b></span><small className="mono dim">{timecode(m.youSec, false)} of voice</small></div>
                <div className="stat"><span className="n clone" data-testid="n-rest">{m.rest}</span><span>{missing === 'original' ? <>lines are the <b>cloned voice</b></> : <>lines are <b>silent</b></>}</span><small className="mono dim">of {m.n} lines</small></div>
                <div className="stat"><span className="n">{timecode(m.total, false)}</span><span>total length</span><small className="mono dim">{secs(m.total, 0)}</small></div>
                <div className="stat"><span className="n good">{secs(m.saved)}</span><span>saved by tightening</span><small className="mono dim">{secs(m.could)} more could be saved</small></div>
              </div>
              <div>
                <div className="label">The edit list, line by line</div>
                <div className="mix" role="img" aria-label={`${m.you} of ${m.n} lines are your takes`}>
                  {lineStates(project, null).map((s, k) => (
                    <i key={k} className={s.kind} style={{ flexGrow: Math.max(0.2, s.b - s.a) }} title={`line ${k + 1}: ${s.kind === 'take' ? 'your take' : s.kind === 'clone' ? 'cloned voice' : s.kind}`} />
                  ))}
                </div>
                <div className="legend"><i style={{ background: 'var(--track-you)' }} /> your take <i style={{ background: 'var(--track-clone)' }} /> cloned voice <i style={{ background: 'var(--line-strong)' }} /> silent / mistake</div>
              </div>
              <div className="dim sub">Writes <span className="mono">presenter/export/{project.build}_edited.mp4</span>, <span className="mono">.srt</span> and <span className="mono">.chapters.txt</span> from the same edit list. Voice cleaning: <b>{clean}</b>.</div>
              <div className="btn-row">
                <Button variant="primary" icon="download" disabled={exporting} id="export-now" onClick={() => void act.exportNow(clean)}>{exporting ? 'Exporting…' : 'Export'}</Button>
                <Button variant="ghost" onClick={() => setMode('edit')}>Review in Edit</Button>
                <Button variant="ghost" icon="film" onClick={() => setWatch(watch === 'lecture' ? '' : 'lecture')}>Watch the lecture video</Button>
                <a className="btn ghost" href={`/${project.build}/${project.build}.mp4`} download={`${project.build}.mp4`} id="download-lecture"><Icon name="download" size={14} />Download the lecture video</a>
              </div>
            </div>
          )}
        </Panel>

        {watching && (
          <Panel title={<>Watching · <span className="mono">{watching.title}</span></>} actions={<Button small variant="ghost" onClick={() => setWatch('')}>close</Button>} className="watch-panel">
            <video key={watching.url} className="watch-video" src={watching.url} controls autoPlay preload="metadata" />
            <p className="dim sub pad"><a href={`/lecture?build=${build}`} target="_blank" rel="noreferrer">open on its own page</a></p>
          </Panel>
        )}

        <Panel title="Build a video in another language" className="langs-panel">
          <LanguageBuilds />
        </Panel>
      </div>

      <div className="export-col">
        <Panel title="Queue" actions={<span className="mono dim">{project?.jobs.filter((j) => j.state === 'queued' || j.state === 'running').length ?? 0} running</span>} className="queue-panel">
          <ul className="plain jobs-list">
            {[...(project?.jobs ?? [])].reverse().slice(0, 10).map((j, i) => (
              <li key={i} data-kind={j.kind} data-state={j.state}>
                <span className={cls('led', j.state === 'done' ? 'good' : j.state === 'failed' ? 'bad' : 'warn')} />
                <span className="grow"><b>{j.kind}</b> <span className="dim mono">{j.key.slice(0, 26)}</span> <span className={j.state === 'failed' ? 'bad' : j.state === 'done' ? 'good' : 'warn'}>{j.state}</span><small className="dim">{j.error || j.detail}</small></span>
                <span className="mono dim">{when(j.updated)}</span>
              </li>
            ))}
            {!project?.jobs.length && <li className="dim">nothing queued</li>}
          </ul>
        </Panel>
        <Panel title="Exports" className="history-panel">
          <ul className="plain exp-list">
            {project?.exports.map((f) => {
              const video = f.name.endsWith('.mp4')
              return (
                <li key={f.name}>
                  <Icon name="film" size={14} />
                  <span className="grow"><a href={f.url} {...(video ? { target: '_blank', rel: 'noreferrer' } : { download: true })}>{f.name}</a><small className="dim mono">{mb(f.size)} · {when(f.time)}</small></span>
                  {video && <Button small variant="ghost" onClick={() => setWatch(f.url)}>watch</Button>}
                  <a className="btn small ghost" href={f.url} download aria-label={`Download ${f.name}`}><Icon name="download" size={12} /></a>
                </li>
              )
            })}
            {!project?.exports.length && <li className="dim">none yet</li>}
          </ul>
        </Panel>
      </div>
    </div>
  )
}
