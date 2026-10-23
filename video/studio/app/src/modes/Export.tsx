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

const hhmm = (s: number) => new Date(s * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
/** a file's URL with its modification time, so a browser never serves an older file of the same name from its cache */
const fresh = (f: { url: string; time: number }) => `${f.url}?v=${Math.round(f.time)}`
const profileName = (c: string) => (c === 'cloned' ? 'cloned voice' : c ? `your voice (${c})` : 'voice profile not recorded')

export function ExportMode() {
  const { project, projectLoading, build, setPanel, watch, setWatch, setRewriteLine, setLine } = useStudio()
  const act = useActions()
  // the voice cleaning defaults to what the lecture's recordings actually use ("cloned" if any is), and is not kept per browser:
  // a choice from an earlier day must not put your own voice back over recordings that are cloned now
  const ready = (project?.sessions ?? []).filter((x) => x.state === 'ready' && !x.stale)
  const counts = ready.reduce<Record<string, number>>((o, x) => ({ ...o, [x.clean || 'unknown']: (o[x.clean || 'unknown'] ?? 0) + 1 }), {})
  const usual = counts.cloned ? 'cloned' : (Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'cloned')
  const [pick, setClean] = useState<string | null>(null)
  const clean = pick ?? (CLEAN.some(([k]) => k === usual) ? usual : 'cloned')
  const mixed = Object.keys(counts).length > 1
  const nCloned = counts.cloned ?? 0
  const nOwn = ready.length - nCloned
  // cloned-voice versions that are ready but not merged: the export still has the lecture video's old line
  const unmerged = Object.entries(project?.versions ?? {}).flatMap(([scene, vs]) => vs.filter((v) => v.state === 'ready').map((v) => ({ scene, v, line: +(v.changed[0] ?? project?.scenes.indexOf(scene) ?? 0) })))
  const newest = [...(project?.exports ?? [])].filter((f) => f.name.endsWith('.mp4')).sort((a, b) => b.time - a.time)[0]
  const missing = project?.settings.missing ?? 'original'
  const m = useMemo(() => (project ? makeup(project) : null), [project])
  const exporting = !!project?.jobs.some((j) => j.kind === 'export' && (j.state === 'queued' || j.state === 'running'))
  const lectureUrl = project ? `/${build}/${build}.mp4?v=${project.video_version}` : ''
  // what plays inline: the lecture video, a finished export (its URL), or a recording built the old way (its name)
  const watching = !watch ? null : watch === 'lecture' ? { url: lectureUrl, title: `the original build ${build}` } : watch.startsWith('/') ? { url: watch, title: watch.split('/').pop() ?? watch } : { url: `/${build}/presenter/recordings/${watch}.mp4`, title: `recording ${watch}` }

  return (
    <div className="export-wrap">
    <div className="export-top" data-testid="export-top">
      {newest ? (
        <>
          <a className="btn primary" id="download-export" href={fresh(newest)} download={newest.name}><Icon name="download" size={14} />Download the export ({hhmm(newest.time)}, {mb(newest.size)})</a>
          <span className="dim sub">{profileName(newest.profile ?? '')} · <Button small variant="ghost" icon="film" onClick={() => setWatch(fresh(newest))}>watch it</Button></span>
        </>
      ) : (
        <span className="dim">No export yet: press Export below.</span>
      )}
    </div>
    <div className="export">
      <div className="export-col">
        <Panel title="Export settings" className="settings-panel">
          <div className="pad stack">
            <fieldset className="radio-cards">
              <legend className="label">Voice cleaning</legend>
              {CLEAN.map(([k, d]) => (
                <label key={k} className={cls('rcard', clean === k && 'on')}>
                  <input type="radio" name="clean" checked={clean === k} onChange={() => setClean(k)} />
                  <span><b>{k}</b>{k === usual && <Chip tone="accent" plain>your recordings</Chip>}<small>{d}</small></span>
                </label>
              ))}
            </fieldset>
            {mixed && <p className="warn sub" data-testid="mixed-profiles">{nCloned} recording{nCloned === 1 ? ' is' : 's are'} cloned, {nOwn} {nOwn === 1 ? 'is' : 'are'} your voice: convert {nOwn === 1 ? 'it' : 'them'} in Recordings… (timeline bar), or the export uses each as it is.</p>}
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
              {unmerged.length > 0 && (
                <div className="update-banner" role="alert" data-testid="unmerged">
                  <span>
                    <b>{unmerged.length} rewritten line{unmerged.length === 1 ? ' is' : 's are'} ready but not merged into the lecture video:</b>{' '}
                    {unmerged.map((u) => `${u.scene} v${u.v.n} (line ${u.line + 1})`).join(', ')} — merge {unmerged.length === 1 ? 'it' : 'them'} first, or the export uses the old line{unmerged.length === 1 ? '' : 's'}.
                  </span>
                  <Button small onClick={() => { setLine(unmerged[0].line); setPanel(null); setRewriteLine(unmerged[0].line) }} title="close Export and open that line's Rewrite dialog (merge is there)">Open</Button>
                </div>
              )}
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
                <Button variant="ghost" onClick={() => setPanel(null)}>Review in the workspace</Button>
                <Button variant="ghost" icon="film" onClick={() => setWatch(watch === 'lecture' ? '' : 'lecture')} title="the video as it was built, before your recordings and edits">Watch the original build</Button>
                <a className="btn ghost" href={lectureUrl} download={`${project.build}.mp4`} id="download-lecture"><Icon name="download" size={14} />Download the original build (before your edits)</a>
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
                  <span className="grow"><a href={fresh(f)} {...(video ? { target: '_blank', rel: 'noreferrer' } : { download: true })}>{f.name}</a><small className="dim mono">{mb(f.size)} · {when(f.time)} · {profileName(f.profile ?? '')}</small></span>
                  {video && <Button small variant="ghost" onClick={() => setWatch(fresh(f))}>watch</Button>}
                  <a className="btn small ghost" href={fresh(f)} download aria-label={`Download ${f.name}`}><Icon name="download" size={12} /></a>
                </li>
              )
            })}
            {!project?.exports.length && <li className="dim">none yet</li>}
          </ul>
        </Panel>
      </div>
    </div>
    </div>
  )
}
