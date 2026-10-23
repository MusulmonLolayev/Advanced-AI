import { useCallback, useEffect, useRef, useState } from 'react'

export const clamp = (x: number, a: number, b: number) => Math.min(b, Math.max(a, x))

/** 0:00.0 style timecode (h:mm:ss.t when over an hour). */
export function timecode(s: number, tenths = true): string {
  s = Math.max(0, s)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = Math.floor(s % 60)
  const t = Math.floor((s * 10) % 10)
  const mm = h ? String(m).padStart(2, '0') : String(m)
  return `${h ? h + ':' : ''}${mm}:${String(sec).padStart(2, '0')}${tenths ? '.' + t : ''}`
}

export const secs = (x: number, d = 1) => `${x.toFixed(d)} s`
export const mb = (b: number) => `${(b / 1e6).toFixed(1)} MB`

export type Async<T> = { data: T | null; error: string | null; loading: boolean }

/** Run a fetcher when `key` changes; the previous answer is dropped, a late answer for an old key is ignored. */
export function useAsync<T>(fn: (() => Promise<T>) | null, key: string): Async<T> {
  const [st, setSt] = useState<Async<T>>({ data: null, error: null, loading: !!fn })
  useEffect(() => {
    if (!fn) {
      setSt({ data: null, error: null, loading: false })
      return
    }
    let live = true
    setSt({ data: null, error: null, loading: true })
    fn().then(
      (data) => live && setSt({ data, error: null, loading: false }),
      (e: Error) => live && setSt({ data: null, error: e.message, loading: false }),
    )
    return () => {
      live = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])
  return st
}

export const cls = (...a: (string | false | null | undefined)[]) => a.filter(Boolean).join(' ')

/** Like useAsync, plus `reload()`: fetch again and keep the old answer on screen; an answer equal to the old one keeps its identity. */
export function useLive<T>(fn: (() => Promise<T>) | null, key: string): Async<T> & { reload: () => Promise<void> } {
  const [st, setSt] = useState<Async<T>>({ data: null, error: null, loading: !!fn })
  const fnRef = useRef(fn)
  const keyRef = useRef(key)
  fnRef.current = fn
  keyRef.current = key
  const reload = useCallback(async () => {
    const f = fnRef.current
    const k = keyRef.current
    if (!f) return
    try {
      const d = await f()
      if (keyRef.current !== k) return
      setSt((s) => ({ data: s.data && JSON.stringify(s.data) === JSON.stringify(d) ? s.data : d, error: null, loading: false }))
    } catch (e) {
      if (keyRef.current === k) setSt((s) => ({ ...s, error: (e as Error).message, loading: false }))
    }
  }, [])
  useEffect(() => {
    if (!fnRef.current) {
      setSt({ data: null, error: null, loading: false })
      return
    }
    setSt({ data: null, error: null, loading: true })
    void reload()
  }, [key, reload])
  return { ...st, reload }
}

/** The build a lecture has in a language, by builds.py's naming: Uzbek in the cloned voice, the others in edge-tts. */
export const buildName = (stem: string, lang: string): string => (lang === 'uz' ? `${stem}_uz_navoiy` : `${stem}_${lang}`)
export const lectureTitle = (n: number): string => `Lecture ${String(n).padStart(2, '0')}`
