import { useEffect, useState } from 'react'
import { Chip, Icon, IconButton } from '../components'
import { useStudio } from '../studio'
import type { LangRow, ModuleRow } from '../types'
import { cls, lectureTitle } from '../util'

function LangStatus({ l }: { l: LangRow }) {
  const done = l.lines.approved === l.lines.total
  return (
    <span className="chips">
      <Chip tone={done && l.has_narration ? 'good' : 'warn'} title={`narration approved ${l.lines.approved} of ${l.lines.total}`}>
        {l.lines.approved}/{l.lines.total}
      </Chip>
      {l.build ? (
        <Chip tone="accent" plain title={l.built_on ? `built ${new Date(l.built_on * 1000).toLocaleDateString([], { day: 'numeric', month: 'short' })}` : 'built'}>
          built
        </Chip>
      ) : (
        <Chip tone="empty" plain title="no video yet">
          no video
        </Chip>
      )}
      {l.sessions > 0 && (
        <Chip tone="you" plain title="recording sessions of this build">
          {l.sessions} recording{l.sessions > 1 ? 's' : ''}
        </Chip>
      )}
    </span>
  )
}

export function ProjectBrowser({ collapsed, onExpand }: { collapsed: boolean; onExpand: () => void }) {
  const { stem, lang, open, overview } = useStudio()
  const mods: ModuleRow[] = overview ?? []
  const cur = mods.find((m) => m.lectures.some((l) => l.stem === stem))
  const [openMods, setOpenMods] = useState<Set<number>>(new Set([cur?.k ?? 0]))
  const [openLecs, setOpenLecs] = useState<Set<string>>(new Set([stem]))
  // the open lecture's module and lecture are open (also when the list arrives after the address, or the address changes)
  useEffect(() => {
    if (!cur) return
    setOpenMods((s) => (s.has(cur.k) ? s : new Set(s).add(cur.k)))
    setOpenLecs((s) => (s.has(stem) ? s : new Set(s).add(stem)))
  }, [cur?.k, stem]) // eslint-disable-line react-hooks/exhaustive-deps
  const flip = <T,>(s: Set<T>, v: T, set: (x: Set<T>) => void) => {
    const n = new Set(s)
    n.has(v) ? n.delete(v) : n.add(v)
    set(n)
  }
  if (collapsed)
    return (
      <aside className="browser rail" aria-label="Project browser (collapsed)">
        <IconButton icon="folder" label="Open the project browser" onClick={onExpand} />
        {mods.filter((m) => m.lectures.length).map((m) => (
          <button key={m.k} type="button" className={cls('rail-mod', m.k === cur?.k && 'on')} title={`Module ${m.k} · ${m.title}`} onClick={onExpand}>
            {m.k}
          </button>
        ))}
      </aside>
    )
  return (
    <aside className="browser" aria-label="Project browser">
      <div className="browser-head">Project</div>
      <div className="browser-body">
        {!overview && <p className="dim pad">Loading the lectures…</p>}
        {mods.map((m) => {
          const isOpen = openMods.has(m.k) && m.lectures.length > 0
          return (
            <div key={m.k} className="tree-mod">
              <button type="button" className={cls('tree-row mod', m.lectures.length === 0 && 'empty')} aria-expanded={isOpen} onClick={() => m.lectures.length && flip(openMods, m.k, setOpenMods)}>
                <Icon name="chevron" size={12} className={isOpen ? 'turn' : ''} />
                <span className="grow">
                  <b>Module {m.k}</b> <span className="dim">{m.title}</span>
                </span>
                <span className="dim count">{m.lectures.length ? m.lectures.length : '—'}</span>
              </button>
              {isOpen && (
                <div className="tree-row files" title="the module's shared files (slides PDF)">
                  <Icon name="film" size={12} />
                  <span className="grow dim">
                    Files:{' '}
                    {m.files.length
                      ? m.files.map((f, k) => (
                          <span key={f.name}>
                            {k > 0 && ', '}
                            <a href={f.url} target="_blank" rel="noreferrer" title={`${(f.size / 1e6).toFixed(1)} MB`}>{f.name}</a>
                          </span>
                        ))
                      : 'nothing shared yet'}
                  </span>
                </div>
              )}
              {isOpen &&
                m.lectures.map((l) => {
                  const lecOpen = openLecs.has(l.stem)
                  return (
                    <div key={l.stem}>
                      <button type="button" className={cls('tree-row lec', l.stem === stem && 'cur')} aria-expanded={lecOpen} onClick={() => flip(openLecs, l.stem, setOpenLecs)}>
                        <Icon name="chevron" size={12} className={lecOpen ? 'turn' : ''} />
                        <span className="grow">{lectureTitle(l.n)}</span>
                        {l.langs.some((x) => x.build) && <Icon name="film" size={12} />}
                      </button>
                      {lecOpen &&
                        l.langs.map((x) => (
                          <button key={x.lang} type="button" className={cls('tree-row langrow', l.stem === stem && x.lang === lang && 'sel')} onClick={() => open(l.stem, x.lang)}>
                            <span className="lang-name">{x.name}</span>
                            <LangStatus l={x} />
                          </button>
                        ))}
                    </div>
                  )
                })}
            </div>
          )
        })}
      </div>
    </aside>
  )
}
