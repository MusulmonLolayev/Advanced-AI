import { useEffect, useState, type ReactNode } from 'react'
import { postPrepare } from '../api'
import { Button, useToast } from '../components'
import { useStudio } from '../studio'

export function EmptyState({ title, children, tone }: { title: string; children?: ReactNode; tone?: 'bad' }) {
  return (
    <div className="empty-state">
      <h2 className={tone}>{title}</h2>
      {children}
    </div>
  )
}

/** A build with no presenter page yet (presenter.py writes lines.json and the silent video): "Prepare presenter page" starts
 *  it and the project is fetched every 3 s until it exists. A language with no video asks for the build first. */
export function NoPresenter({ what }: { what: string }) {
  const { build, stem, lang, projectError, reload, overview } = useStudio()
  const toast = useToast()
  const [started, setStarted] = useState(false)
  const row = overview?.flatMap((m) => m.lectures).find((l) => l.stem === stem)?.langs.find((l) => l.lang === lang)
  const preparing = started || /\(running\)/.test(projectError ?? '')
  useEffect(() => {
    if (!preparing) return
    const t = setInterval(() => void reload(), 3000)
    return () => clearInterval(t)
  }, [preparing, reload])
  const failed = /failed/.test(projectError ?? '')
  return (
    <EmptyState title={`No ${what} for ${stem} · ${lang} yet`} tone={failed ? 'bad' : undefined}>
      {failed && <p className="bad">{projectError}</p>}
      {row && !row.build ? (
        <p>{build} has no video yet: build it first (Script & languages, or Export).</p>
      ) : (
        <>
          <p>{build} has no presenter page (its line timings and the silent video), so there is nothing to {what === 'editor' ? 'edit' : 'record'}.</p>
          <Button
            variant="primary"
            disabled={preparing && !failed}
            onClick={() => {
              setStarted(true)
              postPrepare(build).then(
                () => toast('Preparing the presenter page: about a minute'),
                (e: Error) => (setStarted(false), toast(`Failed: ${e.message}`)),
              )
            }}
          >
            {preparing && !failed ? 'Preparing…' : 'Prepare presenter page'}
          </Button>
        </>
      )}
    </EmptyState>
  )
}
