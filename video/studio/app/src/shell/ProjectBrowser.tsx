import { useState } from 'react'
import { Chip, Icon, IconButton } from '../components'
import { FILES, LANGUAGES, LECTURES, MODULES, lectureTitle, type LangRow } from '../snapshot'
import { useStudio } from '../studio'
import type { LectureLangs } from '../types'
import { cls } from '../util'

function LangStatus({ l }: { l: LangRow }) {
  const done = l.approved === l.total
  return (
    <span className="chips">
      <Chip tone={done ? 'good' : 'warn'} title={`narration approved ${l.approved} of ${l.total}`}>
        {l.approved}/{l.total}
      </Chip>
      {l.build ? (
        <Chip tone="accent" plain title={`built ${l.builtOn}`}>
          built
        </Chip>
      ) : (
        <Chip tone="empty" plain title="no video yet">
          no video
        </Chip>
      )}
      {l.takes > 0 && (
        <Chip tone="you" plain title="lines with a recorded take">
          {l.takes} take{l.takes > 1 ? 's' : ''}
        </Chip>
      )}
    </span>
  )
}

/** the lecture's language rows: the snapshot, or the live ones for the open lecture (after an approval or a build) */
function langRows(l: (typeof LECTURES)[number], live: LectureLangs | null): LangRow[] {
  if (!live) return l.langs
  return live.langs.map((x) => {
    const old = l.langs.find((r) => r.code === x.lang)
    const b = x.builds.find((y) => y.built)
    return { code: x.lang, approved: x.lines.approved, total: x.lines.total, labelsApproved: x.labels.approved, labelsTotal: x.labels.total, build: b?.build ?? null, builtOn: b?.when ? new Date(b.when * 1000).toLocaleDateString([], { day: 'numeric', month: 'short' }) : null, takes: old?.takes ?? 0, sessions: b?.sessions ?? 0 }
  })
}

export function ProjectBrowser({ collapsed, onExpand }: { collapsed: boolean; onExpand: () => void }) {
  const { stem, lang, open, lec } = useStudio()
  const cur = LECTURES.find((l) => l.stem === stem)
  const [openMods, setOpenMods] = useState<Set<number>>(new Set([cur?.module ?? 0]))
  const [openLecs, setOpenLecs] = useState<Set<string>>(new Set([stem]))
  const flip = <T,>(s: Set<T>, v: T, set: (x: Set<T>) => void) => {
    const n = new Set(s)
    n.has(v) ? n.delete(v) : n.add(v)
    set(n)
  }
  if (collapsed)
    return (
      <aside className="browser rail" aria-label="Project browser (collapsed)">
        <IconButton icon="folder" label="Open the project browser" onClick={onExpand} />
        {MODULES.filter((m) => LECTURES.some((l) => l.module === m.k)).map((m) => (
          <button key={m.k} type="button" className={cls('rail-mod', m.k === cur?.module && 'on')} title={`Module ${m.k} · ${m.name}`} onClick={onExpand}>
            {m.k}
          </button>
        ))}
      </aside>
    )
  return (
    <aside className="browser" aria-label="Project browser">
      <div className="browser-head">Project</div>
      <div className="browser-body">
        {MODULES.map((m) => {
          const lecs = LECTURES.filter((l) => l.module === m.k)
          const isOpen = openMods.has(m.k) && lecs.length > 0
          return (
            <div key={m.k} className="tree-mod">
              <button type="button" className={cls('tree-row mod', lecs.length === 0 && 'empty')} aria-expanded={isOpen} onClick={() => lecs.length && flip(openMods, m.k, setOpenMods)}>
                <Icon name="chevron" size={12} className={isOpen ? 'turn' : ''} />
                <span className="grow">
                  <b>Module {m.k}</b> <span className="dim">{m.name}</span>
                </span>
                <span className="dim count">{lecs.length ? lecs.length : '—'}</span>
              </button>
              {isOpen && (
                <div className="tree-row files" title="the module's shared files (slides PDF)">
                  <Icon name="film" size={12} />
                  <span className="grow dim">Files: {FILES[m.k]?.length ? FILES[m.k].map((f) => f.name).join(', ') : 'nothing shared yet'}</span>
                </div>
              )}
              {isOpen &&
                lecs.map((l) => {
                  const lecOpen = openLecs.has(l.stem)
                  return (
                    <div key={l.stem}>
                      <button type="button" className={cls('tree-row lec', l.stem === stem && 'cur')} aria-expanded={lecOpen} onClick={() => flip(openLecs, l.stem, setOpenLecs)}>
                        <Icon name="chevron" size={12} className={lecOpen ? 'turn' : ''} />
                        <span className="grow">{lectureTitle(l)}</span>
                        {l.langs.some((x) => x.build) && <Icon name="film" size={12} />}
                      </button>
                      {lecOpen &&
                        langRows(l, stem === l.stem ? lec : null).map((x) => (
                          <button key={x.code} type="button" className={cls('tree-row langrow', l.stem === stem && x.code === lang && 'sel')} onClick={() => open(l.stem, x.code)}>
                            <span className="lang-name">{(LANGUAGES[x.code]?.name ?? x.code)}</span>
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
