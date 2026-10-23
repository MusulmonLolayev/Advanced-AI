// The panels the old inspector showed, moved here unchanged: each is the body of a dialog opened from a clip's context menu
// (Edit.tsx) or the timeline bar. They read and change the project through the same actions as before.
import { Fragment, useRef, useState, type ReactNode } from 'react'
import { useActions } from '../../actions'
import { Button, Chip, Icon, useDialog, useToast } from '../../components'
import type { EditorLangs, Project, Session, Take, VersionRow } from '../../types'
import type { Transport } from './usePlayer'

export type Act = ReturnType<typeof useActions>

export const sessionLabel = (s: string) => {
  const m = /^\d+-(\d+)-(\d+)T(\d+)-(\d+)/.exec(s)
  return m ? `${m[2]}.${m[1]} ${m[3]}:${m[4]}` : s
}
export const mmss = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(Math.round(s % 60) % 60).padStart(2, '0')}`

/** `now` with the words not in `old` marked, and the words it lost struck out (versions.js wordDiff) */
function wordDiff(old: string, now: string): ReactNode {
  const a = old.split(/\s+/).filter(Boolean)
  const b = now.split(/\s+/).filter(Boolean)
  const L = Array.from({ length: a.length + 1 }, () => new Array<number>(b.length + 1).fill(0))
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--) L[i][j] = a[i] === b[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1])
  let i = 0
  let j = 0
  const out: ReactNode[] = []
  while (i < a.length || j < b.length) {
    if (i < a.length && j < b.length && a[i] === b[j]) {
      out.push(<Fragment key={out.length}>{b[j]} </Fragment>)
      i++
      j++
    } else if (j < b.length && (i >= a.length || L[i][j + 1] >= L[i + 1][j])) {
      out.push(<Fragment key={out.length}><mark>{b[j]}</mark> </Fragment>)
      j++
    } else {
      out.push(<Fragment key={out.length}><del>{a[i]}</del> </Fragment>)
      i++
    }
  }
  return out
}

export function tightenLabel(tg: Take['tighten']): string {
  if (tg.gain <= 0) return 'tightened: nothing more to gain'
  const parts: string[] = []
  if (tg.pauses) parts.push(`${tg.pauses} pause${tg.pauses === 1 ? '' : 's'}`)
  if (tg.start) parts.push(`start ${tg.start.toFixed(1)} s`)
  if (tg.end) parts.push(`end ${tg.end.toFixed(1)} s`)
  return 'tighten: ' + (parts.join(', ') || `${tg.gain.toFixed(1)} s`)
}

/** picture later / sooner than the voice: the slider and the number agree; saved when the slider is let go or the number is left */
function Nudge({ value, onSave }: { value: number; onSave: (v: number) => void }) {
  const [v, setV] = useState<number | null>(null)
  const shown = v ?? value
  const save = () => {
    if (v !== null && Math.abs(v - value) > 1e-9) onSave(v)
    setV(null)
  }
  return (
    <div className="field">
      <label>picture later / sooner than the voice</label>
      <input type="range" min={-2} max={2} step={0.05} value={shown} aria-label="nudge" className="grow" onChange={(e) => setV(+e.target.value)} onPointerUp={save} onKeyUp={save} />
      <input type="number" step={0.05} value={shown} aria-label="nudge in seconds" className="nudge-num" onChange={(e) => setV(+e.target.value || 0)} onBlur={save} onKeyDown={(e) => e.key === 'Enter' && save()} />
      <span className="dim">s</span>
    </div>
  )
}

/** hear a whole recording in your voice (cleaned) or in the cloned voice, one at a time */
function Compare({ yours, cloned }: { yours: string; cloned: string }) {
  const [on, setOn] = useState<'yours' | 'cloned' | null>(null)
  const el = useRef<HTMLAudioElement | null>(null)
  const play = (which: 'yours' | 'cloned') => {
    el.current?.pause()
    if (on === which) return setOn(null)
    const a = new Audio(which === 'yours' ? yours : cloned)
    a.onended = () => setOn(null)
    el.current = a
    setOn(which)
    void a.play().catch(() => setOn(null))
  }
  return (
    <span className="compare">
      <Button small variant={on === 'yours' ? 'primary' : 'ghost'} onClick={() => play('yours')} title="this recording, your voice cleaned, before conversion">{on === 'yours' ? 'stop' : 'your voice'}</Button>
      <Button small variant={on === 'cloned' ? 'primary' : 'ghost'} onClick={() => play('cloned')} title="this recording, re-spoken in the cloned voice">{on === 'cloned' ? 'stop' : 'cloned voice'}</Button>
    </span>
  )
}

function SessionRow({ s, act, p }: { s: Session; act: Act; p: Project }) {
  const { confirm } = useDialog()
  const converting = p.jobs.some((j) => j.kind === 'process' && j.key === s.name && (j.state === 'queued' || j.state === 'running'))
  const yours = p.audio_alt?.[s.name]
  const state = s.stale ? <span className="dim">earlier build of the video: not used</span> : {
    recording: <span className="warn">recording… {s.chunks} s</span>,
    recorded: <span className="warn">waiting</span>,
    processing: <span className="warn">{s.clean === 'cloned' ? 'converting to the cloned voice…' : 'cleaning the voice…'}</span>,
    ready: <span className="dim">{(s.seconds / 60).toFixed(1)} min · {s.clean}</span>,
    failed: <span className="bad">failed {s.error}</span>,
  }[s.state]
  return (
    <li className="session">
      <span className="mono" title={s.name}>{sessionLabel(s.name)}</span>
      <span className="grow">{converting && s.state !== 'processing' ? <span className="warn">converting…</span> : state}</span>
      {s.state === 'ready' && !s.stale && yours && p.audio[s.name] && <Compare yours={yours} cloned={p.audio[s.name]} />}
      {s.state === 'ready' && !s.stale && s.clean !== 'cloned' && (
        <Button small disabled={converting} onClick={() => void act.convertRecording(s.name)} title="re-speak this recording in the cloned voice: your timing and pronunciation, the cloned voice's clean sound (needs the voice server)">convert to cloned voice</Button>
      )}
      <button type="button" className="icon-btn" title={`Delete recording ${s.name}`} aria-label={`Delete recording ${s.name}`}
        onClick={async () => { if (await confirm({ title: `Delete recording ${s.name}?`, body: `The recording (${mmss(s.seconds)}) is deleted. This cannot be undone.`, confirmLabel: 'Delete recording', tone: 'danger' })) void act.deleteRecording(s.name) }}>
        <Icon name="trash" size={14} />
      </button>
    </li>
  )
}


/** Tighten & nudge: the picture against the voice, the hand cuts, what the tightening tool did, tighten / undo */
export function TightenPanel({ chosen, act }: { chosen: Take; act: Act }) {
  const e = chosen.edit
  const tools = !!e && ((e.auto_cuts ?? []).length || (e.squeeze ?? []).length || (e.auto ?? []).length)
  const cuts = e?.cuts ?? []
  return (
    <div className="insp-body">
          <Nudge key={chosen.id} value={e.nudge ?? 0} onSave={(v) => void act.edit(chosen.id, { nudge: v })} />
          <div className="field">
            <label>cuts</label>
            <span className="chips">
              {cuts.map(([a, b], n) => (
                <button key={n} type="button" className="chip chip-btn" title="click to remove" onClick={() => void act.edit(chosen.id, { cuts: cuts.filter((_, i) => i !== n) })}>
                  {a.toFixed(2)}–{b.toFixed(2)} s ✕
                </button>
              ))}
              {!cuts.length && <span className="dim">none</span>}
            </span>
          </div>
          {((e.auto_cuts ?? []).length > 0 || (e.squeeze ?? []).length > 0) && (
            <p className="dim sub">
              tightened: {(e.auto_cuts ?? []).reduce((a, [x, y]) => a + y - x, 0).toFixed(1)} s of pauses cut
              {(e.squeeze ?? []).length > 0 && `, ${(e.squeeze ?? []).reduce((a, [x, y, n]) => a + y - x - n, 0).toFixed(1)} s squeezed`}
            </p>
          )}
          <div className="btn-row">
            <Button small onClick={() => void act.shrink(chosen.id)} disabled={chosen.tighten.gain <= 0} title={`shorten the pauses inside the take, and trim the ends to keep ${chosen.margin} s around the voice (a trim you set by hand stays)`}>{tightenLabel(chosen.tighten)}</Button>
            {tools && <Button small variant="ghost" onClick={() => void act.unshrink(chosen.id)} title="takes back the pause cuts and the trims the tool set; your own cuts, hand-set trims and nudge stay">undo tightening</Button>}
            {cuts.length > 0 && <Button small variant="ghost" onClick={() => void act.edit(chosen.id, { cuts: [] })}>clear cuts</Button>}
          </div>
    </div>
  )
}

/** Script check: the words heard against the approved text; a click on a word cuts or keeps it; transcribe */
export function ScriptCheckPanel({ p, wordsTake, act }: { p: Project; wordsTake: Take; act: Act }) {
  const words = wordsTake.words
  const wordsBusy = p.jobs.some((j) => j.kind === 'words' && (j.state === 'queued' || j.state === 'running'))
  const wordsOf = (t: Take) => {
    const e = t.edit
    const cuts = e.cuts ?? []
    const all = cuts.concat(e.auto_cuts ?? [])
    const inCut = (a: number, b: number) => all.some(([x, y]) => a >= x - 1e-3 && b <= y + 1e-3)
    const extra = new Set((t.check?.extra ?? []).map((x) => x[1].toFixed(3)))
    const changed = t.check?.changed ?? []
    const isChanged = (a: number) => changed.some((c) => a >= c[2] - 1e-3 && a <= c[3] + 1e-3)
    const pauses = t.pauses.filter((q) => q[1] - q[0] >= 0.8)
    let pi = 0
    const cutWord = (a: number, b: number) => {
      const next = cuts.map((x) => [...x] as [number, number])
      const hit = next.findIndex(([x, y]) => a >= x - 1e-3 && b <= y + 1e-3)
      if (hit >= 0) next.splice(hit, 1)
      else next.push([Math.max(0, a - 0.03), b + 0.03])
      void act.edit(t.id, { cuts: next })
    }
    return (t.words?.heard ?? []).map(([w, a, b], i) => {
      const pre: ReactNode[] = []
      while (pi < pauses.length && pauses[pi][0] <= a) {
        pre.push(<span key={'p' + pi} className="pause">⏸{(pauses[pi][1] - pauses[pi][0]).toFixed(1)}s </span>)
        pi++
      }
      return (
        <Fragment key={i}>
          {pre}
          <span className={'w' + (extra.has(a.toFixed(3)) ? ' extra' : isChanged(a) ? ' changed' : '') + (inCut(a, b) ? ' cut' : '')} role="button" tabIndex={0} title={`${a.toFixed(2)}–${b.toFixed(2)} s · click to cut or keep`} onClick={() => cutWord(a, b)} onKeyDown={(ev) => ev.key === 'Enter' && cutWord(a, b)}>
            {w}
          </span>{' '}
        </Fragment>
      )
    })
  }

  const wordsGrid = wordsTake.words ? wordsOf(wordsTake) : null
  return (
    <div className="insp-body">
          {words ? (
            <p className="words">{wordsGrid}</p>
          ) : (
            <p className="dim">This take has not been transcribed and compared with the approved text yet.</p>
          )}
          {wordsTake.check && wordsTake.check.missing.length > 0 && <p className="bad sub">Not heard: {wordsTake.check.missing.join(' · ')}</p>}
          {wordsTake.check && wordsTake.check.changed.length > 0 && (
            <p className="warn sub">Heard differently (the recogniser may be wrong; listen): {wordsTake.check.changed.map((c) => `${c[0]} → ${c[1]}`).join(' · ')}</p>
          )}
          {wordsTake.check && wordsTake.check.weak.length > 0 && <p className="warn sub">Unclear: {wordsTake.check.weak.join(' · ')}</p>}
          <div className="btn-row">
            {words && (
              <Button small disabled={!wordsTake.check?.extra.length} onClick={() => void act.cutExtras(wordsTake.id)}>
                cut the {wordsTake.check?.extra.length ?? 0} extra word{wordsTake.check?.extra.length === 1 ? '' : 's'}
              </Button>
            )}
            <Button small disabled={wordsBusy} onClick={() => void act.words(wordsTake.id)}>{words ? 'transcribe again' : 'transcribe and check'}</Button>
          </div>
    </div>
  )
}

/** The cloned-voice versions of this line's scene: the text box, save as new version, the version list, the voice check */
export function VersionsPanel({ p, k, tr, act }: { p: Project; k: number; tr: Transport; act: Act }) {
  const toast = useToast()
  const { confirm } = useDialog()
  const text = p.lines[k][1]
  const scene = p.scenes[k]
  const versions = p.versions[scene] ?? []
  const vm = p.voice[String(k)]
  const clone = p.engine === 'navoiy' ? 'cloned' : 'synthetic'
  const making = versions.some((x) => ['queued', 'voicing', 'rendering'].includes(x.state))
  // the narration box: what is typed stays per line; `bases` is the version the next one grows from ("Scene/vN")
  const [drafts, setDrafts] = useState<Record<number, string>>({})
  const [bases, setBases] = useState<Record<number, string>>({})
  const box = useRef<HTMLTextAreaElement>(null)
  const base = bases[k]
  const baseText = (base && versions.find((x) => 'v' + x.n === base.split('/')[1])?.texts[String(k)]) || text
  const typed = drafts[k] ?? text
  const dropBase = () => setBases((b) => Object.fromEntries(Object.entries(b).filter(([i]) => +i !== k)))
  const saveVersion = async (asIs: boolean) => {
    if (!asIs && typed.trim() === baseText.trim()) return toast('The text is unchanged' + (p.engine === 'navoiy' ? ': use “new cloned-voice take”' : ''))
    if (await act.version(k, asIs ? undefined : typed.trim(), base)) dropBase()
  }
  const rewriteAgain = (x: VersionRow) => {
    setBases((b) => ({ ...b, [k]: `${scene}/v${x.n}` }))
    setDrafts((d) => ({ ...d, [k]: x.texts[String(k)] ?? text }))
    box.current?.focus()
  }

  return (
    <div className="insp-body">
        <p className="dim sub">The lecture video’s own narration. Rewriting a line voices it again and renders only its scene; a merge replaces the scene in the video. Your recordings are not affected.</p>
        {vm && (
          <div className="vcheck">
            <div className="chips">
              <span className="label">voice check</span>
              {!vm.ok ? <Chip tone="bad">fails: {vm.fails.join(', ')}</Chip> : vm.listen ? <Chip tone="warn">passes, listen</Chip> : <Chip tone="good">passes</Chip>}
            </div>
            <p className="heard dim"><span className="label">heard:</span> {vm.heard}</p>
          </div>
        )}
        {versions.slice().reverse().map((x) => {
          const merging = p.jobs.some((j) => j.kind === 'merge' && j.key === `${scene}/v${x.n}` && (j.state === 'queued' || j.state === 'running'))
          const rep = Object.values(x.report ?? {})
          const ready = x.state === 'ready' && !merging
          const when = new Date(x.created * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
          return (
            <div key={x.n} className={'version' + (x.state === 'stale' || x.state === 'merged' ? ' old' : '')}>
              <div className="chips">
                <b>v{x.n}</b>
                <Chip tone={x.state === 'merged' ? 'good' : x.state === 'failed' ? 'bad' : merging || x.state !== 'ready' ? 'warn' : 'good'}>
                  {merging ? 'merging…' : x.state === 'merged' ? 'merged into the lecture video' : x.state === 'stale' ? 'made before the last merge' : x.state}
                </Chip>
                {rep.length > 0 && (rep.some((r) => !r.ok) ? <Chip tone="bad">voice check fails</Chip> : rep.some((r) => r.listen) ? <Chip tone="warn">passes, listen</Chip> : <Chip tone="good">voice check passes</Chip>)}
                <span className="dim mono">{when}</span>
                {x.base ? <span className="dim">(grew from v{x.base})</span> : null}
              </div>
              <div className="btn-row">
                {x.video && <Button small icon="play" onClick={() => tr.watchVersion(x, scene, k)} title={`the whole scene, from this line, in the ${clone} voice (not your recording)`}>watch</Button>}
                {ready && <Button small variant="ghost" onClick={() => rewriteAgain(x)} title="load this version's text of the line into the box; the next version grows from it">rewrite again</Button>}
                {ready && (
                  <Button small variant="primary" icon="merge" title="put it in the lecture"
                    onClick={async () => { if (await confirm({ title: `Merge v${x.n} into the lecture?`, body: 'The narration file gets its texts, the scene and the lecture video are replaced (about a minute), and your recordings move to the new timings. The previous video is kept as before_merge.', confirmLabel: 'Merge', tone: 'primary' })) void act.merge(scene, x.n) }}>
                    merge
                  </Button>
                )}
                {!(x.state === 'merged' || x.state === 'voicing' || x.state === 'rendering' || merging) && (
                  <Button small variant="ghost" title="delete this version" onClick={async () => { if (await confirm({ title: `Discard v${x.n} of ${scene}?`, body: 'Its files are deleted.', confirmLabel: 'Discard version', tone: 'danger' })) void act.discard(scene, x.n) }}>discard</Button>
                )}
              </div>
              {x.error && <p className="bad sub">{x.error}</p>}
              {x.changed.map((c) => (
                <div key={c} className="vdiff"><span className="dim">line {+c + 1}</span> {x.state === 'merged' ? x.texts[String(c)] : wordDiff(p.lines[+c][1], x.texts[String(c)] ?? '')}</div>
              ))}
            </div>
          )
        })}
        {p.editable && (
          <>
            <textarea ref={box} rows={3} value={typed} onChange={(ev) => setDrafts((d) => ({ ...d, [k]: ev.target.value }))} aria-label="narration of this line" />
            <div className="btn-row">
              <Button small variant="primary" disabled={making} onClick={() => void saveVersion(false)} title={making ? 'a version of this scene is still being made' : 'the lecture is not changed until you merge'}>save as new version</Button>
              {p.engine === 'navoiy' && (
                <Button small disabled={making} onClick={() => void saveVersion(true)} title="the cloned voice says the same words again; the old clip stays if it scores better">new cloned-voice take</Button>
              )}
              {base && (
                <span className="warn sub">
                  grows from {base.split('/')[1]} <button type="button" className="link" onClick={dropBase}>(from the lecture instead)</button>
                </span>
              )}
            </div>
          </>
        )}
    </div>
  )
}

/** The line in the other languages, with "review" and "still fine" */
export function LanguagesPanel({ k, langs, onGotoLang, act }: { k: number; langs: EditorLangs | null; onGotoLang: (lang: string, key: string) => void; act: Act }) {
  const li = langs?.lines[String(k)]
  return (
    <div className="insp-body">
        {!li?.others.length && <p className="dim">This lecture has no other language yet.</p>}
        {li?.others.map((o) => (
          <div key={o.lang} className="lrow">
            <div className="chips">
              <b>{o.lang}</b>
              <Chip tone={o.state === 'approved' ? 'good' : o.state === 'needs_update' ? 'accent' : o.state === 'draft' ? 'warn' : 'empty'}>{o.state.replace('_', ' ')}</Chip>
              <span className="grow" />
              <Button small variant="ghost" onClick={() => onGotoLang(o.lang, li.key)}>review →</Button>
            </div>
            <p>{o.text}</p>
          </div>
        ))}
        {li?.state === 'needs_update' && (
          <div className="update-banner">
            <span>
              <b>needs update</b>{' '}
              {Object.entries(li.changed).map(([l, x]) => (
                <span key={l} className="vdiff"><span className="dim">{l} changed:</span> {wordDiff(x.old, x.new)} </span>
              ))}
            </span>
            <Button small onClick={() => void act.lineFine(li.key)} title="this line is still right: approve it again against the other languages as they are now">still fine</Button>
          </div>
        )}
    </div>
  )
}

/** The recordings of the lecture: state, compare your voice with the cloned one, convert, delete */
export function RecordingsPanel({ p, act }: { p: Project; act: Act }) {
  return (
    <div className="insp-body">
        <ul className="plain sessions">
          {p.sessions.map((s) => <SessionRow key={s.name} s={s} act={act} p={p} />)}
          {!p.sessions.length && <li className="dim">none yet: press Record</li>}
        </ul>
    </div>
  )
}
