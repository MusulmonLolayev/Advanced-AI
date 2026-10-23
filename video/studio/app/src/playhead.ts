// The playhead lives outside React state: it changes 30 times a second while playing, and only the few components
// that show it (Playhead, Timecode, the monitor) subscribe, so the 200-line script and the timeline clips do not re-render.
import { useSyncExternalStore } from 'react'

function store() {
  let T = 0
  const subs = new Set<() => void>()
  return {
    get: () => T,
    set(t: number) {
      if (t === T) return
      T = t
      subs.forEach((f) => f())
    },
    subscribe(f: () => void) {
      subs.add(f)
      return () => subs.delete(f)
    },
  }
}
export const playhead = store()
export const usePlayhead = () => useSyncExternalStore(playhead.subscribe, playhead.get)
/** the clock of a take played alone (its edited seconds), for the wide take editor's moving line */
export const takeHead = store()
export const useTakeHead = () => useSyncExternalStore(takeHead.subscribe, takeHead.get)
