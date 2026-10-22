// Snapshot of the module page (`/?m=K`) and the review API counts, copied from the live server on 2026-10-22.
// It lists the lectures in the project browser (there is no API for that yet); the open lecture's rows are live (`lec`).
export type LangRow = {
  code: string
  approved: number
  total: number
  labelsApproved: number
  labelsTotal: number
  build: string | null
  builtOn: string | null
  takes: number
  sessions: number
}
export type LectureRow = { module: number; stem: string; n: number; langs: LangRow[] }

export const MODULES: { k: number; name: string }[] = [
  { k: 0, name: 'Statistics for Advanced AI' },
  { k: 1, name: 'Classical Machine Learning' },
  { k: 2, name: 'Vision / Deep Neural Networks' },
  { k: 3, name: 'Natural Language Processing' },
  { k: 4, name: 'Graph Neural Networks' },
  { k: 5, name: 'Reinforcement Learning & Alignment' },
  { k: 6, name: 'Efficient AI & Deployment' },
  { k: 7, name: 'AI Agents, Tool Use & Retrieval' },
]

/** The module page's "Files" list (files linked into out/shared/mK/). */
export const FILES: Record<number, { name: string; info: string }[]> = {
  0: [],
  7: [{ name: 'Module7_Lecture01.pdf', info: '0.9 MB · 17 Oct' }],
}

export const LECTURES: LectureRow[] = [
  { module: 0, stem: 'lecture01', n: 1, langs: [
    { code: 'uz', approved: 212, total: 212, labelsApproved: 295, labelsTotal: 295, build: 'lecture01_uz_navoiy', builtOn: '21 Oct', takes: 1, sessions: 1 },
    { code: 'en', approved: 0, total: 212, labelsApproved: 0, labelsTotal: 295, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture02', n: 2, langs: [
    { code: 'uz', approved: 132, total: 132, labelsApproved: 183, labelsTotal: 183, build: 'lecture02_uz_navoiy', builtOn: '14 Oct', takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 132, labelsApproved: 0, labelsTotal: 183, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture03', n: 3, langs: [
    { code: 'uz', approved: 144, total: 144, labelsApproved: 162, labelsTotal: 162, build: 'lecture03_uz_navoiy', builtOn: '14 Oct', takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 144, labelsApproved: 0, labelsTotal: 162, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture04', n: 4, langs: [
    { code: 'uz', approved: 132, total: 132, labelsApproved: 170, labelsTotal: 170, build: 'lecture04_uz_navoiy', builtOn: '14 Oct', takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 132, labelsApproved: 0, labelsTotal: 170, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture05', n: 5, langs: [
    { code: 'uz', approved: 128, total: 128, labelsApproved: 194, labelsTotal: 194, build: 'lecture05_uz_navoiy', builtOn: '14 Oct', takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 128, labelsApproved: 0, labelsTotal: 194, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture06', n: 6, langs: [
    { code: 'uz', approved: 0, total: 137, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 137, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture07', n: 7, langs: [
    { code: 'uz', approved: 0, total: 132, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 132, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture08', n: 8, langs: [
    { code: 'uz', approved: 0, total: 121, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 121, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture09', n: 9, langs: [
    { code: 'uz', approved: 0, total: 134, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 134, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 0, stem: 'lecture10', n: 10, langs: [
    { code: 'uz', approved: 0, total: 148, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 148, labelsApproved: 0, labelsTotal: 1, build: null, builtOn: null, takes: 0, sessions: 0 } ] },
  { module: 7, stem: 'm7_lecture01', n: 1, langs: [
    { code: 'uz', approved: 0, total: 87, labelsApproved: 0, labelsTotal: 102, build: null, builtOn: null, takes: 0, sessions: 0 },
    { code: 'en', approved: 0, total: 90, labelsApproved: 0, labelsTotal: 102, build: 'm7_lecture01_en', builtOn: '19 Oct', takes: 0, sessions: 0 } ] }
]

/** The languages of languages.yaml (name, native name). */
export const LANGUAGES: Record<string, { name: string; native: string }> = {
  uz: { name: 'Uzbek', native: 'Oʻzbekcha' },
  en: { name: 'English', native: 'English' },
  ru: { name: 'Russian', native: 'Русский' },
  ko: { name: 'Korean', native: '한국어' },
  tr: { name: 'Turkish', native: 'Türkçe' },
  de: { name: 'German', native: 'Deutsch' },
  fr: { name: 'French', native: 'Français' },
  es: { name: 'Spanish', native: 'Español' },
  ar: { name: 'Arabic', native: 'العربية' },
  zh: { name: 'Chinese', native: '中文' },
}

export const buildName = (stem: string, lang: string): string => (lang === 'uz' ? `${stem}_uz_navoiy` : `${stem}_${lang}`)
export const lectureTitle = (r: { module: number; n: number }): string => `Lecture ${String(r.n).padStart(2, '0')}`
