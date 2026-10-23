// What a right-click on a clip offers. Each item calls an action that already existed (actions.ts, the transport) or opens
// one of the dialogs (Edit.tsx): this file only decides which items a clip gets.
import type { useActions } from '../../actions'
import type { MenuItem } from '../../components'
import type { ConfirmOptions } from '../../components/Dialog'
import type { LineState } from '../../model'
import type { Project } from '../../types'
import { secs } from '../../util'
import { mmss, sessionLabel } from './panels'
import type { Transport } from './usePlayer'

export type DialogKind = 'parts' | 'tighten' | 'check' | 'versions' | 'langs' | 'recordings'
export type Dlg = { kind: DialogKind; k: number }
/** a YOU clip (a take), a PICTURE or CLONE clip (a line), the empty YOU lane where a line has no take */
export type ClipKind = 'take' | 'line' | 'empty'

let playing: HTMLAudioElement | null = null
/** the voice clips of "Your voice / cloned voice": one at a time, the same item again stops it */
function playUrl(url: string) {
  const same = playing?.src.endsWith(url)
  playing?.pause()
  playing = null
  if (same) return
  const a = new Audio(url)
  playing = a
  a.onended = () => {
    if (playing === a) playing = null
  }
  void a.play().catch(() => {})
}

export type MenuEnv = {
  p: Project
  k: number
  st: LineState
  tr: Transport
  act: ReturnType<typeof useActions>
  confirm: (o: ConfirmOptions) => Promise<boolean>
  toast: (m: string) => void
  open: (d: Dlg) => void
  record: () => void
}

export function menuItems(kind: ClipKind, e: MenuEnv): MenuItem[] {
  const { p, k, st, tr, act, confirm, toast, open, record } = e
  const takes = p.takes[String(k)] ?? []
  const t = st.take
  if (kind === 'empty') return [{ label: 'Record this line', onSelect: record, hint: 'L' }]
  if (kind === 'line') {
    const lastTake = takes[takes.length - 1]
    return [
      { label: 'Play line', onSelect: () => tr.playLine(k) },
      { label: 'Record this line', onSelect: record, hint: 'L' },
      { label: 'Rewrite line in the cloned voice…', onSelect: () => open({ kind: 'versions', k }), sep: true },
      { label: 'Script check…', disabled: !(t ?? lastTake), onSelect: () => open({ kind: 'check', k }) },
      { label: 'Other languages…', onSelect: () => open({ kind: 'langs', k }) },
      { label: 'Copy text', sep: true, onSelect: () => navigator.clipboard.writeText(p.lines[k][1]).then(() => toast('Copied the text of the line'), () => toast('The browser would not copy it')) },
    ]
  }
  if (!t) return []
  const n = takes.findIndex((x) => x.id === t.id) + 1
  const ed = t.edit
  const sess = p.sessions.find((s) => s.name === t.session)
  const yours = p.audio_alt?.[t.session]
  const cloned = p.audio[t.session]
  const canCompare = !!sess && sess.clean === 'cloned' && !!yours && !!cloned
  const off = (a: number, b: number) => Math.abs(a - b) > 1e-3
  const items: MenuItem[] = [
    { label: 'Play take', onSelect: () => tr.playTake(t, n) },
    { label: 'Play in context', onSelect: () => void tr.playContext(t, n) },
    { label: 'Edit parts…', onSelect: () => open({ kind: 'parts', k }), sep: true },
    {
      label: 'Trim silence',
      disabled: !off(t.fit[0], ed.trim_in ?? 0) && !off(t.fit[1], ed.trim_out ?? 0),
      hint: `keeps ${t.margin} s`,
      onSelect: () => void act.fit(t.id, 'both'),
    },
    { label: 'Undo trims', disabled: !ed.trim_in && !ed.trim_out, onSelect: () => void act.edit(t.id, { trim_in: null, trim_out: null }) },
    {
      label: 'Takes',
      sep: true,
      items: takes.map((x, i) => ({
        label: `T${i + 1} · ${secs(x.length)}${x.rejected ? ' · mistake' : ''}`,
        hint: sessionLabel(x.session),
        checked: x.id === t.id,
        onSelect: () => (x.id === t.id ? undefined : void act.choose(k, x.id)),
      })),
    },
    { label: t.rejected ? 'Not a mistake' : 'Mark as mistake', onSelect: () => void act.edit(t.id, { rejected: !t.rejected }) },
    {
      label: 'Hide take',
      danger: true,
      onSelect: async () => {
        if (await confirm({ title: 'Hide this take?', body: 'The take is hidden from the lecture.', confirmLabel: 'Hide take', tone: 'danger' })) void act.edit(t.id, { deleted: true })
      },
    },
    { label: 'Transcribe and check…', sep: true, onSelect: () => open({ kind: 'check', k }) },
    { label: 'Tighten and nudge…', onSelect: () => open({ kind: 'tighten', k }) },
  ]
  if (canCompare) {
    items.push({
      label: 'Your voice / cloned voice',
      sep: true,
      items: [
        { label: 'Play your voice (before conversion)', onSelect: () => playUrl(yours!) },
        { label: 'Play cloned voice', onSelect: () => playUrl(cloned) },
      ],
    })
  }
  if (sess) {
    const converting = p.jobs.some((j) => j.kind === 'process' && j.key === sess.name && (j.state === 'queued' || j.state === 'running'))
    const sub: MenuItem[] = []
    if (sess.state === 'ready' && !sess.stale && sess.clean !== 'cloned') {
      sub.push({ label: 'Convert to cloned voice', disabled: converting, onSelect: () => void act.convertRecording(sess.name) })
    }
    sub.push({
      label: 'Delete recording…',
      danger: true,
      onSelect: async () => {
        if (await confirm({ title: `Delete recording ${sess.name}?`, body: `The recording (${mmss(sess.seconds)}) is deleted. This cannot be undone.`, confirmLabel: 'Delete recording', tone: 'danger' })) void act.deleteRecording(sess.name)
      },
    })
    items.push({ label: `Recording ${sessionLabel(sess.name)}`, sep: !canCompare, items: sub })
  }
  return items
}
