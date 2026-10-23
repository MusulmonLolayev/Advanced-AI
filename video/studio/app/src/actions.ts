// The Edit mode's actions. Each one posts, then fetches the project again; a failure shows the server's message in a
// toast and changes nothing (the old editor's api(): say("failed: …") and no refresh).
import { useMemo } from 'react'
import * as api from './api'
import { useToast } from './components'
import { useStudio } from './studio'

export function useActions() {
  const { build, reload, reloadLangs, reloadLec, stem, lang, langs } = useStudio()
  const lecture = langs?.lecture ?? stem
  const language = langs?.lang ?? lang
  const toast = useToast()
  return useMemo(() => {
    /** run `f`; on success refresh and (optionally) say what happened; null on failure */
    async function run<T>(f: () => Promise<T>, ok?: (r: T) => string): Promise<T | null> {
      try {
        const r = await f()
        await reload()
        if (ok) toast(ok(r))
        return r
      } catch (e) {
        toast(`Failed: ${(e as Error).message}`)
        return null
      }
    }
    return {
      edit: (take: string, changes: api.EditChanges) => run(() => api.postEdit(build, take, changes)),
      choose: (line: number, take: string) => run(() => api.postChoose(build, line, take)),
      fit: (take: string, end: 'both' | 'start' | 'end') => run(() => api.postFit(build, take, end)),
      unshrink: (take: string) => run(() => api.postUnshrink(build, take)),
      shrink: (take: string) => run(() => api.postShrink(build, take)),
      shrinkAll: () => run(() => api.postShrink(build), (r) => `Tightened: ${(r?.saved ?? 0).toFixed(1)} s saved across the lecture`),
      cutExtras: (take: string) => run(() => api.postCutExtras(build, take)),
      words: (take?: string) => run(() => api.postWords(build, take), () => (take ? 'Transcribing and checking the take' : 'Transcribing and checking the chosen takes')),
      version: (line: number, text?: string, base?: string) =>
        run(() => api.postVersion(build, line, text, base), (r) => `Queued: a new version of ${r.scene}`),
      merge: (scene: string, n: number) => run(() => api.postMerge(build, scene, n), () => `Merging v${n}`),
      discard: (scene: string, n: number) => run(() => api.postDiscard(build, scene, n)),
      setting: (key: string, value: string | number) => run(() => api.postSetting(build, key, value)),
      /** make the recording's voice again with a profile (a job); "cloned" needs the voice server */
      convertRecording: (name: string, clean = 'cloned') => run(() => api.postProcess(build, name, clean), () => `Converting ${name} to the cloned voice`),
      deleteRecording: (name: string) => run(() => api.postDelete(build, name), () => `Deleted ${name}`),
      voiceServer: (action: 'start' | 'stop') => run(() => api.postVoiceServer(build, action), () => (action === 'start' ? 'Starting the voice server: about a minute' : 'Stopping the voice server')),
      /** queue the lecture video in a language; the server refuses (with the reason) what cannot be built */
      buildLanguage: async (l: string) => {
        try {
          const r = await api.postBuildLanguage(stem, l)
          await reloadLec()
          toast(`Queued: ${r.build}`)
        } catch (e) {
          toast(`Cannot build: ${(e as Error).message}`)
        }
      },
      addLanguage: async (l: string) => {
        try {
          const r = await api.postAddLanguage(stem, l)
          await reloadLec()
          toast(`Created ${r.file}: every line is empty, to be drafted`)
          return true
        } catch (e) {
          toast(`Failed: ${(e as Error).message}`)
          return false
        }
      },
      exportNow: (clean: string) => run(() => api.postExport(build, clean), () => 'Export queued'),
      lineFine: async (key: string) => {
        try {
          await api.postLineFine(lecture, language, key)
          await reloadLangs()
        } catch (e) {
          toast(`Failed: ${(e as Error).message}`)
        }
      },
    }
  }, [build, reload, reloadLangs, reloadLec, stem, lecture, language, toast])
}
