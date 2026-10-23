// The player: plays the two tracks (voice, picture) the server builds, the same ones the export renders. A port of
// the old editor's player (removed 2026-10-22); the sync rules are the old ones, unchanged. It drives a video element and an audio map it is
// handed, nothing else.
import type { LineSpan, PictureSpan, Tracks, VoiceSpan } from './types'

type Placed<P> = { t: number; p: P }

export type PlayerUI = {
  state?: (playing: boolean) => void
  clock?: (T: number, total: number) => void
  /** playing (or a seek) enters line k */
  line?: (k: number) => void
  /** playing reached the end */
  end?: () => void
}

export class Player {
  v: HTMLVideoElement
  urls: () => Record<string, string>
  ui: PlayerUI
  /** a version's scene clip plays in the video itself (with its own sound), not the two tracks */
  off = false
  vp: Placed<PictureSpan>[] = []
  ap: Placed<VoiceSpan>[] = []
  total = 0
  T = 0
  playing = false
  T0 = 0
  w0 = 0
  audios: Record<string, { url: string; el: HTMLAudioElement }> = {}
  cur: HTMLAudioElement | null = null
  spans: LineSpan[] = []
  lastA: Placed<VoiceSpan> | null = null

  constructor(v: HTMLVideoElement, urls: () => Record<string, string>, ui: PlayerUI = {}) {
    this.v = v
    this.urls = urls
    this.ui = ui
    // a paused picture shows the frame at the playhead: when the video's data arrives after a load or a seek, put it there
    const repaint = () => {
      if (!this.off && !this.playing && this.vp.length) this.sync(true)
    }
    for (const ev of ['loadedmetadata', 'loadeddata', 'canplay']) v.addEventListener(ev, repaint)
  }

  load(tr: Tracks, spans: LineSpan[], at = 0) {
    this.pause()
    this.vp = Player.place(tr.picture)
    this.ap = Player.place(tr.voice)
    this.total = this.vp.length ? this.vp[this.vp.length - 1].t + this.vp[this.vp.length - 1].p[0] : 0
    this.spans = spans
    this.lastA = null
    this.seek(at)
  }
  static place<P extends [number, ...unknown[]]>(track: P[]): Placed<P>[] {
    let t = 0
    return track.map((p) => {
      const o = { t, p }
      t += p[0]
      return o
    })
  }
  static find<P>(list: Placed<P>[], T: number): Placed<P> | null {
    let lo = 0
    let hi = list.length - 1
    let k = -1
    while (lo <= hi) {
      const m = (lo + hi) >> 1
      if (list[m].t <= T + 1e-9) {
        k = m
        lo = m + 1
      } else hi = m - 1
    }
    return k < 0 ? null : list[k]
  }
  audio(src: string): HTMLAudioElement | null {
    const url = this.urls()[src]
    if (!url) return null
    const a = this.audios[src]
    if (!a || a.url !== url) {
      if (a) a.el.pause()
      const el = new Audio(url)
      el.preload = 'auto'
      this.audios[src] = { url, el }
    }
    return this.audios[src].el
  }
  silence() {
    Object.values(this.audios).forEach((a) => a.el.pause())
  }
  state() {
    this.ui.state?.(this.off ? !this.v.paused : this.playing)
  }
  play() {
    if (this.off) return void this.v.play().catch(() => {})
    if (this.T >= this.total - 0.01) this.T = 0
    this.playing = true
    this.T0 = this.T
    this.w0 = performance.now()
    this.state()
  }
  pause() {
    if (this.off) return this.v.pause()
    this.playing = false
    this.v.pause()
    this.silence()
    this.state()
  }
  toggle() {
    if (this.off) return this.v.paused ? this.play() : this.pause()
    this.playing ? this.pause() : this.play()
  }
  seek(T: number) {
    if (this.off) {
      this.v.currentTime = Math.max(0, T)
      return
    }
    this.T = Math.max(0, Math.min(T, this.total))
    this.T0 = this.T
    this.w0 = performance.now()
    this.sync(true)
  }
  clock() {
    this.ui.clock?.(this.T, this.total)
  }
  /** one animation frame: advance the clock, then bring the media elements to it */
  frame() {
    const v = this.v
    if (this.off) {
      this.T = v.currentTime
      this.total = v.duration || 0
      this.state()
      this.clock()
      return
    }
    if (this.playing) {
      this.T = this.T0 + (performance.now() - this.w0) / 1000
      if (this.T >= this.total) {
        this.T = this.total
        this.pause()
        this.sync(false)
        this.ui.end?.()
        return
      }
    }
    this.sync(false)
  }
  // Whether to put a media element at `want`. A forced seek (the user moved) or a jump (a voice piece that does not
  // continue the one before it) always lands exactly; otherwise only drift beyond `tol`, and never while the element
  // is still seeking or buffering: its currentTime then lags the clock, and seeking again each frame restarts the
  // load and replays the same fragment (worst on a slow link).
  static seekNow(el: HTMLMediaElement, want: number, force: boolean, jump: boolean, tol: number): boolean {
    if (force || jump) return true
    if (el.seeking || el.readyState < 3) return false
    return Math.abs(el.currentTime - want) > tol
  }
  sync(force: boolean) {
    const v = this.v
    const T = this.T
    const pv = Player.find(this.vp, T)
    const pa = Player.find(this.ap, T)
    if (pv) {
      const [, kind, a, , s] = pv.p
      const local = T - pv.t
      if (kind === 'play') {
        const want = a + local * s
        const rate = Math.min(16, Math.max(0.0625, s)) // browsers honour 0.0625 to 16; the squeezes use up to ~3.6
        if (v.playbackRate !== rate) v.playbackRate = rate
        if (Player.seekNow(v, want, force, false, 0.25)) v.currentTime = want
        if (this.playing && v.paused) v.play().catch(() => {})
        if (!this.playing && !v.paused) v.pause()
      } else {
        if (!v.paused) v.pause()
        if (Math.abs(v.currentTime - a) > 0.03) v.currentTime = a
      }
    }
    let el: HTMLAudioElement | null = null
    if (pa && pa.p[1]) {
      el = this.audio(pa.p[1])
      if (el) {
        const want = pa.p[2] + (T - pa.t)
        const q = this.lastA
        // entering a piece: contiguous with the one before (same source, its position plus its length) plays on
        const entered = pa !== q
        const same = !!q && q.p[1] === pa.p[1] && Math.abs(q.p[2] + q.p[0] - pa.p[2]) < 0.005
        if (Player.seekNow(el, want, force, entered && !same, this.playing ? 0.25 : 0.15)) el.currentTime = want
        if (this.playing && el.paused) el.play().catch(() => {})
        if (!this.playing && !el.paused) el.pause()
      }
    }
    this.lastA = pa
    if (this.cur && this.cur !== el) this.cur.pause()
    this.cur = el
    this.clock()
    const sp = this.spans.find((x) => T >= x[1] && T < x[2]) ?? this.spans[this.spans.length - 1]
    if (sp) this.ui.line?.(sp[0])
  }
}

/** Tracks end to end (a take in context); a shorter track is padded like the edit list. Mirrors the old takes panel's glue(). */
export function glue(parts: Tracks[]): Tracks {
  const out: Tracks = { voice: [], picture: [] }
  for (const tr of parts) {
    const v = tr.voice.slice()
    const p = tr.picture.slice()
    const gap = v.reduce((a, x) => a + x[0], 0) - p.reduce((a, x) => a + x[0], 0)
    if (gap > 1e-6) {
      const last = p[p.length - 1]
      p.push([gap, 'hold', last ? (last[1] === 'play' ? (last[3] ?? 0) : last[2]) : 0, null, 1])
    } else if (gap < -1e-6) v.push([-gap, null, 0])
    out.voice.push(...v)
    out.picture.push(...p)
  }
  return out
}
export const spanOf = (tr: Tracks) => tr.picture.reduce((a, x) => a + x[0], 0)
