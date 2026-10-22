// The app's shared state: which mode, lecture and language are open, the selected line, and the loaded project.
import { createContext, useContext } from 'react'
import type { EditorLangs, LectureLangs, Project } from './types'

export type Mode = 'record' | 'edit' | 'script' | 'export'

export type Studio = {
  mode: Mode
  setMode: (m: Mode) => void
  stem: string
  lang: string
  open: (stem: string, lang: string) => void
  build: string
  line: number
  setLine: (k: number) => void
  project: Project | null
  projectError: string | null
  projectLoading: boolean
  langs: EditorLangs | null
  /** fetch the project (or the languages) again and update the screen */
  reload: () => Promise<void>
  reloadLangs: () => Promise<void>
  /** the lecture's languages with counts, builds and build jobs (loaded in Script and Export) */
  lec: LectureLangs | null
  reloadLec: () => Promise<void>
  recording: boolean
  setRecording: (r: boolean) => void
  recSeconds: number
}

export const StudioCtx = createContext<Studio | null>(null)
export function useStudio(): Studio {
  const s = useContext(StudioCtx)
  if (!s) throw new Error('StudioCtx missing')
  return s
}
