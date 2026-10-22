// `npm run check`: the Export summary equals the counts the server's own fields give, on a few made-up projects.
// (esbuild bundles it; run with node.)
import { makeup } from './makeup'
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
if (bad) throw new Error(`${bad} makeup check(s) failed`)
console.log('makeup check OK')
