// What the Edit mode derives from /api/project: line states, sections, the edit list's level and its long silences,
// and the edit list's voice levels.
import type { EditorLangs, LangState, Levels, Project, Take, TakeEdit } from './types'

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


// ─── what an edit removes, in the raw take's seconds: mirrors studio/timeline.plan (check_makeup.ts compares them) ───
type Span = [number, number]
type Squeeze = [number, number, number]
export function mergeSpans(spans: Span[]): Span[] {
  const out: Span[] = []
  for (const [a, b] of spans.map(([p, q]): Span => (p <= q ? [p, q] : [q, p])).sort((x, y) => x[0] - y[0] || x[1] - y[1])) {
    if (out.length && a <= out[out.length - 1][1]) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b)
    else if (b > a) out.push([a, b])
  }
  return out
}
function validSqueezes(sq: Squeeze[]): Squeeze[] {
  const out: Squeeze[] = []
  let prev = 0
  for (const [x, y, n] of sq.map(([a, b, n]): Squeeze => [Math.min(a, b), Math.max(a, b), n]).sort((p, q) => p[0] - q[0] || p[1] - q[1] || p[2] - q[2])) {
    if (n > 1e-9 && n < y - x - 1e-9 && x >= prev - 1e-9) {
      out.push([x, y, n])
      prev = y
    }
  }
  return out
}
/** the picture holds still where it says so; a trim removes the still parts and speeds up (up to 4x) the playing ones */
function fastForward(picture: [number, number, 'play' | 'hold'][], spans: Span[]): [Span[], Squeeze[]] {
  const still = mergeSpans(picture.filter((p) => p[2] === 'hold').map((p): Span => [p[0], p[1]]))
  const cuts: Span[] = []
  const sq: Squeeze[] = []
  for (const [lo, hi] of spans) {
    let t = lo
    for (let [x, y] of [...still, [hi, hi] as Span]) {
      x = Math.min(Math.max(x, lo), hi)
      y = Math.min(Math.max(y, lo), hi)
      const p = x - t
      if (p > 1e-9 && Math.max(p / 4, 0.15) < p - 1e-9) sq.push([t, x, Math.max(p / 4, 0.15)])
      if (y > x) cuts.push([x, y])
      t = Math.max(t, y)
    }
  }
  return [mergeSpans(cuts), sq]
}
export type EditPlan = { cuts: Span[]; sq: Squeeze[] }
export function planOf(edit: TakeEdit, picture: [number, number, 'play' | 'hold'][], total: number): EditPlan {
  const ends: Span[] = []
  if (edit.trim_in) ends.push([0, Math.min(edit.trim_in, total)])
  if (edit.trim_out) ends.push([Math.max(total - edit.trim_out, 0), total])
  const [c, s] = fastForward(picture, ends)
  return { cuts: mergeSpans([...(edit.cuts ?? []), ...(edit.auto_cuts ?? []), ...c]), sq: validSqueezes([...(edit.squeeze ?? []), ...s]) }
}
/** where raw take time `tt` lands in the edited take (kept parts, squeezed ones faster) */
export function editedTime(plan: EditPlan, total: number, tt: number): number {
  const f = plan.sq.map(([x, y, n]) => [x, y, (y - x) / n] as Squeeze)
  const pts = [...new Set([0, total, ...plan.cuts.flat(), ...f.flatMap((s) => [s[0], s[1]])].map((x) => Math.min(Math.max(x, 0), total)))].sort((a, b) => a - b)
  let out = 0
  for (let i = 0; i + 1 < pts.length; i++) {
    const u = pts[i]
    const v = pts[i + 1]
    const m = (u + v) / 2
    if (v - u <= 1e-9 || plan.cuts.some(([a, b]) => a < m && m < b)) continue
    const s = f.find(([a, b]) => a < m && m < b)
    out += Math.max(Math.min(v, tt) - u, 0) / (s ? s[2] : 1)
  }
  return out
}
