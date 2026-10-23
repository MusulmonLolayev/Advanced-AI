// Response shapes of the studio's read APIs, typed from real responses (2026-10-22).

/** [start seconds in the lecture video, text] */
export type LineRow = [number, string]

export type VoiceMark = { ok: boolean; listen: boolean; fails: string[]; heard: string }

/** extra: [word, start, end]; changed: [said, heard, start, end] (seconds in the recording) */
export type TakeCheck = { missing: string[]; extra: [string, number, number][]; changed: [string, string, number, number][]; weak: string[] }

export type TakeEdit = {
  trim_in?: number | null
  trim_out?: number | null
  cuts?: [number, number][]
  auto_cuts?: [number, number][]
  squeeze?: [number, number, number][]
  auto?: string[]
  nudge?: number
  rejected?: boolean
  deleted?: boolean
}

/** [duration, 'play' | 'hold', start in the video, end in the video (null on a hold), speed] */
export type PictureSpan = [number, 'play' | 'hold', number, number | null, number]
/** [duration, source ("__original__" or a session name, null = silent), start in the source] */
export type VoiceSpan = [number, string | null, number]
export type Tracks = { voice: VoiceSpan[]; picture: PictureSpan[] }

export type Take = {
  id: string
  session: string
  line: number
  t_in: number
  t_out: number
  rejected: boolean
  edit: TakeEdit
  raw_length: number
  length: number
  pauses: [number, number][]
  tighten: { pauses: number; start: number; end: number; gain: number }
  tracks: Tracks
  lead: number
  tail: number
  margin: number
  /** where "fit both" would put trim_in / trim_out */
  fit: [number, number]
  raw_picture: [number, number, 'play' | 'hold'][]
  words: { heard: [string, number, number][] } | null
  check: TakeCheck | null
}

/** [line, start, end, take id or null] in edit-list seconds */
export type LineSpan = [number, number, number, string | null]

export type Session = {
  build: string
  name: string
  created: number
  updated: number
  state: 'recording' | 'recorded' | 'processing' | 'ready' | 'failed'
  chunks: number
  seconds: number
  clean: string
  error: string
  stale: boolean
}

export type Job = { build: string; kind: string; key: string; state: string; error: string; updated: number; detail: string }

export type ExportFile = { name: string; url: string; size: number; time: number }

export type VersionRow = {
  n: number
  base: number | null
  texts: Record<string, string>
  state: 'queued' | 'voicing' | 'rendering' | 'ready' | 'failed' | 'merged' | 'stale'
  error: string
  created: number
  changed: number[]
  report: Record<string, { ok: boolean; listen: boolean }>
  video: string | null
  line_starts: Record<string, number>
}

export type Project = {
  build: string
  video: string
  video_version: number
  lines: LineRow[]
  sessions: Session[]
  audio: Record<string, string>
  /** recordings made with the cloned profile: the same recording before conversion (your voice, cleaned) */
  audio_alt?: Record<string, string>
  settings: { missing: 'original' | 'silent'; margin: string }
  voice: Record<string, VoiceMark>
  editable: boolean
  old_page: boolean
  engine: string
  voice_server: { up: boolean; pid: number | null; installed: boolean } | null
  takes: Record<string, Take[]>
  choices: Record<string, string>
  used: string[]
  edit_list: Tracks & { lines: LineSpan[] }
  jobs: Job[]
  scenes: string[]
  versions: Record<string, VersionRow[]>
  exports: ExportFile[]
}

export type Levels = { step: number; db: number[] }

export type LangState = 'approved' | 'draft' | 'needs_update' | 'empty'

export type EditorLangs = {
  lang: string
  lecture: string
  others: { lang: string; name: string; native: string; build: string | null; review: string; counts: Counts }[]
  lines: Record<
    string,
    { key: string; state: LangState; changed: Record<string, { old: string; new: string }>; others: { lang: string; text: string; state: LangState; review: string }[] }
  >
}

export type Counts = { approved: number; needs_update: number; draft: number; empty: number; total: number }

export type LanguageInfo = { code: string; name: string; native: string; script: string; rtl: boolean }

export type ReviewItem = {
  key: string
  section?: number
  where?: string
  text: string
  state: LangState
  changed: Record<string, { old: string; new: string }>
  refs: Record<string, string>
  checks: [string, string][]
}

export type Review = {
  lecture: string
  lang: string
  language: LanguageInfo
  primary: string
  exists: boolean
  languages: LanguageInfo[]
  have: string[]
  lines: ReviewItem[]
  sections: Record<string, string>
  counts: Counts
  labels: ReviewItem[]
  label_counts: Counts
}

export type LineInfo = { build: string; line: number; lines: number; text: string; starts: number[]; video: string; context: { before: Tracks; after: Tracks }; busy: boolean; pending: PendingTake[] }
/** a recording of this line that is not processed yet */
export type PendingTake = { id: string; session: string; state: string; error: string; seconds: number }

export type BuildPlan = {
  build: string
  can: boolean
  draft: boolean
  /** clean: all approved; draft: something is not (built with a draft tag); refused: Uzbek with something unapproved */
  approval: 'clean' | 'draft' | 'refused'
  problems: unknown[]
  reasons: string[]
  unapproved: { lines: number; labels: number; total: number }
  built: boolean
}
export type LangBuild = { build: string; built: boolean; when: number | null; prepared: boolean; stale: string[] | null; sessions: number; has_page: boolean }
export type BuildJob = { state: string; detail: string; error: string; updated: number }
export type LangSummary = {
  lang: string
  name: string
  native: string
  has_narration: boolean
  lines: Counts
  labels: Counts & { missing: number }
  builds: LangBuild[]
  ready: boolean
  missing: string[]
  plan: BuildPlan
  job: BuildJob | null
}
export type LectureLangs = { lecture: string; primary: string | null; langs: LangSummary[]; addable: { code: string; name: string; native: string }[] }
export type ActResult = { item: ReviewItem; counts: Counts; label_counts: Counts }

/** GET /api/lectures: the project browser's list (studio/review.py lecture_list) */
export type LangRow = {
  lang: string
  name: string
  native: string
  has_narration: boolean
  lines: Counts
  labels: Counts
  /** the built build's name, or null */
  build: string | null
  built_on: number | null
  sessions: number
  /** the name its build has, or will have (builds.py) */
  build_name: string
}
export type LectureRow = { stem: string; n: number; langs: LangRow[] }
export type SharedFile = { name: string; size: number; time: number; url: string }
export type ModuleRow = { k: number; title: string; files: SharedFile[]; lectures: LectureRow[] }
