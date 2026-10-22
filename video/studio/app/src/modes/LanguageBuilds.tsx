import { useActions } from '../actions'
import { Button, Chip, Icon } from '../components'
import { useStudio } from '../studio'
import type { LangSummary } from '../types'
import { cls } from '../util'

/** The state of a language's build, in words (the lecture page's row). */
export function buildState(l: LangSummary): { label: string; tone: 'good' | 'warn' | 'bad' | 'accent' | 'empty' } {
  const b = l.builds.find((x) => x.built)
  if (b) return { label: 'built', tone: 'accent' }
  if (l.job && (l.job.state === 'queued' || l.job.state === 'running')) return { label: 'building', tone: 'warn' }
  return { label: 'no video', tone: 'empty' }
}

/** One row per language of the lecture: its approval, its video, and Build video / Build draft video with the server's reason when it refuses. */
export function LanguageBuilds({ compact }: { compact?: boolean }) {
  const { lec, stem, lang, open } = useStudio()
  const act = useActions()
  if (!lec) return <p className="dim pad">Loading the languages…</p>
  return (
    <>
      <table className={cls('ltable', compact && 'compact')}>
        <tbody>
          {lec.langs.map((l) => {
            const p = l.plan
            const built = l.builds.find((b) => b.built)
            const running = !!l.job && (l.job.state === 'queued' || l.job.state === 'running')
            const left = l.lines.total - l.lines.approved + (l.labels.total - l.labels.approved)
            const st = buildState(l)
            return (
              <tr key={l.lang} className={l.lang === lang ? 'cur' : ''} data-lang={l.lang}>
                <td><b>{l.name}</b>{l.native !== l.name && <span className="dim"> {l.native}</span>}</td>
                <td className="mono dim">{p.build}</td>
                <td>
                  <Chip tone={st.tone}>{st.label}</Chip>{' '}
                  <Chip tone={left === 0 && l.has_narration ? 'good' : 'warn'}>{l.lines.approved}/{l.lines.total} lines · {l.labels.approved}/{l.labels.total} labels</Chip>
                </td>
                <td className="cell-r">
                  {built ? (
                    <Button small variant="ghost" onClick={() => open(stem, l.lang)}>Open</Button>
                  ) : (
                    <Button small variant={p.can ? 'primary' : 'ghost'} disabled={!p.can || running} onClick={() => void act.buildLanguage(l.lang)} title={p.can ? '' : p.reasons.join('; ')}>
                      {p.draft ? 'Build draft video' : 'Build video'}
                    </Button>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {lec.langs.map((l) => {
        const p = l.plan
        if (l.builds.some((b) => b.built)) return null
        const job = l.job
        return (
          <div key={l.lang} className="build-note" data-lang={l.lang}>
            {p.approval === 'refused' && (
              <p className="bad sub"><Icon name="warn" size={12} /> {l.name}: not built, not voiced. {p.reasons.join('; ') || 'Uzbek is built only when every line and label is approved.'}</p>
            )}
            {p.approval !== 'refused' && !p.can && p.reasons.length > 0 && <p className="bad sub"><Icon name="warn" size={12} /> {l.name}: {p.reasons.join('; ')}</p>}
            {p.can && p.draft && <p className="warn sub"><Icon name="warn" size={12} /> {l.name}: {p.unapproved.lines} lines and {p.unapproved.labels} labels are not approved: the frames carry a draft tag.</p>}
            {job && <p className={cls('sub', job.state === 'failed' ? 'bad' : job.state === 'done' ? 'good' : 'warn')}>build job: {job.state} <span className="dim">{(job.error || job.detail || '').slice(0, 300)}</span></p>}
          </div>
        )
      })}
    </>
  )
}
