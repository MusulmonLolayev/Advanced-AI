// `npm run check`: the Export summary equals the counts the server's own fields give, on a few made-up projects.
// (esbuild bundles it; run with node.)
import { addCut, cutSeconds, cutsLabel, rawTime, removeCut, selection, xToTake, type Span } from './cuts'
import { makeup } from './makeup'
import { editedTime, planOf } from './model'
import type { Project, Take } from './types'

const take = (id: string, raw: number, len: number, gain: number) => ({ id, raw_length: raw, length: len, tighten: { gain }, rejected: false }) as unknown as Take
function project(n: number, spans: [number, string | null][]): Project {
  // n lines of 2 s; spans = [line, take id] for the lines that have a take
  const takes: Record<string, Take[]> = {}
  for (const [k, id] of spans) if (id) takes[String(k)] = [take(id, 3, 2.5, 0.25)]
  const lines = Array.from({ length: n }, (_, k) => [k * 2, `line ${k}`] as [number, string])
  const used = spans.filter(([, id]) => id).map(([, id]) => id as string)
  return {
    lines,
    scenes: lines.map(() => 'S'),
    takes,
    used,
    voice: {},
    settings: { missing: 'original', margin: '0.3' },
    edit_list: {
      lines: Array.from({ length: n }, (_, k) => [k, k * 2, k * 2 + 2, spans.find(([l]) => l === k)?.[1] ?? null]),
      voice: Array.from({ length: n }, (_, k) => [2, 'x', k * 2]),
      picture: [],
    },
  } as unknown as Project
}

let bad = 0
const eq = (what: string, a: unknown, b: unknown) => {
  if (a !== b) {
    bad++
    console.error(`FAIL ${what}: ${a} != ${b}`)
  }
}
for (const [n, spans] of [[5, []], [5, [[1, 'a@0'], [3, 'b@0']]], [4, [[0, 'a@0'], [1, 'b@0'], [2, 'c@0'], [3, 'd@0']]]] as [number, [number, string | null][]][]) {
  const p = project(n, spans)
  const m = makeup(p)
  eq('your takes = lines with a take in the edit list', m.you, p.edit_list.lines.filter((l) => l[3]).length)
  eq('your takes = used take ids', m.you, p.used.length)
  eq('you + rest = lines', m.you + m.rest, p.lines.length)
  eq('total = sum of the voice spans', m.total, p.edit_list.voice.reduce((a, v) => a + v[0], 0))
  eq('voice seconds = 2 s per take line', m.youSec, 2 * m.you)
  eq('saved = 0.5 s per take', Math.round(m.saved * 100), Math.round(50 * m.you))
}
// the strip's plan equals studio/timeline.plan: for this take (picture hold 1 s, play 4, hold 1.5, play 3, hold 0.5; trims 2.0 and 3.5, a cut at
// 5.2-5.6) timeline.plan gives cuts (0-1) (5.2-5.6) (9.5-10) and squeezes (1-2 to 0.25 s) (6.5-9.5 to 0.75 s) (computed by python, 2026-10-22)
const pic: [number, number, 'play' | 'hold'][] = [[0, 1, 'hold'], [1, 5, 'play'], [5, 6.5, 'hold'], [6.5, 9.5, 'play'], [9.5, 10, 'hold']]
const plan = planOf({ trim_in: 2, trim_out: 3.5, cuts: [[5.2, 5.6]] }, pic, 10)
eq('plan cuts', JSON.stringify(plan.cuts), JSON.stringify([[0, 1], [5.2, 5.6], [9.5, 10]]))
eq('plan squeezes', JSON.stringify(plan.sq), JSON.stringify([[1, 2, 0.25], [6.5, 9.5, 0.75]]))
eq('edited time of raw 5.8 s', Math.round(editedTime(plan, 10, 5.8) * 1000), 3650)       // 0.25 + 3.2 + (5.8 - 5.6)
eq('edited length', Math.round(editedTime(plan, 10, 10) * 1000), 5100)                   // 0.25 + 3.2 + 0.9 + 0.75

// hand cuts (cuts.ts): a drag becomes a selection in the take's own seconds (the wave's x axis, the clock timeline.plan reads cuts in),
// joins `cuts` by the same merge, and the plan and the edited length equal timeline.py's for the same edit. The expected values below
// were computed by python (studio.timeline.plan, squeeze and nudge on this take's tracks, 2026-10-23); the take is the one above.
const handCuts = (drags: [number, number][], tin = 0, tout = 0): Span[] => drags.reduce<Span[]>((c, [a, b]) => { const s = selection(a, b, 10, tin, tout); return s ? addCut(c, s) : c }, [])
const planFor = (edit: { trim_in?: number; trim_out?: number; cuts: Span[]; nudge?: number }) => {
  const pl = planOf(edit, pic, 10)
  return { cuts: JSON.stringify(pl.cuts), sq: JSON.stringify(pl.sq), len: Math.round((editedTime(pl, 10, 10) + Math.abs(edit.nudge ?? 0)) * 1000) }
}
const T2 = { trim_in: 2, trim_out: 3.5 }
let c = handCuts([[5.2, 5.6], [5.5, 6.0]])                                                 // an overlap: one cut
eq('overlap cuts', JSON.stringify(c), JSON.stringify([[5.2, 6]]))
let r = planFor({ cuts: c })
eq('overlap plan cuts', r.cuts, JSON.stringify([[5.2, 6]]))
eq('overlap plan squeezes', r.sq, '[]')
eq('overlap length', r.len, 9200)
c = handCuts([[5.2, 5.6]], 2, 3.5)                                                         // a cut inside the trims
r = planFor({ ...T2, cuts: c })
eq('inside plan cuts', r.cuts, JSON.stringify([[0, 1], [5.2, 5.6], [9.5, 10]]))
eq('inside length', r.len, 5100)
c = handCuts([[5.2, 5.6], [5.6, 5.9]], 2, 3.5)                                             // touching cuts join
eq('touching cuts', JSON.stringify(c), JSON.stringify([[5.2, 5.9]]))
r = planFor({ ...T2, cuts: c })
eq('touching plan cuts', r.cuts, JSON.stringify([[0, 1], [5.2, 5.9], [9.5, 10]]))
eq('touching length', r.len, 4800)
c = handCuts([[1.5, 2.5], [6.0, 7.0], [5.2, 5.6]], 2, 3.5)                                 // drags from inside the start trim and across the end trim: clamped to 2.0 and 6.5
eq('clamped to the trim', JSON.stringify(c), JSON.stringify([[2, 2.5], [5.2, 5.6], [6, 6.5]]))
r = planFor({ ...T2, cuts: c })                                                            // cuts touching both trims
eq('trim-touching plan cuts', r.cuts, JSON.stringify([[0, 1], [2, 2.5], [5.2, 5.6], [6, 6.5], [9.5, 10]]))
eq('trim-touching length', r.len, 4100)                                                    // python: 4.1
c = handCuts([[5.2, 5.6]], 2, 3.5)                                                         // a nudge does not move a cut; it adds |nudge| to the length
for (const nudge of [0.5, -0.5]) {
  r = planFor({ ...T2, cuts: c, nudge })
  eq(`nudge ${nudge} plan cuts`, r.cuts, JSON.stringify([[0, 1], [5.2, 5.6], [9.5, 10]]))
  eq(`nudge ${nudge} length`, r.len, 5600)
}
eq('too short is ignored', selection(3, 3.04, 10), null)
eq('snaps to 0.01', JSON.stringify(selection(3.004, 3.456, 10)), JSON.stringify([3, 3.46]))
eq('outside the trims is nothing', selection(0.5, 1.5, 10, 2, 3.5), null)
eq('pointer x to take second', xToTake(150, 50, 200, 10), 5)
eq('restore', JSON.stringify(removeCut([[1, 2], [3, 4]], 0)), JSON.stringify([[3, 4]]))
eq('cuts label', cutsLabel([[1, 2], [3, 3.4]]), '2 parts cut (1.4 s)')
eq('cut seconds', Math.round(cutSeconds([[1, 2], [3, 3.4]]) * 100), 140)
eq('rawTime inverts editedTime', Math.round(rawTime(plan, 10, editedTime(plan, 10, 5.8)) * 100), 580)
if (bad) throw new Error(`${bad} makeup check(s) failed`)
console.log('makeup check OK')
