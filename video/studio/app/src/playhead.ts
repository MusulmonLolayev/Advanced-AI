// The playhead lives outside React state: it changes 30 times a second while playing, and only the few components
// that show it (Playhead, Timecode, the monitor) subscribe, so the 200-line script and the timeline clips do not re-render.
import { useSyncExternalStore } from 'react'

let T = 0
const subs = new Set<() => void>()
export const playhead = {
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
export const usePlayhead = () => useSyncExternalStore(playhead.subscribe, playhead.get)
