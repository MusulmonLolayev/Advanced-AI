import { useEffect, useRef, useState, type ReactNode } from 'react'
import { useActions } from '../actions'
import { Button, Chip, Icon } from '../components'
import { useStudio } from '../studio'
import { lectureTitle, timecode } from '../util'

function Pop({ trigger, children, label }: { trigger: ReactNode; children: ReactNode; label: string }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!open) return
    const off = (e: MouseEvent) => !ref.current?.contains(e.target as Node) && setOpen(false)
    const esc = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', off)
    document.addEventListener('keydown', esc)
    return () => {
      document.removeEventListener('mousedown', off)
      document.removeEventListener('keydown', esc)
    }
  }, [open])
  return (
    <div className="pop" ref={ref}>
      <button type="button" className="status-btn" aria-expanded={open} aria-label={label} onClick={() => setOpen(!open)}>
        {trigger}
      </button>
      {open && <div className="pop-body">{children}</div>}
    </div>
  )
}

export function TopBar({ toggleBrowser }: { toggleBrowser: () => void }) {
  const { boothOn, setBoothOn, panel, setPanel, stem, lang, open, project, recording, recSeconds, overview } = useStudio()
  const mod = overview?.find((m) => m.lectures.some((l) => l.stem === stem))
  const lec = mod?.lectures.find((l) => l.stem === stem)
  const vs = project?.voice_server
  const act = useActions()
  const jobs = project?.jobs ?? []
  const running = jobs.filter((j) => j.state === 'queued' || j.state === 'running')
  return (
    <header className="topbar">
      <button type="button" className="icon-btn" title="Show or hide the project browser" aria-label="Show or hide the project browser" onClick={toggleBrowser}>
        <Icon name="sidebar" />
      </button>
      <div className="mark" aria-label="Studio">
        <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="11" fill="var(--accent)" />
          <path d="M5 12h2M8.5 9v6M12 6v12M15.5 9v6M19 12h-2" stroke="var(--accent-ink)" strokeWidth="2" strokeLinecap="round" />
        </svg>
        <span>Studio</span>
      </div>
      <nav className="crumbs" aria-label="Project">
        <span className="dim mod-crumb">Module {mod?.k ?? '…'}</span>
        <Icon name="chevron" size={12} className="mod-crumb" />
        <span>{lec ? lectureTitle(lec.n) : stem}</span>
        <Icon name="chevron" size={12} />
        <label className="lang-switch">
          <Icon name="globe" size={14} />
          <select value={lang} aria-label="Language" onChange={(e) => open(stem, e.target.value)}>
            {(lec?.langs ?? [{ lang, name: lang, lines: { approved: 0, total: 0 } }]).map((l) => (
              <option key={l.lang} value={l.lang}>
                {l.name} · {l.lines.approved}/{l.lines.total}
              </option>
            ))}
          </select>
        </label>
      </nav>
      <div className="grow" />
      <button type="button" className={'top-btn rec-toggle' + (boothOn ? ' on' : '')} aria-pressed={boothOn} title={boothOn ? 'Record is on: the monitor is the booth. Turn it off to go back to the monitor (B)' : 'Turn the monitor into the recording booth (B). L records one take of the selected line'} onClick={() => setBoothOn(!boothOn)}>
        <span className="dot" />Record
      </button>
      <button type="button" className={'top-btn' + (panel === 'script' ? ' on' : '')} aria-pressed={panel === 'script'} title="The narration in every language: approve, edit, build (S)" onClick={() => setPanel(panel === 'script' ? null : 'script')}>
        Script &amp; languages
      </button>
      <button type="button" className={'top-btn' + (panel === 'export' ? ' on' : '')} aria-pressed={panel === 'export'} title="Export the lecture with your takes, watch it, download it (E)" onClick={() => setPanel(panel === 'export' ? null : 'export')}>
        Export
      </button>
      <div className="grow" />
      <div className={'rec-state' + (recording ? ' on' : '')} role="status" aria-label={recording ? 'Recording' : 'Not recording'}>
        <span className="dot" />
        {recording ? (
          <>
            <b>REC</b>
            <span className="mono">{timecode(recSeconds, false)}</span>
          </>
        ) : (
          <span>idle</span>
        )}
      </div>
      <Pop label="Voice server" trigger={<><Icon name="server" size={14} /><span className={vs?.up ? 'good' : 'dim'}>voice<span className="wide-only"> {vs?.up ? 'up' : 'off'}</span></span></>}>
        <h4>Cloned voice server</h4>
        <p>
          {vs?.up ? <Chip tone="good">running</Chip> : <Chip tone="empty">off</Chip>} {vs?.pid ? <span className="dim mono">pid {vs.pid}</span> : null}
        </p>
        <p className="dim">Re-voicing starts it when needed. It uses the GPU while it runs.</p>
        {vs && (vs.up ? (
          vs.pid ? <Button small onClick={() => void act.voiceServer('stop')}>stop</Button> : <span className="dim">(not started here)</span>
        ) : (
          <Button small onClick={() => void act.voiceServer('start')}>start</Button>
        ))}
      </Pop>
      <Pop label="Jobs" trigger={<><Icon name="jobs" size={14} /><span className={running.length ? 'warn' : 'dim'}>{running.length ? `${running.length} running` : <>jobs<span className="wide-only"> idle</span></>}</span></>}>
        <h4>Jobs</h4>
        <ul className="jobs">
          {jobs.slice(-6).reverse().map((j, i) => (
            <li key={i}>
              <span>{j.kind}</span> <span className="dim">{j.key.slice(0, 28)}</span> <span className={j.state === 'failed' ? 'bad' : j.state === 'done' ? 'good' : 'warn'}>{j.state}</span>
              <div className="dim">{j.error || j.detail}</div>
            </li>
          ))}
          {!jobs.length && <li className="dim">none</li>}
        </ul>
      </Pop>
    </header>
  )
}
