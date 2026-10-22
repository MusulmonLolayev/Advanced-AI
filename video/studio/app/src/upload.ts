// The recording's upload queue, a port of presenter.py's page script: every piece is kept in the browser (IndexedDB,
// same database and keys as the old page, so either page can recover what the other left) until the server has it; sent
// in order, retried with a growing wait until it arrives. A 400 means refused: retrying will not help.
type Listener = () => void
const state = { waiting: 0, error: '', recording: false, inflight: new Set<string>() }
const listeners = new Set<Listener>()
const emit = () => listeners.forEach((f) => f())

export const uploads = {
  subscribe(f: Listener) {
    listeners.add(f)
    return () => void listeners.delete(f)
  },
  /** pieces not yet at the server */
  waiting: () => state.waiting,
  error: () => state.error,
  recording: () => state.recording,
  setRecording(r: boolean) {
    state.recording = r
    emit()
  },
  /** true while recording or while pieces are unsent: closing the page would lose something */
  unsaved: () => state.recording || state.waiting > 0,
  clearError() {
    state.error = ''
    emit()
  },
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

function idb(): Promise<IDBDatabase> {
  return new Promise((ok, no) => {
    const r = indexedDB.open('presenterChunks', 1)
    r.onupgradeneeded = () => r.result.createObjectStore('c')
    r.onsuccess = () => ok(r.result)
    r.onerror = () => no(r.error)
  })
}
async function idbDo<T>(mode: IDBTransactionMode, f: (s: IDBObjectStore) => IDBRequest<T> | void): Promise<T | null> {
  try {
    const d = await idb()
    return await new Promise<T | null>((ok, no) => {
      const tx = d.transaction('c', mode)
      const out = f(tx.objectStore('c'))
      tx.oncomplete = () => ok(out ? out.result : null)
      tx.onerror = () => no(tx.error)
    })
  } catch {
    return null
  }
}
const keep = (key: string, val: unknown) => idbDo('readwrite', (s) => void s.put(val, key))
const drop = (key: string) => idbDo('readwrite', (s) => void s.delete(key))

type Left = { build: string; name: string; seq?: number; blob?: Blob; events?: string }
async function pending(): Promise<[string, Left][]> {
  const d = await idb().catch(() => null)
  if (!d) return []
  return new Promise((ok) => {
    const out: [string, Left][] = []
    const cur = d.transaction('c', 'readonly').objectStore('c').openCursor()
    cur.onsuccess = () => {
      const c = cur.result
      if (c) {
        out.push([c.key as string, c.value as Left])
        c.continue()
      } else ok(out)
    }
    cur.onerror = () => ok(out)
  })
}

async function send(url: string, body: BodyInit) {
  for (let wait = 500; ; wait = Math.min(wait * 2, 8000)) {
    let r: Response | null = null
    try {
      r = await fetch(url, { method: 'POST', body })
    } catch {
      /* offline: wait and try again */
    }
    if (r && r.ok) return
    if (r && r.status === 400) throw new Error(await r.text())
    await sleep(wait)
  }
}

let sendQ: Promise<unknown> = Promise.resolve()
/** send `body` to `url` after everything queued before it; `key` is its IndexedDB slot */
function queue(key: string, url: string, body: BodyInit): Promise<unknown> {
  state.waiting++
  state.inflight.add(key)
  emit()
  sendQ = sendQ
    .then(() => send(url, body))
    .then(() => drop(key))
    .catch((e: Error) => {
      state.error = 'NOT saved: ' + e.message
    })
    .finally(() => {
      state.waiting--
      state.inflight.delete(key)
      emit()
    })
  return sendQ
}

const enc = encodeURIComponent
export function queueChunk(build: string, name: string, seq: number, blob: Blob) {
  const key = `${build}|${name}|${String(seq).padStart(6, '0')}`
  void keep(key, { build, name, seq, blob })
  return queue(key, `/api/chunk?build=${enc(build)}&name=${name}&seq=${seq}`, blob)
}
export function queueEvents(build: string, name: string, events: unknown[]) {
  const key = `${build}|${name}|events`
  const body = JSON.stringify(events)
  void keep(key, { build, name, events: body })
  return queue(key, `/api/events?build=${enc(build)}&name=${name}`, body)
}
export const queueFinish = (build: string, name: string) => queue(`${build}|${name}|finish`, `/api/finish?build=${enc(build)}&name=${name}`, '')
export const whenSent = () => sendQ

/** Pieces a closed tab never sent: send them now, then close that session. Returns the sessions it found. */
export async function recover(build: string): Promise<string[]> {
  const left = (await pending()).filter(([k, v]) => v.build === build && !state.inflight.has(k)).sort((a, b) => (a[0] < b[0] ? -1 : 1))
  const names = [...new Set(left.map(([, v]) => v.name))]
  for (const [key, val] of left) {
    if (val.blob) void queue(key, `/api/chunk?build=${enc(build)}&name=${val.name}&seq=${val.seq}`, val.blob)
    else void queue(key, `/api/events?build=${enc(build)}&name=${val.name}`, val.events ?? '[]')
  }
  for (const n of names) void queueFinish(build, n)
  if (names.length) await sendQ
  return names
}
