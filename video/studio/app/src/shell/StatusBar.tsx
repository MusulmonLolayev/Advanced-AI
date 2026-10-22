import { Icon } from '../components'
import { MAKING } from '../model'
import { useStudio } from '../studio'

const when = (s: number) => new Date(s * 1000).toLocaleString([], { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false })

const builds0 = (lec: ReturnType<typeof useStudio>['lec']) => (lec?.langs ?? []).filter((l) => l.job && (l.job.state === 'queued' || l.job.state === 'running')).length

export function StatusBar() {
  const { project, projectError, projectLoading, recording, lec } = useStudio()
  const jobs = project?.jobs ?? []
  const live = jobs.filter((j) => j.state === 'queued' || j.state === 'running')
  const running = live.length + builds0(lec)
  const making = Object.entries(project?.versions ?? {}).flatMap(([scene, vs]) => vs.filter((v) => MAKING.includes(v.state)).map((v) => `${scene} v${v.n} ${v.state}`))
  const builds = (lec?.langs ?? []).filter((l) => l.job && (l.job.state === 'queued' || l.job.state === 'running')).map((l) => `build ${l.plan.build}: ${l.job!.detail || l.job!.state}`)
  const failed = jobs.filter((j) => j.state === 'failed' && Date.now() / 1000 - j.updated < 3600).slice(-1)[0]
  const now = [...live.map((j) => `${j.kind}${j.key ? ' ' + j.key.slice(0, 24) : ''} ${j.state}`), ...making, ...builds].slice(0, 2).join(' · ')
  const last = project?.sessions.filter((s) => s.state === 'ready').slice(-1)[0]
  const answering = !projectError || !projectError.includes('did not answer')
  return (
    <footer className="statusbar">
      <span title="jobs queued or running"><Icon name="jobs" size={12} /> jobs: {running ? <b className="warn">{running} running</b> : <span>0 running</span>} · {jobs.filter((j) => j.state === 'done').length} done</span>
      {now && <span className="warn" title="what the server is making now">{now}</span>}
      {failed && <span className="bad" title={failed.error}>last job failed: {failed.kind}</span>}
      <span title="background tasks: voice check, level cache, words">background: {project ? (project.sessions.some((s) => s.state === 'processing') ? 'processing a recording' : 'idle') : '…'}</span>
      <span className={answering ? 'good' : 'bad'}><span className="led" /> server {projectLoading ? 'connecting…' : answering ? 'answering' : 'not answering'}</span>
      <span className="grow" />
      {recording && <span className="bad">● recording: the takes panel is closed</span>}
      <span title="the newest recording the server finished">last saved recording: {last ? <span className="mono">{when(last.updated)} · {(last.seconds / 60).toFixed(1)} min · {last.clean}</span> : 'none'}</span>
    </footer>
  )
}
