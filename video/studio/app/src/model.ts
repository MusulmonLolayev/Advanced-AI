// What the Edit mode derives from /api/project: line states, sections, the edit list's level and its long silences,
// and the edit list's voice levels.
import type { EditorLangs, LangState, Levels, Project, Take } from './types'

export type LineKind = 'take' | 'mistake' | 'clone' | 'silent'
export type LineState = {
  kind: LineKind
  take: Take | null
  voice: 'fail' | 'listen' | null
  lang: LangState | null
  a: number
  b: number
}

export const ORIGINAL = '__original__'

export function lineStates(p: Project, langs: EditorLangs | null): LineState[] {
  const spans = new Map(p.edit_list.lines.map((s) => [s[0], s]))
  return p.lines.map((_, k) => {
    const sp = spans.get(k)
    const takes = p.takes[String(k)] ?? []
    const tid = sp?.[3] ?? null
    const take = takes.find((t) => t.id === tid) ?? null
    const allBad = takes.length > 0 && takes.every((t) => t.rejected)
    const vm = p.voice[String(k)]
    const kind: LineKind = take ? 'take' : allBad ? 'mistake' : p.settings.missing === 'silent' ? 'silent' : 'clone'
    return {
      kind,
      take,
      voice: !take && vm ? (!vm.ok ? 'fail' : vm.listen ? 'listen' : null) : null,
      lang: langs?.lines[String(k)]?.state ?? null,
      a: sp?.[1] ?? 0,
      b: sp?.[2] ?? 0,
    }
  })
}

export type Section = { scene: string; from: number; to: number; a: number; b: number }

export function sections(p: Project, st: LineState[]): Section[] {
  const out: Section[] = []
  p.scenes.forEach((scene, k) => {
    const last = out[out.length - 1]
    if (last && last.scene === scene) {
      last.to = k
      last.b = st[k].b
    } else out.push({ scene, from: k, to: k, a: st[k].a, b: st[k].b })
  })
  return out
}

export const totalSeconds = (p: Project) => p.edit_list.voice.reduce((a, v) => a + v[0], 0)

/** Edit-list time -> the line it falls in. */
export function lineAt(st: LineState[], T: number): number {
  let lo = 0
  let hi = st.length - 1
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1
    if (st[mid].a <= T) lo = mid
    else hi = mid - 1
  }
  return lo
}

/** The edit list's two voices as one level array each (dB at 50 Hz): YOU = recorded takes, CLONE = the video's own voice. */
export type Composite = { you: Int8Array; clone: Int8Array; n: number; total: number }
export const FLOOR = -80

export function composite(p: Project, src: Record<string, Levels>): Composite {
  const total = totalSeconds(p)
  const n = Math.round(total * 50)
  const you = new Int8Array(n).fill(FLOOR)
  const clone = new Int8Array(n).fill(FLOOR)
  let t = 0
  for (const [d, s, pos] of p.edit_list.voice) {
    const i0 = Math.round(t * 50)
    const i1 = Math.min(n, Math.round((t + d) * 50))
    t += d
    const lv = s ? src[s] : undefined
    if (!lv) continue
    const dst = s === ORIGINAL ? clone : you
    const j0 = Math.round(pos * 50)
    for (let i = i0; i < i1; i++) {
      const v = lv.db[j0 + i - i0]
      dst[i] = v === undefined ? FLOOR : Math.max(FLOOR, v)
    }
  }
  return { you, clone, n, total }
}

/** Runs of quiet frames of `minSec` or more, across line boundaries (the server's rule: a third of the way from room to voice). */
export function longSilences(c: Composite, minSec: number): { a: number; b: number }[] {
  const all: number[] = []
  for (let i = 0; i < c.n; i += 5) all.push(Math.max(c.you[i], c.clone[i]))
  all.sort((x, y) => x - y)
  const room = all[Math.floor(all.length * 0.1)] ?? FLOOR
  const voice = all[Math.floor(all.length * 0.9)] ?? 0
  const th = room + (voice - room) / 3
  const need = Math.max(1, Math.ceil(minSec * 50))
  const out: { a: number; b: number }[] = []
  let s = -1
  for (let i = 0; i <= c.n; i++) {
    const quiet = i < c.n && Math.max(c.you[i], c.clone[i]) <= th
    if (quiet && s < 0) s = i
    else if (!quiet && s >= 0) {
      if (i - s >= need) out.push({ a: s / 50, b: i / 50 })
      s = -1
    }
  }
  return out
}

export const sourcesOf = (p: Project): string[] => [...new Set(p.edit_list.voice.map((v) => v[1]).filter((s): s is string => !!s))]

export const MAKING = ['queued', 'voicing', 'rendering']

/** Something the server is still making: a job, a version being voiced or rendered, a recording being cleaned. */
export const busy = (p: Project) =>
  p.jobs.some((j) => j.state === 'queued' || j.state === 'running') ||
  p.sessions.some((s) => ['recording', 'recorded', 'processing'].includes(s.state)) ||
  Object.values(p.versions).flat().some((v) => MAKING.includes(v.state))

