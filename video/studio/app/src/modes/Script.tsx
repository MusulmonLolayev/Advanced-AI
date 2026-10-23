import { Fragment, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { useActions } from '../actions'
import { fetchReview, postNarration } from '../api'
import { Button, Chip, Icon, Panel, Tabs, useToast, type ChipTone } from '../components'
import { useStudio } from '../studio'
import type { Counts, LangState, Review, ReviewItem } from '../types'
import { cls, useLive } from '../util'
import { EmptyState } from './EmptyState'
import { LanguageBuilds } from './LanguageBuilds'

const TONE: Record<LangState, ChipTone> = { approved: 'good', draft: 'warn', needs_update: 'accent', empty: 'empty' }
const WORD: Record<LangState, string> = { approved: 'approved', draft: 'draft', needs_update: 'needs update', empty: 'empty' }
type Filter = 'all' | 'needs_update' | 'draft' | 'empty' | 'approved'

function wordDiff(old: string, now: string): { t: string; k: 'same' | 'add' | 'del' }[] {
  const a = old.split(/\s+/).filter(Boolean)
  const b = now.split(/\s+/).filter(Boolean)
  const L = Array.from({ length: a.length + 1 }, () => new Array<number>(b.length + 1).fill(0))
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--) L[i][j] = a[i] === b[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1])
  const out: { t: string; k: 'same' | 'add' | 'del' }[] = []
  let i = 0
  let j = 0
  while (i < a.length || j < b.length) {
    if (i < a.length && j < b.length && a[i] === b[j]) (out.push({ t: b[j], k: 'same' }), i++, j++)
    else if (j < b.length && (i >= a.length || L[i][j + 1] >= L[i + 1][j])) (out.push({ t: b[j], k: 'add' }), j++)
    else (out.push({ t: a[i], k: 'del' }), i++)
  }
  return out
}

const countText = (c: Counts) => [`approved ${c.approved} / ${c.total}`, c.needs_update && `${c.needs_update} need update`, c.draft && `${c.draft} draft`, c.empty && `${c.empty} empty`].filter(Boolean).join(' · ')

const norm = (t: string) => t.replace(/\s+/g, ' ').trim()

/** A textarea as tall as its text (the whole text shows, the panel scrolls). */
function AutoText({ value, ...rest }: { value: string } & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const ref = useRef<HTMLTextAreaElement>(null)
  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight + 2}px`
  }, [value])
  return <textarea ref={ref} value={value} rows={2} {...rest} />
}

export function ScriptMode() {
  const { stem, lec, reloadLec } = useStudio()
  const toast = useToast()
  const act = useActions()
  const langCodes = useMemo(() => lec?.langs.map((l) => l.lang) ?? [], [lec])
  const names = useMemo(() => Object.fromEntries((lec?.langs ?? []).map((l) => [l.lang, l])), [lec])
  const reviews = useLive(langCodes.length ? () => Promise.all(langCodes.map((c) => fetchReview(stem, c))) : null, langCodes.length ? `${stem}|${langCodes.join(',')}` : '')
  const [tab, setTab] = useState<'lines' | 'labels'>('lines')
  const [filter, setFilter] = useState<Filter>('all')
  const [sel, setSel] = useState<{ key: string; lang: string } | null>(null)
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [errs, setErrs] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const [adding, setAdding] = useState<string | null>(null)
  const [rvW, setRvW] = useState<number>(() => {
    try {
      const n = Number(localStorage.getItem('studio.reviewWidth'))
      return n >= 320 && n <= 900 ? n : 460
    } catch {
      return 460
    }
  })
  const dragSplit = (e: React.PointerEvent<HTMLDivElement>) => {
    e.preventDefault()
    const box = (e.currentTarget.parentElement as HTMLElement).getBoundingClientRect()
    let w = rvW
    const move = (ev: PointerEvent) => {
      w = Math.round(Math.max(320, Math.min(900, box.right - ev.clientX, box.width - 320)))
      setRvW(w)
    }
    const up = () => {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
      try {
        localStorage.setItem('studio.reviewWidth', String(w))
      } catch {
        /* no storage: the width is kept for this visit only */
      }
    }
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
  }

  const byLang = useMemo(() => {
    const m: Record<string, Review> = {}
    reviews.data?.forEach((r) => (m[r.lang] = r))
    return m
  }, [reviews.data])
  // a language just added has no review until the fetch for it comes back: show the ones that have
  const codes = useMemo(() => langCodes.filter((c) => byLang[c]), [langCodes, byLang])
  const primary = lec?.primary ?? 'uz'
  const nameOf = (c: string) => names[c]?.name ?? c
  const items = (r: Review) => (tab === 'lines' ? r.lines : r.labels)
  const counts = (r: Review) => (tab === 'lines' ? r.counts : r.label_counts)

  useEffect(() => (setSel(null), setErrs({})), [stem, tab])
  useEffect(() => setErrs({}), [sel?.key])
  const first = byLang[codes[0]]
  const keys = first ? items(first).map((it) => it.key) : []
  const index = useMemo(() => {
    const m: Record<string, Record<string, ReviewItem>> = {}
    for (const c of codes) if (byLang[c]) m[c] = Object.fromEntries(items(byLang[c]).map((it) => [it.key, it]))
    return m
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [byLang, tab])

  if (!lec || reviews.loading) return <EmptyState title="Loading the review data…" />
  if (reviews.error || !first) return <EmptyState title="Cannot load the narration" tone="bad"><p className="dim">{reviews.error}</p></EmptyState>

  const shown = (key: string) => (filter === 'all' ? true : codes.some((c) => index[c]?.[key]?.state === filter))
  const sectionName = (it: ReviewItem) => (it.section === 0 ? 'Opening' : first.sections[String(it.section)] ?? '')
  let lastSec: number | undefined = -1
  const selIdx = sel ? keys.indexOf(sel.key) : -1
  const kind = tab === 'lines' ? 'line' : 'label'
  const rtl = (c: string) => (byLang[c]?.language.rtl ? 'rtl' : undefined)
  const idOf = (lang: string, key: string) => `${tab}|${lang}|${key}`
  const valueOf = (lang: string, key: string) => drafts[idOf(lang, key)] ?? index[lang]?.[key]?.text ?? ''
  // whitespace alone (a click that left a space or a newline) is not an edit: it must not lock approve / still fine
  const isDirty = (lang: string, key: string) => !!index[lang]?.[key] && norm(valueOf(lang, key)) !== norm(index[lang][key].text)
  const done = {
    approve: 'Approved', save: 'Saved and approved', fine: 'Confirmed: still fine',
  }

  /** One action on one language of the selected line; every block refreshes afterwards (one change can flag the others). */
  const post = async (lang: string, action: 'approve' | 'save' | 'fine', quiet = false) => {
    if (!sel) return
    const key = sel.key
    setErrs((e) => ({ ...e, [lang]: '' }))
    try {
      await postNarration(action, stem, lang, kind, key, action === 'save' ? valueOf(lang, key) : undefined)
      setDrafts((d) => Object.fromEntries(Object.entries(d).filter(([k]) => k !== idOf(lang, key))))
      if (!quiet) toast(`${nameOf(lang)}: ${done[action]}`)
      return true
    } catch (e) {
      setErrs((x) => ({ ...x, [lang]: (e as Error).message }))
      return false
    }
  }
  const run = async (lang: string, action: 'approve' | 'save' | 'fine') => {
    setBusy(true)
    try {
      await post(lang, action)
      await Promise.all([reviews.reload(), reloadLec()])
    } finally {
      setBusy(false)
    }
  }
  const approveAll = async () => {
    if (!sel) return
    setBusy(true)
    try {
      for (const c of codes) {
        const it = index[c]?.[sel.key]
        if (it && it.state === 'draft' && !isDirty(c, sel.key)) await post(c, 'approve', true)
      }
      toast('Approved every draft of this line')
      await Promise.all([reviews.reload(), reloadLec()])
    } finally {
      setBusy(false)
    }
  }
  const move = (d: number) => sel && keys[selIdx + d] && setSel({ ...sel, key: keys[selIdx + d] })
  const openDrafts = sel ? codes.filter((c) => index[c]?.[sel.key]?.state === 'draft' && !isDirty(c, sel.key)).length : 0
  const openAdd = adding !== null
  const uzPlan = names['uz'] ? names['uz'].plan.unapproved : null
  const uzLeft = uzPlan ? uzPlan.lines + uzPlan.labels : 0      // `total` counts every item, approved ones too

  return (
    <div className="script">
      <div className="script-bar">
        <Tabs
          label="Narration or labels"
          value={tab}
          onChange={setTab}
          tabs={[
            { id: 'lines', label: `Narration (${first.counts.total})` },
            { id: 'labels', label: `Labels (${first.label_counts.total})` },
          ]}
        />
        <Tabs
          pills
          label="Filter"
          value={filter}
          onChange={setFilter}
          tabs={[
            { id: 'all', label: 'all' },
            { id: 'needs_update', label: 'needs update' },
            { id: 'draft', label: 'draft' },
            { id: 'empty', label: 'empty' },
            { id: 'approved', label: 'approved' },
          ]}
        />
        <span className="grow" />
        <span className="legend">
          {(['approved', 'draft', 'needs_update', 'empty'] as LangState[]).map((s) => <Chip key={s} tone={TONE[s]}>{WORD[s]}</Chip>)}
        </span>
        {openAdd ? (
          <span className="field">
            <select aria-label="Language to add" value={adding ?? ''} onChange={(e) => setAdding(e.target.value)}>
              {lec.addable.map((l) => <option key={l.code} value={l.code}>{l.name} · {l.native}</option>)}
            </select>
            <Button small variant="primary" disabled={!adding} onClick={() => void act.addLanguage(adding!).then((ok) => ok && setAdding(null))}>create</Button>
            <Button small variant="ghost" onClick={() => setAdding(null)}>cancel</Button>
          </span>
        ) : (
          <Button small icon="plus" disabled={!lec.addable.length} onClick={() => setAdding(lec.addable[0]?.code ?? null)} title="write an empty narration skeleton for a new language, to be drafted by Claude">add language</Button>
        )}
      </div>
      {uzLeft > 0 && names['uz'] && (
        <div className="uz-rule" role="status">
          <Icon name="warn" size={14} /> <b>Uzbek is never voiced or built until it is approved.</b> {uzLeft} {uzLeft === 1 ? 'line or label is' : 'lines and labels are'} not approved yet. Approve them here (or save an edit, which approves it).
        </div>
      )}
      <details className="lang-strip" open>
        <summary>Languages and videos</summary>
        <LanguageBuilds compact />
      </details>

      <div className="script-split" style={{ ['--rv-w' as string]: `${rvW}px` }}>
        <Panel className="grid-panel" bodyClass="grid-body" title={<>{tab === 'lines' ? 'Lines' : 'Labels'} × languages</>} actions={<span className="mono dim">{stem}</span>}>
          <div className="mgrid" style={{ ['--ncols' as string]: codes.length }} role="grid">
            <div className="mg-head" role="row">
              <div className="mg-key">key</div>
              {codes.map((c) => (
                <div key={c} className="mg-lang" role="columnheader">
                  <b>{names[c]?.native ?? c}</b>
                  <small className="mono dim">{countText(counts(byLang[c]))}</small>
                </div>
              ))}
              <div className="mg-text">{nameOf(primary)} text</div>
            </div>
            {items(first).map((it0) => {
              if (!shown(it0.key)) return null
              const secChanged = tab === 'lines' && it0.section !== lastSec
              if (tab === 'lines') lastSec = it0.section
              return (
                <Fragment key={it0.key}>
                  {secChanged && <div className="mg-sec">{sectionName(it0)}</div>}
                  <div className={cls('mg-row', sel?.key === it0.key && 'sel')} role="row" data-key={it0.key}>
                    <div className="mg-key mono" onClick={() => setSel({ key: it0.key, lang: sel?.lang ?? primary })}>{it0.key}</div>
                    {codes.map((c) => {
                      const it = index[c]?.[it0.key]
                      const on = sel?.key === it0.key && sel.lang === c
                      return (
                        <button key={c} type="button" role="gridcell" data-lang={c} data-state={it?.state ?? 'empty'} className={cls('mg-cell', on && 'on')} aria-selected={on} onClick={() => setSel({ key: it0.key, lang: c })}>
                          <Chip tone={it ? TONE[it.state] : 'empty'}>{it ? WORD[it.state] : 'empty'}</Chip>
                          {it && it.checks.length > 0 && <Icon name="warn" size={12} style={{ color: 'var(--warn)' }} />}
                        </button>
                      )
                    })}
                    <div className="mg-text" title={it0.text} onClick={() => setSel({ key: it0.key, lang: sel?.lang ?? primary })}>{(index[primary]?.[it0.key] ?? it0).text.split('\n').join('  |  ')}</div>
                  </div>
                </Fragment>
              )
            })}
          </div>
        </Panel>

        <div className="split-handle" role="separator" aria-orientation="vertical" aria-label="Resize the review panel" data-testid="split" onPointerDown={dragSplit} />

        <Panel
          className="review-panel"
          title={sel ? <>Review · <span className="mono">{sel.key}</span>{tab === 'lines' && index[codes[0]]?.[sel.key] ? <> · {sectionName(index[codes[0]][sel.key])}</> : null}</> : 'Review'}
          actions={sel ? (
            <>
              <Button small variant="ghost" disabled={selIdx <= 0} onClick={() => move(-1)} title="Alt+↑">← prev</Button>
              <Button small variant="ghost" disabled={selIdx >= keys.length - 1} onClick={() => move(1)} title="Alt+↓">next →</Button>
              <Button small variant="primary" disabled={busy || openDrafts === 0} onClick={() => void approveAll()} title="approve every language that is a draft with no unsaved edit (needs-update ones need “still fine” or an edit)">approve all</Button>
            </>
          ) : undefined}
        >
          {!sel ? (
            <div className="empty-note pad">
              <p><b>Select a row</b> to review that line in every language, one under the other.</p>
              <p className="dim">Approve a draft, edit and save it (the save is the approval), or confirm “still fine” when another language changed. Ctrl+Enter saves or approves the block you are in; Alt+↓ / Alt+↑ move to the next / previous line.</p>
            </div>
          ) : (
            <div className="review" onKeyDown={(e) => { if (e.altKey && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) { e.preventDefault(); move(e.key === 'ArrowDown' ? 1 : -1) } }}>
              {codes.map((c) => {
                const it = index[c]?.[sel.key]
                if (!it) return null
                const value = valueOf(c, sel.key)
                const dirty = isDirty(c, sel.key)
                return (
                  <section key={c} className="rv-block" data-lang={c} data-state={it.state} aria-label={nameOf(c)}>
                    <div className="chips">
                      <b className="rv-h">{nameOf(c)}</b>
                      <span className="dim">{names[c]?.native}</span>
                      <Chip tone={TONE[it.state]}>{WORD[it.state]}</Chip>
                      {tab === 'labels' && it.where && <span className="dim">{it.where}</span>}
                    </div>
                    {c === 'uz' && it.state !== 'approved' && <div className="uz-rule" role="status"><Icon name="warn" size={14} /> Uzbek, not approved: it is not voiced or built until you approve it.</div>}
                    <AutoText
                      dir={rtl(c)}
                      className={dirty ? 'dirty' : ''}
                      value={value}
                      aria-label="text"
                      onChange={(e) => setDrafts((d) => ({ ...d, [idOf(c, sel.key)]: e.target.value }))}
                      onKeyDown={(e) => {
                        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                          e.preventDefault()
                          if (busy) return
                          if (dirty) void run(c, 'save')
                          else if (it.state === 'draft') void run(c, 'approve')
                        }
                      }}
                    />
                    {it.checks.length > 0 && (
                      <div className="checks">
                        {it.checks.map(([lv, m], i) => <div key={i} className={lv === 'warn' ? 'warn' : 'dim'}>{lv === 'warn' ? '⚠ ' : '· '}{m}</div>)}
                      </div>
                    )}
                    {Object.entries(it.changed).map(([l, x]) => (
                      <div key={l} className="change">
                        <b>{l} changed</b> <span className="dim">(the {l} text when this was approved, and now)</span>
                        <p>{wordDiff(x.old, x.new).map((w, i) => <Fragment key={i}>{w.k === 'add' ? <mark>{w.t}</mark> : w.k === 'del' ? <del>{w.t}</del> : w.t} </Fragment>)}</p>
                      </div>
                    ))}
                    <div className="btn-row">
                      <Button small variant="primary" disabled={busy || dirty || it.state !== 'draft'} onClick={() => void run(c, 'approve')} title="the text as it is now is right">approve</Button>
                      <Button small disabled={busy || !dirty} onClick={() => void run(c, 'save')} title="write the edited text to the narration file and approve it (Ctrl+Enter)">save edit</Button>
                      <Button small variant="ghost" disabled={busy || dirty || it.state !== 'needs_update'} onClick={() => void run(c, 'fine')} title={dirty ? 'you changed the text: save it, or undo the change first' : 'the other language changed, and this one is still right'}>still fine</Button>
                      {dirty && <Button small variant="ghost" disabled={busy} onClick={() => setDrafts((d) => Object.fromEntries(Object.entries(d).filter(([k]) => k !== idOf(c, sel.key))))} title="put back the text as it is in the narration">undo change</Button>}
                    </div>
                    {errs[c] && <p className="bad sub" role="alert">{errs[c]}</p>}
                  </section>
                )
              })}
              <p className="dim sub">Checks are shown inline and never block an approval: Cyrillic in a Latin-script text, Uzbek ʻ/ʼ, Latin words in a Cyrillic text, digits.</p>
            </div>
          )}
        </Panel>
      </div>
    </div>
  )
}
