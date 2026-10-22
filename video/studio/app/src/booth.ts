// The recording booth's engine: a port of presenter.py's page script (PAGE). It plays the silent video line by line,
// records the microphone (MediaRecorder, one piece a second, streamed through upload.ts), logs every moment the picture
// starts, stops or jumps, and records either a whole session (R) or one take of one line (L). Behaviour, event shapes
// and names are the old page's; the UI only reads `snap` and calls the methods.
import { Player } from './player'
import type { Tracks } from './types'
import { queueChunk, queueEvents, queueFinish, uploads, whenSent } from './upload'

/** [start in the video, text, [chunk start, chunk end, chunk text]] (presenter/lines.json) */
export type Line = [number, string, [number, number, string][]]
export type Level = { rms: number; peak: number; clip: boolean }
export type Snap = {
  line: number
  playing: boolean
  recording: boolean
  /** the line being recorded alone (L), else -1 */
  single: number
  count: number
  /** words of the current line already said (by the narration's pace) */
  said: number
  watching: string
  watchClock: string
  mic: string
  micError: string
  saved: string
  /** a mistake was marked on this line (X): shown until the line plays again */
  note: string
}
type Cb = {
  state: (s: Snap) => void
  level: (l: Level) => void
  setLine: (k: number) => void
  say: (m: string) => void
  setRecording: (r: boolean) => void
  /** a recording ended and everything is at the server (one: a single take) */
  recorded: (name: string, one: boolean) => void
  audio: () => Record<string, string>
}

const RATE = 1 / 1.1 // the narration's pace felt fast: the picture plays at 1/1.1
const MIME = 'audio/webm;codecs=opus'
const SLICE = 1000
let lastName = ''
/** a session is named by its start second (UTC); never twice the same */
function newName() {
  let d = new Date()
  let n: string
  while ((n = d.toISOString().replace(/[:.]/g, '-').slice(0, 19)) <= lastName) d = new Date(d.getTime() + 1000)
  return (lastName = n)
}
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))
export const dbfs = (x: number) => (x > 1e-5 ? 20 * Math.log10(x) : -100)

export class Booth {
  v: HTMLVideoElement
  build: string
  L: Line[]
  cb: Cb
  i = 0
  nxt = 0
  stopAt: number | null = null
  rec: MediaRecorder | null = null
  t0 = 0
  ev: unknown[][] = []
  seq = 0
  single: { line: number; timer: ReturnType<typeof setTimeout> | null } | null = null
  evTimer: ReturnType<typeof setInterval> | undefined
  starting = false
  cancelCount = false
  disposed = false
  words: { t: number; w: string }[] = []
  stream: MediaStream | null = null
  micId = ''
  countIn = 3
  snap: Snap = { line: 0, playing: false, recording: false, single: -1, count: 0, said: 0, watching: '', watchClock: '', mic: '', micError: '', saved: '', note: '' }
  private player: Player | null = null
  private watchCut: [number, number] | null = null
  private raf = 0
  private meterRaf = 0
  private actx: AudioContext | null = null
  private off: (() => void)[] = []
  private clipUntil = 0
  private peakHold = -100

  constructor(v: HTMLVideoElement, build: string, lines: Line[], cb: Cb, line = 0) {
    this.v = v
    this.build = build
    this.L = lines
    this.cb = cb
    this.i = this.nxt = Math.max(0, Math.min(line, lines.length - 1))
    if (lines[this.i]) v.currentTime = lines[this.i][0]
    try {
      this.micId = localStorage.getItem('presenterMic') || ''
      const c = localStorage.getItem('studioCountIn')
      if (c !== null && /^\d+$/.test(c)) this.countIn = +c
    } catch {
      /* private window: defaults */
    }
    v.defaultPlaybackRate = v.playbackRate = RATE
    const on = (n: string, f: () => void) => {
      v.addEventListener(n, f)
      this.off.push(() => v.removeEventListener(n, f))
    }
    on('playing', () => (this.log('play'), this.push({ playing: true })))
    on('pause', () => (this.log('hold'), this.push({ playing: false })))
    on('waiting', () => this.log('hold'))
    on('seeked', () => this.v.paused && this.log('hold')) // a jump while held: hold the new frame
    on('ended', () => this.lineEnded())
    this.setWords()
    const tick = () => {
      this.tick()
      this.raf = requestAnimationFrame(tick)
    }
    this.raf = requestAnimationFrame(tick)
  }

  // ─── state ───
  push(p: Partial<Snap>) {
    this.snap = { ...this.snap, ...p }
    this.cb.state(this.snap)
  }
  private log(kind: string, k?: number) {
    if (this.rec && this.t0 && !this.snap.watching) {
      const e: unknown[] = [(performance.now() - this.t0) / 1000, kind, this.v.currentTime, this.v.playbackRate]
      if (k !== undefined) e.push(k)
      this.ev.push(e)
    }
  }
  private setWords() {
    this.words = []
    for (const [a, b, text] of this.L[this.i]?.[2] ?? []) {
      const ws = text.split(/\s+/).filter(Boolean)
      const n = ws.reduce((x, w) => x + w.length + 1, 0)
      let c = 0
      for (const w of ws) {
        this.words.push({ t: a + ((b - a) * c) / n, w })
        c += w.length + 1
      }
    }
  }
  private show() {
    this.setWords()
    this.push({ line: this.i, said: this.saidNow(), note: '' })
    this.cb.setLine(this.i)
  }
  private saidNow() {
    if (this.snap.watching) return this.snap.said
    const t = this.v.currentTime
    return this.words.reduce((n, x) => n + (t >= x.t + 0.03 ? 1 : 0), 0)
  }
  private tick() {
    const s = this.saidNow()
    if (s !== this.snap.said) this.push({ said: s })
    this.frame()
    const v = this.v
    if (this.stopAt !== null && !v.paused && v.currentTime >= this.stopAt) {
      v.pause()
      v.currentTime = this.stopAt
      this.stopAt = null
      this.lineEnded()
    }
  }
  /** the line on screen changed from outside (the studio's selected line) */
  sync(k: number) {
    if (this.rec || this.snap.watching || k === this.i || !this.L[k]) return
    this.i = this.nxt = k
    this.v.pause()
    this.stopAt = null
    this.v.currentTime = this.L[k][0]
    this.setWords()
    this.push({ line: k, said: 0, note: '' })
  }

  // ─── playing, as the old page ───
  play(k: number) {
    this.i = Math.max(0, Math.min(k, this.L.length - 1))
    this.nxt = this.i + 1
    this.v.currentTime = this.L[this.i][0]
    this.stopAt = this.L[this.i + 1] ? this.L[this.i + 1][0] - 0.04 : null
    this.show()
    this.log('line', this.i)
    void this.v.play().catch(() => {})
  }
  next() {
    const v = this.v
    if (this.single) return this.stopTake() // → ends a one-take recording
    if (!v.paused) {
      v.pause() // finish this line now
      if (this.stopAt !== null) v.currentTime = this.stopAt
      this.stopAt = null
      return
    }
    if (this.stopAt !== null) return void v.play().catch(() => {}) // a line paused with Space: carry on
    if (this.nxt < this.L.length) this.play(this.nxt)
  }
  toggle() {
    const v = this.v
    if (!v.paused) return v.pause()
    if (this.stopAt !== null) return void v.play().catch(() => {})
    if (this.nxt < this.L.length) this.play(this.nxt)
  }
  back() {
    if (this.single) return this.cb.say('Recording a take: press → or L to stop it first.')
    const v = this.v
    v.pause()
    this.stopAt = null
    if (Math.abs(v.currentTime - this.L[this.i][0]) < 0.05) this.i = Math.max(0, this.i - 1)
    v.currentTime = this.L[this.i][0]
    this.nxt = this.i
    this.show()
  }
  /** pick a line without playing it (the arrow buttons of the prompter while stopped) */
  go(k: number) {
    if (this.single || this.snap.watching) return
    this.v.pause()
    this.stopAt = null
    this.i = this.nxt = Math.max(0, Math.min(k, this.L.length - 1))
    this.v.currentTime = this.L[this.i][0]
    this.show()
  }
  private lineEnded() {
    if (this.single && !this.single.timer) this.single.timer = setTimeout(() => this.stopTake(), 1000)
  }
  /** the take is over: the picture stops, the recording is finished and processed */
  stopTake() {
    if (!this.single || !this.rec) return
    if (this.single.timer) clearTimeout(this.single.timer)
    this.v.pause()
    this.stopAt = null
    this.nxt = Math.min(this.single.line + 1, this.L.length - 1)
    setTimeout(() => void this.toggleRec(), 30) // after the pause event, so it is logged before the stop
  }
  /** X: this line's take is a mistake; start the line over */
  retake() {
    if (!this.rec) return this.cb.say('X marks a mistake while recording. Press R to record, or L to record a take of just this line.')
    this.log('retake', this.i)
    if (this.single) {
      if (this.single.timer) clearTimeout(this.single.timer)
      this.single.timer = null
      this.play(this.i)
    } else {
      this.v.pause()
      this.stopAt = null
      this.v.currentTime = this.L[this.i][0]
      this.nxt = this.i
      this.show()
    }
    this.push({ note: `retake: line ${this.i + 1} starts over` })
  }

  // ─── the microphone ───
  private constraints(id: string): MediaStreamConstraints {
    return { audio: { echoCancellation: false, autoGainControl: true, ...(id ? { deviceId: { exact: id } } : {}) } }
  }
  /** the chosen microphone; if it is gone, the default one. Also starts the level meter. */
  async openMic(id = this.micId): Promise<void> {
    this.closeMic()
    let stream: MediaStream | null = null
    try {
      if (!navigator.mediaDevices) throw new Error('no microphone access in this page')
      if (id) stream = await navigator.mediaDevices.getUserMedia(this.constraints(id)).catch(() => null)
      stream ??= await navigator.mediaDevices.getUserMedia(this.constraints(''))
    } catch (e) {
      this.push({ mic: '', micError: (e as Error).message || String(e) })
      return
    }
    if (this.disposed) return stream.getTracks().forEach((t) => t.stop())
    this.stream = stream
    this.push({ mic: stream.getAudioTracks()[0]?.label ?? '', micError: '' })
    const ctx = new AudioContext()
    this.actx = ctx
    const an = ctx.createAnalyser()
    an.fftSize = 1024
    ctx.createMediaStreamSource(stream).connect(an)
    const buf = new Float32Array(an.fftSize)
    const draw = () => {
      if (this.actx !== ctx) return
      an.getFloatTimeDomainData(buf)
      let peak = 0
      let sum = 0
      for (const x of buf) {
        peak = Math.max(peak, Math.abs(x))
        sum += x * x
      }
      const now = performance.now()
      const pk = dbfs(peak)
      if (pk > -1) this.clipUntil = now + 1500
      this.peakHold = Math.max(pk, this.peakHold - 0.4) // the peak falls slowly
      this.cb.level({ rms: dbfs(Math.sqrt(sum / buf.length)), peak: this.peakHold, clip: now < this.clipUntil })
      this.meterRaf = requestAnimationFrame(draw)
    }
    this.meterRaf = requestAnimationFrame(draw)
  }
  private closeMic() {
    cancelAnimationFrame(this.meterRaf)
    this.stream?.getTracks().forEach((t) => t.stop())
    this.stream = null
    void this.actx?.close().catch(() => {})
    this.actx = null
  }
  async setMic(id: string) {
    this.micId = id
    try {
      localStorage.setItem('presenterMic', id)
    } catch {
      /* not remembered */
    }
    if (!this.rec) await this.openMic(id)
  }
  setCountIn(n: number) {
    this.countIn = n
    try {
      localStorage.setItem('studioCountIn', String(n))
    } catch {
      /* not remembered */
    }
  }
  static async devices(): Promise<MediaDeviceInfo[]> {
    try {
      return (await navigator.mediaDevices.enumerateDevices()).filter((d) => d.kind === 'audioinput')
    } catch {
      return []
    }
  }
  get currentDeviceId() {
    return this.stream?.getAudioTracks()[0]?.getSettings().deviceId ?? ''
  }

  // ─── recording ───
  /** R (a whole session), or L (`one`: one take of the line on screen) */
  async toggleRec(one = false) {
    if (this.rec) {
      this.log('stop')
      this.rec.stop()
      return
    }
    if (this.snap.count > 0) {
      this.cancelCount = true // Esc / the button again: the count-in is cancelled
      return
    }
    if (this.starting) return
    this.starting = true
    try {
      if (!this.stream) await this.openMic()
      const stream = this.stream
      if (!stream) return this.cb.say('No microphone: ' + (this.snap.micError || 'not available') + '. Recording needs https or the ssh tunnel (http://localhost:8081).')
      if (one) {
        // the line's first frame while counting in
        this.v.pause()
        this.stopAt = null
        this.v.currentTime = this.L[this.i][0]
      }
      this.cancelCount = false
      for (let n = this.countIn; n > 0 && !this.cancelCount; n--) {
        this.push({ count: n })
        await sleep(1000)
      }
      this.push({ count: 0 })
      if (this.cancelCount || this.disposed) return
      this.start(stream, one)
    } finally {
      this.starting = false
      this.push({ count: 0 })
    }
  }
  private start(stream: MediaStream, one: boolean) {
    this.ev = []
    this.seq = 0
    this.single = one ? { line: this.i, timer: null } : null
    const name = newName()
    const rec = new MediaRecorder(stream, { mimeType: MIME })
    this.rec = rec
    rec.ondataavailable = (e) => {
      if (e.data.size) void queueChunk(this.build, name, this.seq++, e.data)
    }
    rec.onstart = () => {
      this.t0 = performance.now()
      this.ev.push([0, this.v.paused ? 'hold' : 'play', this.v.currentTime, this.v.playbackRate])
      if (this.single) this.play(this.single.line) // the line, from its start
      else if (!this.v.paused || this.stopAt !== null) this.ev.push([0, 'line', this.L[this.i][0], this.v.playbackRate, this.i])
      this.evTimer = setInterval(() => void queueEvents(this.build, name, this.ev), 5000)
      uploads.setRecording(true)
      this.cb.setRecording(true)
      this.push({ recording: true, single: this.single ? this.single.line : -1, saved: '', note: '' })
    }
    rec.onstop = async () => {
      clearInterval(this.evTimer)
      const oneLine = this.single
      if (oneLine?.timer) clearTimeout(oneLine.timer)
      this.single = null
      this.rec = null
      void queueEvents(this.build, name, this.ev)
      this.t0 = 0
      void queueFinish(this.build, name)
      uploads.setRecording(false)
      this.cb.setRecording(false)
      this.push({ recording: false, single: -1, note: '' })
      if (this.disposed) this.closeMic()
      await whenSent()
      if (uploads.error()) return
      this.push({ saved: name })
      this.cb.recorded(name, !!oneLine)
    }
    rec.start(SLICE)
  }

  // ─── watching a take (as it will appear in the video, or in context) ───
  watch(id: string, tracks: Tracks, spans: [number, number, number, string | null][], cut: [number, number] | null, at = 0) {
    if (this.rec) return this.cb.say('Watching is not possible while recording.')
    if (!this.player)
      this.player = new Player(this.v, () => this.cb.audio(), {
        clock: (T, total) => {
          const c = this.watchCut
          const where = c ? (T < c[0] ? 'end of the line before · ' : T < c[1] ? 'this take · ' : 'start of the line after · ') : ''
          const s = `${where}${T.toFixed(1)} / ${total.toFixed(1)} s`
          if (s !== this.snap.watchClock) this.push({ watchClock: s })
        },
        end: () => this.stopWatch(),
      })
    this.watchCut = cut
    this.stopAt = null
    this.push({ watching: id }) // the page's own view logs nothing while a take plays
    this.player.load(tracks, spans, at)
    this.player.play()
  }
  /** Space on a watched take */
  toggleWatch() {
    this.player?.toggle()
  }
  stopWatch() {
    if (!this.snap.watching) return
    this.player?.pause()
    this.push({ watching: '', watchClock: '' })
    this.v.playbackRate = this.v.defaultPlaybackRate
    this.stopAt = null
    this.v.currentTime = this.L[this.i][0]
    this.v.pause()
    this.nxt = this.i
  }
  /** called every frame while a take plays */
  frame() {
    if (this.snap.watching) this.player?.frame()
  }

  /** L: one take of the line on screen; it stops itself 1 s after the line */
  recordTake() {
    if (this.single) return this.stopTake()
    if (this.rec) return this.cb.say('A recording is running: stop it with R first.')
    if (this.snap.watching) this.stopWatch()
    void this.toggleRec(true)
  }

  dispose() {
    this.disposed = true
    cancelAnimationFrame(this.raf)
    this.off.forEach((f) => f())
    if (this.single?.timer) clearTimeout(this.single.timer)
    this.player?.pause()
    this.v.pause()
    if (this.rec) {
      // leaving while recording: finish and send what there is (onstop queues events and finish, then closes the mic)
      this.log('stop')
      this.rec.stop()
    } else this.closeMic()
  }
}
