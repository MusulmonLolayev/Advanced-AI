import { memo, useEffect, useMemo, useRef, useState } from 'react'
import { Chip, Panel, Tabs } from '../../components'
import type { LineState } from '../../model'
import type { LineRow, Project } from '../../types'
import { cls, secs, timecode } from '../../util'

type Filter = 'all' | 'take' | 'clone' | 'marks'

export function LineMarks({ s, k, p }: { s: LineState; k: number; p: Project }) {
  const vm = p.voice[String(k)]
  return (
    <>
      {s.kind === 'take' && s.take && (
        <Chip tone="you" title="your recording is used for this line">
          T{(p.takes[String(k)] ?? []).findIndex((t) => t.id === s.take!.id) + 1} · {secs(s.take.length)}
        </Chip>
      )}
      {s.kind === 'clone' && (
        <Chip tone="clone" title="no take: the lecture video's own narration (cloned or synthetic voice) is used">
          cloned voice
        </Chip>
      )}
      {s.kind === 'silent' && <Chip tone="empty">silent</Chip>}
      {s.kind === 'mistake' && <Chip tone="bad">mistake</Chip>}
      {s.lang === 'needs_update' && (
        <Chip tone="accent" title="another language changed this line">
          needs update
        </Chip>
      )}
      {s.voice === 'fail' && vm && (
        <Chip tone="bad" title={`the voice check heard: ${vm.heard}`}>
          voice check: {vm.fails.join(', ')}
        </Chip>
      )}
      {s.voice === 'listen' && (
        <Chip tone="warn" title="the voice check put this line on the listen list">
          listen
        </Chip>
      )}
    </>
  )
}

const Row = memo(function Row({ k, text, start, s, p, selected, onPick }: { k: number; text: string; start: number; s: LineState; p: Project; selected: boolean; onPick: (k: number) => void }) {
  return (
    <button type="button" id={`line-${k}`} className={cls('row line-row', selected && 'selected', `k-${s.kind}`)} aria-selected={selected} onClick={() => onPick(k)}>
      <span className="line-no mono">{k + 1}</span>
      <span className="line-main">
        <span className="line-text">{text}</span>
        <span className="line-meta">
          <span className="mono dim">{timecode(start, false)}</span>
          <LineMarks s={s} k={k} p={p} />
        </span>
      </span>
    </button>
  )
})

export function ScriptList({ p, states, line, onPick }: { p: Project; states: LineState[]; line: number; onPick: (k: number) => void }) {
  const [f, setF] = useState<Filter>('all')
  const ref = useRef<HTMLDivElement>(null)
  const counts = useMemo(() => {
    const c = { all: states.length, take: 0, clone: 0, marks: 0 }
    states.forEach((s) => {
      if (s.kind === 'take') c.take++
      if (s.kind === 'clone' || s.kind === 'silent') c.clone++
      if (s.voice || s.lang === 'needs_update' || s.kind === 'mistake') c.marks++
    })
    return c
  }, [states])
  const show = (s: LineState) => f === 'all' || (f === 'take' && s.kind === 'take') || (f === 'clone' && (s.kind === 'clone' || s.kind === 'silent')) || (f === 'marks' && !!(s.voice || s.lang === 'needs_update' || s.kind === 'mistake'))
  useEffect(() => {
    const el = document.getElementById(`line-${line}`)
    const box = ref.current
    if (!el || !box) return
    const r = el.getBoundingClientRect()
    const b = box.getBoundingClientRect()
    if (r.top < b.top + 8 || r.bottom > b.bottom - 8) box.scrollTop += r.top - b.top - b.height / 3
  }, [line, f])
  return (
    <Panel title="Script" className="script-panel" actions={<span className="mono dim">{p.lines.length} lines</span>} bodyClass="script-body">
      <div className="script-filter">
        <Tabs
          pills
          label="Filter lines"
          value={f}
          onChange={setF}
          tabs={[
            { id: 'all', label: `All ${counts.all}` },
            { id: 'take', label: `Takes ${counts.take}` },
            { id: 'clone', label: `Cloned ${counts.clone}` },
            { id: 'marks', label: `Marks ${counts.marks}` },
          ]}
        />
      </div>
      <div className="script-list" ref={ref}>
        {p.lines.map((l: LineRow, k) => (show(states[k]) ? <Row key={k} k={k} text={l[1]} start={states[k].a} s={states[k]} p={p} selected={k === line} onPick={onPick} /> : null))}
      </div>
    </Panel>
  )
}
