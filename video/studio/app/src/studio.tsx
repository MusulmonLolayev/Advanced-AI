// The app's shared state: the lecture and language that are open, the selected line, the loaded project, whether the booth
// (Record) is on and which panel (Script & languages drawer, Export dialog) is open.
import { createContext, useContext } from 'react'
import type { EditorLangs, LectureLangs, ModuleRow, Project } from './types'

export type Panel = 'script' | 'export' | null

export type Studio = {
  /** Record is on: the monitor area is the booth. Turning it off while a recording runs asks first. */
  boothOn: boolean
  setBoothOn: (on: boolean, opts?: { take?: boolean }) => void
  /** the booth was opened with L: it records one take of the selected line as soon as it is up (read once) */
  takeOnOpen: { current: boolean }
  /** a line whose Rewrite… dialog the workspace should open (set by Export's "Open", read once) */
  rewriteLine: number | null
  setRewriteLine: (k: number | null) => void
  /** the Script & languages drawer, or the Export dialog */
  panel: Panel
  setPanel: (p: Panel) => void
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
  /** fetch the lecture's languages and the project browser's list again */
  reloadLec: () => Promise<void>
  /** every module, lecture and language (the project browser); null while loading */
  overview: ModuleRow[] | null
  /** Export: what is playing inline ("lecture", a recording's name, or an export file's URL), else '' */
  watch: string
  setWatch: (w: string) => void
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
