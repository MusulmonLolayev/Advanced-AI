// The Edit mode's transport. It owns the Player (src/player.ts) and says what it is playing: the whole lecture's edit
// list, one take (alone or in context), or a version's scene clip (the video itself, with its own sound). Time on the
// timeline is the edit list's; the Player clock drives the playhead store. Mirrors static/editor/main.js.
import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from 'react'
import { fetchLine } from '../../api'
import { useToast } from '../../components'
import { lineAt, type LineState } from '../../model'
import { Player, glue, spanOf } from '../../player'
import { playhead } from '../../playhead'
import type { Project, Take, VersionRow } from '../../types'

export type Playing = { kind: 'lecture' } | { kind: 'take'; label: string } | { kind: 'version'; label: string }

export type Transport = {
  playing: boolean
  what: Playing
  /** clock of a take or a version, "0:03 / 0:15" (the lecture's is the playhead) */
  sideClock: string
  seek: (T: number) => void
  toggle: () => void
  playLine: (k: number) => void
  playTake: (t: Take, n: number) => void
  playContext: (t: Take, n: number) => Promise<void>
  watchVersion: (v: VersionRow, scene: string, k: number) => void
  back: () => void
}

const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`

export function usePlayer(p: Project, states: LineState[], videoRef: RefObject<HTMLVideoElement | null>, line: number, setLine: (k: number) => void): Transport {
  const toast = useToast()
  const [playing, setPlaying] = useState(false)
  const [what, setWhat] = useState<Playing>({ kind: 'lecture' })
  const [sideClock, setSideClock] = useState('')
  const player = useRef<Player | null>(null)
  const cur = useRef({ p, states, line, what, setLine })
  cur.current = { p, states, line, what, setLine }
  const quiet = useRef(false) // a seek by the user: the span the player lands in is not a "playing entered a line" event
  const lastSpan = useRef(-1)
  const videoSrc = `${p.video}?v=${p.video_version}`
  const elKey = useMemo(() => JSON.stringify(p.edit_list), [p.edit_list])

  const loadAll = useCallback((at: number) => {
    const P = player.current
    if (!P) return
    const el = cur.current.p.edit_list
    quiet.current = true
    P.load(el, el.lines, at)
    quiet.current = false
    setWhat({ kind: 'lecture' })
    setSideClock('')
  }, [])

  const leaveVersion = useCallback(() => {
    const P = player.current
    const v = videoRef.current
    if (!P || !v || !P.off) return
    P.off = false
    v.pause()
    v.muted = true
    v.src = `${cur.current.p.video}?v=${cur.current.p.video_version}`
  }, [videoRef])

  // the player and its frame loop
  useEffect(() => {
    const v = videoRef.current
    if (!v) return
    let last = ''
    const P = new Player(v, () => cur.current.p.audio, {
      state: setPlaying,
      clock: (T, total) => {
        if (cur.current.what.kind === 'lecture') playhead.set(T)
        else {
          const s = `${mmss(T)} / ${mmss(total)}`
          if (s !== last) setSideClock((last = s))
        }
      },
      line: (k) => {
        if (cur.current.what.kind !== 'lecture') return
        if (quiet.current) lastSpan.current = k
        else if (k !== lastSpan.current) {
          lastSpan.current = k
          cur.current.setLine(k)
        }
      },
    })
    player.current = P
    let raf = 0
    const loop = () => {
      P.frame()
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
    return () => {
      cancelAnimationFrame(raf)
      P.pause()
      P.off = false
      player.current = null
    }
  }, [videoRef])

  // the lecture video and the edit list: again whenever either changes (playing resumes where it was)
  const lastSrc = useRef('')
  useEffect(() => {
    const v = videoRef.current
    const P = player.current
    if (!v || !P) return
    const rebuilt = !!lastSrc.current && lastSrc.current !== videoSrc
    if (rebuilt) {
      leaveVersion()
      toast('The lecture video was rebuilt')
    }
    lastSrc.current = videoSrc
    if (!v.src.endsWith(videoSrc) && !P.off) v.src = videoSrc
    if (!rebuilt && (cur.current.what.kind !== 'lecture' || P.off)) return
    const T = P.total ? P.T : playhead.get()
    const was = P.playing
    loadAll(T)
    if (was) P.play()
  }, [elKey, videoSrc, loadAll, leaveVersion, videoRef, toast])

  const seek = useCallback(
    (T: number) => {
      const P = player.current
      if (!P) return
      if (cur.current.what.kind !== 'lecture') {
        leaveVersion()
        loadAll(T)
      } else {
        quiet.current = true
        P.seek(T)
        quiet.current = false
      }
      playhead.set(P.T)
      cur.current.setLine(lineAt(cur.current.states, T))
    },
    [leaveVersion, loadAll],
  )

  const back = useCallback(() => {
    const s = cur.current.states[cur.current.line]
    leaveVersion()
    loadAll(s ? s.a : 0)
    playhead.set(s ? s.a : 0)
  }, [leaveVersion, loadAll])

  const playLine = useCallback(
    (k: number) => {
      const P = player.current
      if (!P) return
      seek(cur.current.states[k].a)
      cur.current.setLine(k)
      P.play()
    },
    [seek],
  )

  const toggle = useCallback(() => player.current?.toggle(), [])

  const startTake = useCallback(
    (tracks: Take['tracks'], t: Take, label: string, at = 0) => {
      const P = player.current
      if (!P) return
      leaveVersion()
      P.load(tracks, [[t.line, 0, spanOf(tracks), t.id]], at)
      setWhat({ kind: 'take', label })
      P.play()
    },
    [leaveVersion],
  )
  const playTake = useCallback((t: Take, n: number) => startTake(t.tracks, t, `take T${n}`), [startTake])
  const playContext = useCallback(
    async (t: Take, n: number) => {
      try {
        const c = (await fetchLine(cur.current.p.build, t.line)).context
        startTake(glue([c.before, t.tracks, c.after]), t, `take T${n} in context`, Math.max(0, spanOf(c.before) - 1))
      } catch (e) {
        toast(`Failed: ${(e as Error).message}`)
      }
    },
    [startTake, toast],
  )

  const watchVersion = useCallback(
    (x: VersionRow, scene: string, k: number) => {
      const P = player.current
      const v = videoRef.current
      if (!P || !v || !x.video) return
      P.pause()
      P.off = true
      v.muted = false
      v.playbackRate = 1
      const at = x.line_starts[String(k)] ?? 0
      v.addEventListener(
        'loadedmetadata',
        () => {
          v.currentTime = at
          void v.play().catch(() => {})
        },
        { once: true },
      )
      v.src = x.video
      setWhat({ kind: 'version', label: `v${x.n} of ${scene}` })
    },
    [videoRef],
  )

  return { playing, what, sideClock, seek, toggle, playLine, playTake, playContext, watchVersion, back }
}
