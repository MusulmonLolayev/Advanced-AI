import { Fragment, useEffect, useMemo, useState } from 'react'
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

export function ScriptMode() {
  const { stem, lang: appLang, lec, reloadLec } = useStudio()
  const toast = useToast()
  const act = useActions()
  const langCodes = useMemo(() => lec?.langs.map((l) => l.lang) ?? [], [lec])
  const names = useMemo(() => Object.fromEntries((lec?.langs ?? []).map((l) => [l.lang, l])), [lec])
  const reviews = useLive(langCodes.length ? () => Promise.all(langCodes.map((c) => fetchReview(stem, c))) : null, langCodes.length ? `${stem}|${langCodes.join(',')}` : '')
  const [tab, setTab] = useState<'lines' | 'labels'>('lines')
  const [filter, setFilter] = useState<Filter>('all')
  const [sel, setSel] = useState<{ key: string; lang: string } | null>(null)
  const [refLang, setRefLang] = useState<string | null>(null)
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [adding, setAdding] = useState<string | null>(null)

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

  useEffect(() => (setSel(null), setErr('')), [stem, tab])
  useEffect(() => setErr(''), [sel])
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
  const cur = sel ? index[sel.lang]?.[sel.key] : null
  const ref = refLang && refLang !== sel?.lang ? refLang : sel && sel.lang !== primary ? primary : codes.find((c) => c !== (sel?.lang ?? appLang)) ?? primary
  const sectionName = (it: ReviewItem) => (it.section === 0 ? 'Opening' : first.sections[String(it.section)] ?? '')
  let lastSec: number | undefined = -1
  const selIdx = sel ? keys.indexOf(sel.key) : -1
  const id = sel ? `${tab}|${sel.lang}|${sel.key}` : ''
  const value = cur ? drafts[id] ?? cur.text : ''
  const dirty = !!cur && value !== cur.text
  const kind = tab === 'lines' ? 'line' : 'label'
  const uzOpen = sel?.lang === 'uz' && !!cur && cur.state !== 'approved'
  const rtl = (c: string) => (byLang[c]?.language.rtl ? 'rtl' : undefined)

  const run = async (action: 'approve' | 'save' | 'fine') => {
    if (!sel) return
    setBusy(true)
    setErr('')
    try {
      await postNarration(action, stem, sel.lang, kind, sel.key, action === 'save' ? value : undefined)
      setDrafts((d) => Object.fromEntries(Object.entries(d).filter(([k]) => k !== id)))
      await Promise.all([reviews.reload(), reloadLec()])
      toast(action === 'save' ? 'Saved and approved' : action === 'fine' ? 'Confirmed: still fine' : 'Approved')
    } catch (e) {
      setErr((e as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const openAdd = adding !== null
  const uzLeft = names['uz'] ? names['uz'].plan.unapproved.total : 0

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
          <Icon name="warn" size={14} /> <b>Uzbek is never voiced or built until it is approved.</b> {uzLeft} lines and labels are not approved yet. Approve them here (or save an edit, which approves it).
        </div>
      )}
      <details className="lang-strip" open>
        <summary>Languages and videos</summary>
        <LanguageBuilds compact />
      </details>

      <div className="script-split">
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
                    <div className="mg-key mono">{it0.key}</div>
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
                    <div className="mg-text" title={it0.text}>{(index[primary]?.[it0.key] ?? it0).text.split('\n').join('  |  ')}</div>
                  </div>
                </Fragment>
              )
            })}
          </div>
        </Panel>

        <Panel
          className="review-panel"
          title={sel && cur ? <>Review · <span className="mono">{sel.key}</span> · {nameOf(sel.lang)}</> : 'Review'}
          actions={sel ? (
            <>
              <Button small variant="ghost" disabled={selIdx <= 0} onClick={() => setSel({ ...sel, key: keys[selIdx - 1] })}>← prev</Button>
              <Button small variant="ghost" disabled={selIdx >= keys.length - 1} onClick={() => setSel({ ...sel, key: keys[selIdx + 1] })}>next →</Button>
            </>
          ) : undefined}
        >
          {!sel || !cur ? (
            <div className="empty-note pad">
              <p><b>Select a cell</b> to review that line in that language beside a reference language.</p>
              <p className="dim">Approve a draft, edit and save it (the save is the approval), or confirm “still fine” when another language changed.</p>
            </div>
          ) : (
            <div className="review">
              <div className="chips">
                <Chip tone={TONE[cur.state]}>{WORD[cur.state]}</Chip>
                {tab === 'labels' && cur.where && <span className="dim">{cur.where}</span>}
                <span className="grow" />
                <label className="field"><span className="label">reference</span>
                  <select value={ref} onChange={(e) => setRefLang(e.target.value)} aria-label="Reference language">
                    {codes.filter((c) => c !== sel.lang).map((c) => <option key={c} value={c}>{nameOf(c)} · {names[c]?.native}</option>)}
                  </select>
                </label>
              </div>
              {uzOpen && <div className="uz-rule" role="status"><Icon name="warn" size={14} /> Uzbek, not approved: it is not voiced or built until you approve it.</div>}
              <div className="rv-cols">
                <div>
                  <div className="label rv-h">{nameOf(ref)}</div>
                  <div className="rv-ref" dir={rtl(ref)}>{(cur.refs[ref] ?? index[ref]?.[sel.key]?.text ?? '').split('\n').join('  |  ') || <span className="dim">no text in this language</span>}</div>
                </div>
                <div>
                  <div className="label rv-h">{nameOf(sel.lang)} · edit</div>
                  <textarea key={id} dir={rtl(sel.lang)} className={dirty ? 'dirty' : ''} value={value} rows={tab === 'labels' ? 4 : 7} aria-label="text" onChange={(e) => setDrafts((d) => ({ ...d, [id]: e.target.value }))} />
                </div>
              </div>
              <div className="checks">
                {cur.checks.length === 0 ? <span className="good">· no checks to show</span> : cur.checks.map(([lv, m], i) => <div key={i} className={lv === 'warn' ? 'warn' : 'dim'}>{lv === 'warn' ? '⚠ ' : '· '}{m}</div>)}
              </div>
              {Object.entries(cur.changed).map(([l, x]) => (
                <div key={l} className="change">
                  <b>{l} changed</b> <span className="dim">(the {l} text when this was approved, and now)</span>
                  <p>{wordDiff(x.old, x.new).map((w, i) => <Fragment key={i}>{w.k === 'add' ? <mark>{w.t}</mark> : w.k === 'del' ? <del>{w.t}</del> : w.t} </Fragment>)}</p>
                </div>
              ))}
              <div className="btn-row">
                <Button variant="primary" disabled={busy || dirty || cur.state !== 'draft'} onClick={() => void run('approve')} title="the text as it is now is right">approve</Button>
                <Button disabled={busy || !dirty} onClick={() => void run('save')} title="write the edited text to the narration file and approve it">save edit</Button>
                <Button variant="ghost" disabled={busy || dirty || cur.state !== 'needs_update'} onClick={() => void run('fine')} title="the other language changed, and this one is still right">still fine</Button>
              </div>
              {err && <p className="bad sub" role="alert">{err}</p>}
              <p className="dim sub">Checks are shown inline and never block an approval: Cyrillic in a Latin-script text, Uzbek ʻ/ʼ, Latin words in a Cyrillic text, digits.</p>
            </div>
          )}
        </Panel>
      </div>
    </div>
  )
}
