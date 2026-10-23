import { useEffect, useRef, useState } from 'react'
import type { useActions } from '../../actions'
import * as api from '../../api'
import { Button } from '../../components'
import { addCut, cutsLabel, rawTime, removeCut } from '../../cuts'
import { editedTime, planOf } from '../../model'
import { useTakeHead } from '../../playhead'
import { useStudio } from '../../studio'
import type { Levels, Take } from '../../types'
import { secs } from '../../util'
import { TakeWave } from './TakeWave'
import type { Transport } from './usePlayer'

type Act = ReturnType<typeof useActions>

/** The props a take's wave gets, shared by the inspector's small wave and the wide editor so the cut logic lives in one place:
 *  select, cut, restore, clear, play a selection or from a click, trim. (Cuts are in the take's own seconds; see cuts.ts.) */
export function takeWaveProps(t: Take, n: number, act: Pick<Act, 'edit'>, tr: Transport) {
  const e = t.edit
  const at = (tt: number) => editedTime(planOf(e, t.raw_picture, t.raw_length), t.raw_length, tt) + Math.max(-(e.nudge ?? 0), 0)
  return {
    from: t.t_in,
    to: t.t_out,
    pauses: t.pauses,
    trimIn: e.trim_in ?? 0,
    trimOut: e.trim_out ?? 0,
    fit: t.fit,
    color: '--track-you',
    cuts: e.cuts ?? [],
    autoCuts: e.auto_cuts ?? [],
    onCut: (span: [number, number]) => void act.edit(t.id, { cuts: addCut(e.cuts ?? [], span) }),
    onRestore: (i: number) => void act.edit(t.id, { cuts: removeCut(e.cuts ?? [], i) }),
    onClearCuts: () => void act.edit(t.id, { cuts: [] }),
    onPlaySelection: (sp: [number, number]) => tr.playTake(t, n, at(sp[0]), at(sp[1])),
    onTrim: (c: { trim_in?: number | null; trim_out?: number | null }) => void act.edit(t.id, c),
    onPlayFrom: (tt: number) => tr.playTake(t, n, at(tt)),
  }
}

const ZOOMS = [1, 1.5, 2, 3, 4, 6]

/** A large editor for one take, in a native <dialog> like the app's other dialogs: the same wave at the dialog's width (zoom with
 *  horizontal scroll), the same select / cut / restore and trim handles, a moving playhead, the cuts list. */
export function TakeEditor({ t, n, levels, tr, onClose }: { t: Take; n: number; levels: Levels | undefined; tr: Transport; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null)
  const [zoom, setZoom] = useState(0)
  // every edit saves as it is made: this shows it (saving… while the POST is out, ✓ saved for 2 s, or why it failed)
  const { build, reload } = useStudio()
  const [save, setSave] = useState<{ s: 'idle' | 'saving' | 'saved' | 'error'; msg?: string }>({ s: 'idle' })
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  useEffect(() => () => { if (timer.current) clearTimeout(timer.current) }, [])
  const run = async <T,>(f: () => Promise<T>): Promise<T | null> => {
    if (timer.current) clearTimeout(timer.current)
    setSave({ s: 'saving' })
    try {
      const r = await f()
      await reload()
      setSave({ s: 'saved' })
      timer.current = setTimeout(() => setSave({ s: 'idle' }), 2000)
      return r
    } catch (e) {
      setSave({ s: 'error', msg: (e as Error).message })
      return null
    }
  }
  const act = { edit: (take: string, changes: api.EditChanges) => run(() => api.postEdit(build, take, changes)) }
  const off = (x: number, y: number) => Math.abs(x - y) > 1e-3
  useEffect(() => {
    const d = ref.current
    if (d && !d.open) d.showModal()
  }, [])
  const e = t.edit
  const cuts = e.cuts ?? []
  const T = useTakeHead()
  const mine = tr.what.kind === 'take' && tr.what.label === `take T${n}`
  const plan = planOf(e, t.raw_picture, t.raw_length)
  const head = mine ? rawTime(plan, t.raw_length, Math.max(T - Math.max(-(e.nudge ?? 0), 0), 0)) : null
  const z = ZOOMS[zoom]
  return (
    <dialog
      ref={ref}
      className="dialog take-editor"
      aria-label={`edit parts of take T${n}`}
      data-loaded-voice={tr.loadedVoice()}
      onCancel={(ev) => {
        ev.preventDefault()
        onClose()
      }}
      onClick={(ev) => {
        if (ev.target === ref.current) onClose()
      }}
      // the app listens for single keys on the document: keep them out while this is open
      onKeyDown={(ev) => ev.nativeEvent.stopPropagation()}
    >
      <div className="te-head">
        <h2 className="dialog-title">Edit parts · T{n}</h2>
        <span className="mono dim">{secs(t.raw_length, 2)} → {secs(t.length, 2)}</span>
        <span className="grow" />
        <Button small disabled={!off(t.fit[0], e.trim_in ?? 0) && !off(t.fit[1], e.trim_out ?? 0)} onClick={() => void run(() => api.postFit(build, t.id, 'both'))} title={`set the start and end to your first and last word, keeping ${t.margin} s`}>trim silence</Button>
        <Button small variant="ghost" disabled={!e.trim_in && !e.trim_out} onClick={() => void act.edit(t.id, { trim_in: null, trim_out: null })} title="put both ends back to the recording's own">undo trims</Button>
        <Button small icon="play" onClick={() => (mine && tr.playing ? tr.toggle() : tr.playTake(t, n, mine && T < t.length - 0.1 ? T : 0))} title="play the take as it is now (cuts and trims applied) from where it stopped, or pause">{mine && tr.playing ? 'pause' : 'play'}</Button>
        <Button small aria-label="zoom out" disabled={zoom === 0} onClick={() => setZoom(zoom - 1)}>−</Button>
        <span className="mono dim te-zoom">{z}×</span>
        <Button small aria-label="zoom in" disabled={zoom === ZOOMS.length - 1} onClick={() => setZoom(zoom + 1)}>+</Button>
      </div>
      <p className="dim sub">Every cut and trim is saved as you make it.</p>
      <p className="dim sub">Drag the blue handles to trim the start and end. Drag on the wave to select a part, then ✂ or Delete to cut it. Click a cut to restore it. Click anywhere else to play from there.</p>
      <div className="te-body">
        <div className="te-scroll">
          <div style={{ width: `${z * 100}%` }}>
            <TakeWave levels={levels} {...takeWaveProps(t, n, act, tr)} height={160} playhead={head} bigHandles />
          </div>
        </div>
      </div>
      <div className="te-cuts">
        <span className="label">cuts</span>
        {cuts.map(([a, b], i) => (
          <button key={i} type="button" className="chip chip-btn" title="click to restore this part" onClick={() => void act.edit(t.id, { cuts: removeCut(cuts, i) })}>
            {a.toFixed(2)}–{b.toFixed(2)} s ✕
          </button>
        ))}
        {!cuts.length && <span className="dim">none</span>}
        {cuts.length > 0 && <span className="mono dim">{cutsLabel(cuts)}</span>}
        {cuts.length > 0 && <Button small variant="ghost" onClick={() => void act.edit(t.id, { cuts: [] })}>clear cuts</Button>}
      </div>
      <div className="dialog-actions">
        <span className={'te-save mono ' + (save.s === 'error' ? 'bad' : 'dim')} role="status" data-save={save.s}>
          {save.s === 'saving' ? 'saving…' : save.s === 'saved' ? '✓ saved' : save.s === 'error' ? `not saved: ${save.msg}` : ''}
        </span>
        <Button variant="primary" onClick={onClose}>Close</Button>
      </div>
    </dialog>
  )
}
