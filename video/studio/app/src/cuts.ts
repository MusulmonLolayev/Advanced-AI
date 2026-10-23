// Hand cuts, pure (no React): a drag on a take's wave becomes a cut, and the cut joins the take's `cuts`.
//
// TIME BASE. A cut [a, b] is in the take's own seconds, counted from the take's start (t_in) on the raw recording, BEFORE
// the trims, squeezes and nudge: timeline.edited() runs plan() (cuts + auto_cuts + the trims' cuts) and squeeze() on the raw
// take, and only then nudge(). So the wave's x axis (0 .. raw_length), trim_in, trim_out, the word times and the cuts are all
// one clock, and a nudge does not move a cut. check_makeup.ts tests this against studio/timeline.py.
import { editedTime, mergeSpans, type EditPlan } from './model'

export type Span = [number, number]
/** a selection snaps to this many seconds */
export const SNAP = 0.01
/** a shorter selection is a slip of the hand and is ignored */
export const MIN_SELECTION = 0.05
/** two decimals: what a cut shows, and what the server keeps (no float noise from the snap) */
export const r2 = (x: number) => Math.round(x * 100) / 100

/** the take's second under pointer x, on a strip `width` px wide starting at `left` px, for a take `len` s long */
export const xToTake = (x: number, left: number, width: number, len: number) => Math.min(Math.max(((x - left) / Math.max(width, 1)) * len, 0), len)

/** the strip's drag from take second `t0` to `t1` as a selection: snapped to 0.01 s, clamped to the trimmed region
 *  [trimIn, len - trimOut], or null when shorter than 0.05 s (after the clamp) */
export function selection(t0: number, t1: number, len: number, trimIn = 0, trimOut = 0): Span | null {
  const lo = Math.max(trimIn, 0)
  const hi = Math.min(len - trimOut, len)
  const a = Math.min(Math.max(r2(Math.min(t0, t1)), lo), hi)
  const b = Math.min(Math.max(r2(Math.max(t0, t1)), lo), hi)
  return b - a >= MIN_SELECTION - 1e-9 ? [r2(a), r2(b)] : null
}

/** `cuts` with `span` added: overlapping or touching cuts become one, sorted (the same merge as timeline.merge) */
export const addCut = (cuts: Span[], span: Span): Span[] => mergeSpans([...cuts, span]).map(([a, b]): Span => [r2(a), r2(b)])

/** `cuts` without the i-th */
export const removeCut = (cuts: Span[], i: number): Span[] => cuts.filter((_, j) => j !== i)

/** seconds the cuts remove (they are kept merged, so a plain sum) */
export const cutSeconds = (cuts: Span[]) => cuts.reduce((s, [a, b]) => s + (b - a), 0)

/** "2 parts cut (1.4 s)" */
export const cutsLabel = (cuts: Span[]) => `${cuts.length} part${cuts.length === 1 ? '' : 's'} cut (${cutSeconds(cuts).toFixed(1)} s)`

/** the take second (raw, the wave's clock) that plays at edited second `te`: the inverse of model.editedTime, for the wide editor's playhead */
export function rawTime(plan: EditPlan, total: number, te: number): number {
  let lo = 0
  let hi = total
  for (let i = 0; i < 40; i++) {
    const m = (lo + hi) / 2
    if (editedTime(plan, total, m) < te) lo = m
    else hi = m
  }
  return hi
}
