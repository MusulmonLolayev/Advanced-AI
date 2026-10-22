import { useEffect, useState } from 'react'
import { fetchLevels } from '../../api'
import { ORIGINAL } from '../../model'
import type { Levels } from '../../types'

/** Voice levels of the given sources (sessions and "__original__"), loaded one by one and cached by api.ts. */
export function useLevels(build: string, srcs: string[], version = 0): Record<string, Levels> {
  const [have, setHave] = useState<Record<string, Levels>>({})
  const vkey = (s: string) => (s === ORIGINAL ? version : 0) // the original voice follows the video
  const key = build + '|' + srcs.join(',') + '|' + version
  useEffect(() => {
    let live = true
    srcs.forEach((s) =>
      fetchLevels(build, s, vkey(s)).then(
        (lv) => live && setHave((h) => (h[build + s + vkey(s)] === lv ? h : { ...h, [build + s + vkey(s)]: lv })),
        () => {},
      ),
    )
    return () => {
      live = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])
  const out: Record<string, Levels> = {}
  for (const s of srcs) if (have[build + s + vkey(s)]) out[s] = have[build + s + vkey(s)]
  return out
}
