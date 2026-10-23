// Typed fetchers (GET) and the editor's actions (POST), against today's routes. The POST helpers mirror the old editor's
// old editor's scripts (removed 2026-10-22): same route, same parameters, same body.
import type { ActResult, EditorLangs, Levels, LectureLangs, LineInfo, ModuleRow, Project, Review } from './types'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function getJSON<T>(url: string): Promise<T> {
  let r: Response
  try {
    r = await fetch(url)
  } catch (e) {
    throw new ApiError(0, `the server did not answer (${(e as Error).message})`)
  }
  if (!r.ok) {
    let why = ''
    try {
      const j = (await r.json()) as { error?: string; preparing?: string }
      why = (j.error ?? '') + (j.preparing ? ` (${j.preparing})` : '')
    } catch {
      /* not JSON */
    }
    throw new ApiError(r.status, `HTTP ${r.status}${why ? ': ' + why : ''}`)
  }
  return (await r.json()) as T
}

const q = encodeURIComponent
const cache = new Map<string, Promise<unknown>>()
const once = <T>(key: string, f: () => Promise<T>): Promise<T> => {
  if (!cache.has(key)) cache.set(key, f().catch((e) => (cache.delete(key), Promise.reject(e))))
  return cache.get(key) as Promise<T>
}

/** GET /api/project?build=… (lines, takes, edit list, voice marks, sessions, jobs, versions, exports). */
export const fetchProject = (build: string) => getJSON<Project>(`/api/project?build=${q(build)}`)
/** GET /api/levels?build=…&src=… (voice level of a session or "__original__", dB every 20 ms). Cached for the page's life (`version`: the video's, since the original voice follows it). */
export const fetchLevels = (build: string, src: string, version = 0) => once(`lv:${build}:${src}:${version}`, () => getJSON<Levels>(`/api/levels?build=${q(build)}&src=${q(src)}`))
/** GET /api/line?build=…&line=K (K from 0). */
export const fetchLine = (build: string, line: number) => getJSON<LineInfo>(`/api/line?build=${q(build)}&line=${line}`)
/** GET /api/editor-langs?build=… (the line in the lecture's other languages). */
export const fetchEditorLangs = (build: string) => getJSON<EditorLangs>(`/api/editor-langs?build=${q(build)}`)
/** GET /api/narration?lecture=…&lang=… (the review page's data: lines and labels with state, checks, reference texts). Not cached: approvals change it. */
export const fetchReview = (lecture: string, lang: string) => getJSON<Review>(`/api/narration?lecture=${q(lecture)}&lang=${q(lang)}`)
/** GET /api/lectures (every module with its lectures and their languages: counts and build state). */
export const fetchLectures = () => getJSON<{ modules: ModuleRow[] }>('/api/lectures').then((r) => r.modules)
/** GET /api/lecture-langs?lecture=… (the lecture page's language rows: counts, builds, can it be built and why not, the build job). */
export const fetchLectureLangs = (lecture: string) => getJSON<LectureLangs>(`/api/lecture-langs?lecture=${q(lecture)}`)
/** GET /api/counts?build=… (takes per line). */
export const fetchCounts = (build: string) => getJSON<Record<string, number>>(`/api/counts?build=${q(build)}`)

// ─── actions (POST). A failure throws an ApiError whose message is the server's, so the caller can toast it. ───

type Params = Record<string, string | number | undefined>

async function post<T = null>(path: string, params: Params, body?: unknown): Promise<T> {
  const qs = Object.entries(params)
    .filter(([, v]) => v !== undefined)
    .map(([k, v]) => `${k}=${q(String(v))}`)
    .join('&')
  let r: Response
  try {
    r = await fetch(`${path}?${qs}`, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) })
  } catch (e) {
    throw new ApiError(0, `the server did not answer (${(e as Error).message})`)
  }
  const text = await r.text()
  if (!r.ok) {
    let why = text
    try {
      why = (JSON.parse(text) as { error?: string }).error ?? text
    } catch {
      /* an HTML error page */
    }
    throw new ApiError(r.status, why.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 160) || `HTTP ${r.status}`)
  }
  try {
    return JSON.parse(text) as T
  } catch {
    return null as T
  }
}

export type EditChanges = Partial<{ trim_in: number | null; trim_out: number | null; cuts: [number, number][]; nudge: number; rejected: boolean; deleted: boolean }>

/** POST /api/edit?build&take, body = the changes (null clears a trim). Returns the saved edit. */
export const postEdit = (build: string, take: string, changes: EditChanges) => post<unknown>('/api/edit', { build, take }, changes)
/** POST /api/choose?build&line&take (line from 0): use this take for the line. */
export const postChoose = (build: string, line: number, take: string) => post('/api/choose', { build, line, take })
/** POST /api/fit?build&take&end=both|start|end */
export const postFit = (build: string, take: string, end: 'both' | 'start' | 'end') => post('/api/fit', { build, take, end })
export const postUnshrink = (build: string, take: string) => post('/api/unshrink', { build, take })
/** POST /api/shrink?build[&take]: one take, or every chosen take. Returns the seconds saved. */
export const postShrink = (build: string, take?: string) => post<{ saved: number }>('/api/shrink', { build, take })
export const postCutExtras = (build: string, take: string) => post('/api/cut-extras', { build, take })
/** POST /api/words?build[&take]: transcribe and check against the script (a job). No take = every chosen take. */
export const postWords = (build: string, take?: string) => post('/api/words', { build, take })
/** POST /api/version?build&line[&base]: a new cloned-voice version of the line's scene. No text = the same words again. */
export const postVersion = (build: string, line: number, text?: string, base?: string) =>
  post<{ scene: string; n: number }>('/api/version', { build, line, base }, text === undefined ? undefined : { text })
export const postMerge = (build: string, scene: string, n: number) => post('/api/version/merge', { build, scene, n })
export const postDiscard = (build: string, scene: string, n: number) => post('/api/version/discard', { build, scene, n })
/** POST /api/settings?build&key&value (margin, missing) */
export const postSetting = (build: string, key: string, value: string | number) => post('/api/settings', { build, key, value })
/** POST /api/process?build&name&clean=<profile>: clean the recording's voice again with a profile (a job); cloned = re-spoken in the cloned voice. */
export const postProcess = (build: string, name: string, clean: string) => post('/api/process', { build, name, clean })
/** POST /api/delete?build&name: forget a recording and its files. */
export const postDelete = (build: string, name: string) => post('/api/delete', { build, name })
export const postVoiceServer = (build: string, action: 'start' | 'stop') => post('/api/voice-server', { build, action })
/** POST /api/narration/fine?lecture&lang&kind=line&key: the line is still right against the other languages. */
export const postLineFine = (lecture: string, lang: string, key: string) => post('/api/narration/fine', { lecture, lang, kind: 'line', key })

/** POST /api/narration/{approve,save,fine}?lecture&lang&kind=line|label&key (save: body {text}). Returns the item and the counts. */
export const postNarration = (action: 'approve' | 'save' | 'fine', lecture: string, lang: string, kind: 'line' | 'label', key: string, text?: string) =>
  post<ActResult>(`/api/narration/${action}`, { lecture, lang, kind, key }, action === 'save' ? { text } : undefined)
/** POST /api/narration/add?lecture&lang: the empty skeleton of a new language. */
export const postAddLanguage = (lecture: string, lang: string) => post<{ file: string }>('/api/narration/add', { lecture, lang })
/** POST /api/narration/build?lecture&lang: queue the lecture video in this language. A refusal (Uzbek not approved...) throws with the reason. */
export const postBuildLanguage = (lecture: string, lang: string) => post<{ build: string }>('/api/narration/build', { lecture, lang })
/** POST /api/export?build&clean=<profile> */
export const postExport = (build: string, clean: string) => post('/api/export', { build, clean })
/** POST /api/prepare?build: write the presenter page (lines.json, the silent video) of a built lecture. */
export const postPrepare = (build: string) => post('/api/prepare', { build })
