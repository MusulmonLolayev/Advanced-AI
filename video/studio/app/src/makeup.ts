// What the export will contain, from /api/project: how much of the lecture is your takes and how much the cloned voice.
// Pure, so check_makeup.ts can compare it with the counts the server gives (npm run check).
import { lineStates, totalSeconds } from './model'
import type { Project } from './types'

export type Makeup = { n: number; you: number; rest: number; total: number; youSec: number; saved: number; could: number }

export function makeup(p: Project): Makeup {
  const st = lineStates(p, null)
  const takes = st.filter((s) => s.kind === 'take')
  return {
    n: st.length,
    you: takes.length,
    rest: st.length - takes.length,
    total: totalSeconds(p),
    youSec: takes.reduce((a, s) => a + (s.b - s.a), 0),
    saved: takes.reduce((a, s) => a + ((s.take?.raw_length ?? 0) - (s.take?.length ?? 0)), 0),
    could: takes.reduce((a, s) => a + (s.take?.tighten.gain ?? 0), 0),
  }
}
