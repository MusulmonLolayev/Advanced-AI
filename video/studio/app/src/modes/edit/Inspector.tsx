import { Fragment, useRef, useState, type ReactNode } from 'react'
import { useActions } from '../../actions'
import { Button, Chip, Icon, InspectorSection, Panel, useToast } from '../../components'
import { ORIGINAL, type LineState } from '../../model'
import type { EditorLangs, Levels, Project, Session, Take, VersionRow } from '../../types'
import { secs, timecode } from '../../util'
import { LineMarks } from './ScriptList'
import { TakeWave } from './TakeWave'
import type { Transport } from './usePlayer'

type Act = ReturnType<typeof useActions>

const sessionLabel = (s: string) => {
  const m = /^\d+-(\d+)-(\d+)T(\d+)-(\d+)/.exec(s)
  return m ? `${m[2]}.${m[1]} ${m[3]}:${m[4]}` : s
}
const mmss = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(Math.round(s % 60) % 60).padStart(2, '0')}`

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

function tightenLabel(tg: Take['tighten']): string {
  if (tg.gain <= 0) return 'tightened: nothing more to gain'
  const parts: string[] = []
  if (tg.pauses) parts.push(`${tg.pauses} pause${tg.pauses === 1 ? '' : 's'}`)
  if (tg.start) parts.push(`start ${tg.start.toFixed(1)} s`)
  if (tg.end) parts.push(`end ${tg.end.toFixed(1)} s`)
  return 'tighten: ' + (parts.join(', ') || `${tg.gain.toFixed(1)} s`)
}

function TakeCard({ t, n, k, used, levels, act, tr }: { t: Take; n: number; k: number; used: boolean; levels: Levels | undefined; act: Act; tr: Transport }) {
  const e = t.edit
  const off = (a: number, b: number) => Math.abs(a - b) > 1e-3
  const ck = t.check
  return (
    <div className={'take' + (used ? ' used' : '') + (t.rejected ? ' bad' : '')} data-take={t.id}>
      <div className="take-head">
        <b className="take-name">T{n}</b>
        <span className="mono">{secs(t.length)}</span>
        <span className="mono dim" title={t.id}>{sessionLabel(t.session)}</span>
        <span className="grow" />
        {used && <Chip tone="you" title="your recording is used for this line in the preview and the export; the lecture video keeps its own narration">used in your edit</Chip>}
        {t.rejected && <Chip tone="bad">mistake</Chip>}
        {ck && (ck.missing.length ? <Chip tone="bad">{ck.missing.length} missed</Chip> : <Chip tone="good">script ✓</Chip>)}
      </div>
      <TakeWave levels={levels} from={t.t_in} to={t.t_out} pauses={t.pauses} trimIn={e.trim_in ?? 0} trimOut={e.trim_out ?? 0} fit={t.fit} color="--track-you" onTrim={(c) => void act.edit(t.id, c)} />
      <div className="take-trim mono dim">
        <span>in {(e.trim_in ?? 0).toFixed(2)}</span>
        <span>{secs(t.raw_length)} → {secs(t.length)}</span>
        <span>out {(e.trim_out ?? 0).toFixed(2)}</span>
      </div>
      <div className="btn-row">
        <Button small icon="play" onClick={() => tr.playTake(t, n)} title="play this take alone">watch</Button>
        <Button small onClick={() => void tr.playContext(t, n)} title="the end of the line before, this take, the start of the line after">in context</Button>
        {!used && <Button small variant="primary" onClick={() => void act.choose(k, t.id)} title="use this recording for the line in your edit (preview and export)">use this one</Button>}
        <Button small variant="ghost" onClick={() => void act.edit(t.id, { rejected: !t.rejected })}>{t.rejected ? 'not a mistake' : 'mistake'}</Button>
        <Button small variant="ghost" icon="trash" onClick={() => { if (window.confirm('Hide this take?')) void act.edit(t.id, { deleted: true }) }}>hide</Button>
      </div>
      <div className="btn-row fit">
        <span className="dim label">line ends · keep {t.margin} s</span>
        <Button small disabled={!off(t.fit[0], e.trim_in ?? 0)} onClick={() => void act.fit(t.id, 'start')} title={`trim the start so ${t.margin} s of silence stays before the first word (${t.fit[0].toFixed(2)} s)`}>fit start</Button>
        <Button small disabled={!off(t.fit[1], e.trim_out ?? 0)} onClick={() => void act.fit(t.id, 'end')} title={`trim the end so ${t.margin} s of silence stays after the last word (${t.fit[1].toFixed(2)} s)`}>fit end</Button>
        <Button small disabled={!off(t.fit[0], e.trim_in ?? 0) && !off(t.fit[1], e.trim_out ?? 0)} onClick={() => void act.fit(t.id, 'both')}>fit both</Button>
        <Button small variant="ghost" disabled={!e.trim_in && !e.trim_out} onClick={() => void act.edit(t.id, { trim_in: null, trim_out: null })} title="put both ends back to the recording's own">reset</Button>
      </div>
    </div>
  )
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

function SessionRow({ s, act }: { s: Session; act: Act }) {
  const state = s.stale ? <span className="dim">earlier build of the video: not used</span> : {
    recording: <span className="warn">recording… {s.chunks} s</span>,
    recorded: <span className="warn">waiting</span>,
    processing: <span className="warn">cleaning the voice…</span>,
    ready: <span className="dim">{(s.seconds / 60).toFixed(1)} min · {s.clean}</span>,
    failed: <span className="bad">failed {s.error}</span>,
  }[s.state]
  return (
    <li className="session">
      <span className="mono" title={s.name}>{sessionLabel(s.name)}</span>
      <span className="grow">{state}</span>
      <button type="button" className="icon-btn" title={`Delete recording ${s.name}`} aria-label={`Delete recording ${s.name}`}
        onClick={() => { if (window.confirm(`Delete recording ${s.name} (${mmss(s.seconds)})? This cannot be undone.`)) void act.deleteRecording(s.name) }}>
        <Icon name="trash" size={14} />
      </button>
    </li>
  )
}

export function Inspector({
  p, k, st, langs, levels, tr, onGotoLang, onRecord,
}: {
  p: Project
  k: number
  st: LineState
  langs: EditorLangs | null
  levels: Record<string, Levels>
  tr: Transport
  onGotoLang: (lang: string, key: string) => void
  onRecord: () => void
}) {
  const act = useActions()
  const toast = useToast()
  const takes = p.takes[String(k)] ?? []
  const text = p.lines[k][1]
  const scene = p.scenes[k]
  const versions = p.versions[scene] ?? []
  const vm = p.voice[String(k)]
  const li = langs?.lines[String(k)]
  const orig = levels[ORIGINAL]
  const vStart = p.lines[k][0]
  const vEnd = p.lines[k + 1]?.[0] ?? vStart + (st.b - st.a)
  const chosen = st.take
  const wordsTake = chosen ?? takes[takes.length - 1]
  const words = wordsTake?.words
  const clone = p.engine === 'navoiy' ? 'cloned' : 'synthetic'
  const making = versions.some((x) => ['queued', 'voicing', 'rendering'].includes(x.state))
  const wordsBusy = p.jobs.some((j) => j.kind === 'words' && (j.state === 'queued' || j.state === 'running'))

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

  const e = chosen?.edit
  const tools = !!e && ((e.auto_cuts ?? []).length || (e.squeeze ?? []).length || (e.auto ?? []).length)
  const cuts = e?.cuts ?? []
  const wordsGrid = wordsTake?.words ? wordsOf(wordsTake) : null
  return (
    <Panel
      title={
        <>
          Inspector · line <b className="mono">{k + 1}</b>
        </>
      }
      actions={<span className="mono dim">{timecode(st.a)}–{timecode(st.b)}</span>}
      className="inspector"
    >
      <div className="insp-head">
        <p className="insp-text">{text}</p>
        <div className="chips">
          <LineMarks s={st} k={k} p={p} />
          <Chip tone="empty" plain className="mono" title="the scene this line belongs to">{scene}</Chip>
        </div>
        <div className="btn-row">
          <Button variant="record" small icon="rec" onClick={onRecord} title="open the booth on this line (L)">record this line</Button>
          <Button small icon="play" onClick={() => tr.playLine(k)}>play</Button>
        </div>
      </div>

      <InspectorSection title="Takes" count={takes.length ? `${takes.length}` : 'none'}>
        {takes.length === 0 && (
          <div className="empty-note">
            <p>
              <b>No take of this line.</b> {p.settings.missing === 'original' ? 'The lecture video’s own narration (the cloned voice) plays here.' : 'This line is silent in the export.'}
            </p>
            <div className="dim label">the lecture video's own voice for this line</div>
            <TakeWave levels={orig} from={vStart} to={vEnd} color="--track-clone" handles={false} height={52} />
          </div>
        )}
        {takes.map((t, i) => (
          <TakeCard key={t.id} t={t} n={i + 1} k={k} used={t.id === chosen?.id} levels={levels[t.session]} act={act} tr={tr} />
        ))}
      </InspectorSection>

      {chosen && e && (
        <InspectorSection title="Tighten & nudge" open={false}>
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
        </InspectorSection>
      )}

      {wordsTake && (
        <InspectorSection title="Script check" count={words ? `${words.heard.length} words heard` : 'not transcribed'} open={false}>
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
        </InspectorSection>
      )}

      <InspectorSection title={`${clone === 'cloned' ? 'Cloned' : 'Synthetic'}-voice versions`} count={versions.length ? `${versions.length} for ${scene}` : undefined}>
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
                    onClick={() => { if (window.confirm(`Merge v${x.n} into the lecture? The narration file gets its texts, the scene and the lecture video are replaced (about a minute), and your recordings move to the new timings. The previous video is kept as before_merge.`)) void act.merge(scene, x.n) }}>
                    merge
                  </Button>
                )}
                {!(x.state === 'merged' || x.state === 'voicing' || x.state === 'rendering' || merging) && (
                  <Button small variant="ghost" title="delete this version" onClick={() => { if (window.confirm(`Discard v${x.n} of ${scene}? Its files are deleted.`)) void act.discard(scene, x.n) }}>discard</Button>
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
      </InspectorSection>

      <InspectorSection title="Other languages" count={li?.others.length ? li.others.map((o) => o.lang).join(' ') : undefined}>
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
      </InspectorSection>

      <InspectorSection title="Recordings" count={p.sessions.length || 'none'} open={false}>
        <ul className="plain sessions">
          {p.sessions.map((s) => <SessionRow key={s.name} s={s} act={act} />)}
          {!p.sessions.length && <li className="dim">none yet: press Record</li>}
        </ul>
      </InspectorSection>
    </Panel>
  )
}
