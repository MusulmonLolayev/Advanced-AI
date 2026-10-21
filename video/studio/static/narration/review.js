// The narration review page: one language of one lecture, line by line (and label by label) against a reference language.
// Data from /api/narration; the buttons post to /api/narration/{approve,save,fine}, which answer with the item and the counts.
let R = null, tab = 'lines', filter = 'all', ref = '';
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const WORD = {approved: 'approved', needs_update: 'needs update', draft: 'draft', empty: 'empty'};
const FILTERS = [['all', 'all'], ['open', 'not approved'], ['needs_update', 'needs update'], ['empty', 'empty']];
const items = () => R[tab];
const kind = () => tab === 'lines' ? 'line' : 'label';
const counts = () => tab === 'lines' ? R.counts : R.label_counts;
function say(t){ const m = document.getElementById('msg'); m.textContent = t; m.style.display = 'block'; clearTimeout(say.t); say.t = setTimeout(() => m.style.display = 'none', 3000); }

function wordDiff(old, now){          // `now` with the words not in `old` marked, and the words it lost struck out
  const a = old.split(/\s+/).filter(Boolean), b = now.split(/\s+/).filter(Boolean);
  const L = Array.from({length: a.length + 1}, () => new Array(b.length + 1).fill(0));
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--)
    L[i][j] = a[i] === b[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
  let i = 0, j = 0; const out = [];
  while (i < a.length || j < b.length){
    if (i < a.length && j < b.length && a[i] === b[j]){ out.push(esc(b[j])); i++; j++; }
    else if (j < b.length && (i >= a.length || L[i][j + 1] >= L[i + 1][j])){ out.push('<mark>' + esc(b[j]) + '</mark>'); j++; }
    else { out.push('<del>' + esc(a[i]) + '</del>'); i++; } }
  return out.join(' '); }

const langInfo = code => R.languages.find(l => l.code === code) || {};
const nice = text => tab === 'labels' ? text.split('\n').join('  |  ') : text;

function shown(it){ return filter === 'all' ? true : filter === 'open' ? it.state !== 'approved' : it.state === filter; }
function count(c){ const parts = [`approved ${c.approved} / ${c.total}`];
  if (c.needs_update) parts.push(`${c.needs_update} need update`); if (c.draft) parts.push(`${c.draft} draft`); if (c.empty) parts.push(`${c.empty} empty`);
  return parts.join(' · '); }

function itemHtml(it){
  const id = (tab === 'lines' ? 'line-' : 'label-') + it.key, refText = it.refs[ref] || '';
  const changed = Object.entries(it.changed);
  const rtl = R.language.rtl ? ' dir="rtl"' : '';
  return `<div class="item ${it.state}" id="${esc(id)}" data-key="${esc(it.key)}">
    <div class="meta"><span class="key">${esc(it.key)}</span><span class="chip ${it.state}">${WORD[it.state]}${changed.length ? ': ' + changed.map(([l]) => esc(l) + ' changed').join(', ') : ''}</span>
      ${tab === 'labels' ? `<span class="dim">${esc(it.where)}</span>` : ''}</div>
    <div class="cols"><div><div class="reflang">${esc(ref || '—')}</div><div class="reftext"${langInfo(ref).rtl ? ' dir="rtl"' : ''}>${esc(nice(refText)) || '<span class="dim">no text in this language</span>'}</div></div>
      <div><textarea${rtl} data-saved="${esc(it.text)}" rows="${tab === 'labels' ? Math.max(2, it.text.split('\n').length) : Math.min(12, Math.max(3, Math.ceil(it.text.length / 62) + 1))}" oninput="typed(this)" placeholder="${tab === 'labels' ? 'one form per line, the default first' : 'not drafted yet'}">${esc(it.text)}</textarea>
        <div class="checks">${it.checks.map(([lv, m]) => `<span class="${lv}">${lv === 'warn' ? '⚠ ' : '· '}${esc(m)}</span>`).join('')}</div></div></div>
    ${changed.map(([l, x]) => `<div class="change"><b>${esc(l)} changed</b> <span class="dim">(the ${esc(l)} text when this was approved, and now)</span><br>${wordDiff(x.old, x.new)}</div>`).join('')}
    <div class="btns"><button data-do="approve" onclick="act(this, 'approve')" ${it.state === 'draft' ? '' : 'disabled'} title="the text as it is now is right">approve</button>
      <button data-do="save" onclick="act(this, 'save')" disabled title="write the edited text to the file and approve it">save edit</button>
      <button data-do="fine" class="quiet" onclick="act(this, 'fine')" ${it.state === 'needs_update' ? '' : 'disabled'} title="the other language changed, and this one is still right">still fine</button>
      <span class="err"></span></div></div>`; }

function render(){
  document.getElementById('tab-lines').className = tab === 'lines' ? 'on' : '';
  document.getElementById('tab-labels').className = tab === 'labels' ? 'on' : '';
  document.getElementById('tab-lines').textContent = `Narration (${R.counts.total})`;
  document.getElementById('tab-labels').textContent = `Labels (${R.label_counts.total})`;
  const c = counts();
  document.getElementById('counts').textContent = count(c);
  document.getElementById('filters').innerHTML = FILTERS.map(([f, name]) => {
    const n = f === 'all' ? c.total : f === 'open' ? c.total - c.approved : c[f];
    return `<button class="${filter === f ? 'on' : 'quiet'}" onclick="setFilter('${f}')">${name} ${n}</button>`; }).join('');
  const list = document.getElementById('list');
  if (!R.exists && tab === 'lines'){
    list.innerHTML = `<p>There is no ${esc(R.language.name)} narration for this lecture yet.</p>
      <p><button onclick="createSkeleton()">create the empty skeleton</button> <span class="dim">then ask Claude to draft ${esc(R.language.name)} for this lecture; you approve it here, line by line.</span></p>`;
    return; }
  let html = '', sec = null;
  for (const it of items()){
    if (!shown(it)) continue;
    if (tab === 'lines' && it.section !== sec){ sec = it.section; html += `<h2 class="sec">${esc(sec === 0 ? 'Opening' : R.sections[sec] || '')}</h2>`; }
    html += itemHtml(it); }
  list.innerHTML = html || '<p class="dim">nothing here with this filter</p>';
  const m = location.hash.match(/^#(line|label)=(.+)$/);
  if (m && !render.scrolled){ render.scrolled = true;
    const el = document.getElementById(m[1] + '-' + decodeURIComponent(m[2]));
    if (el){ el.classList.add('target'); el.scrollIntoView({block: 'center'}); } } }

function setTab(t){ tab = t; render(); }
function setFilter(f){ filter = f; render(); }
function typed(ta){ const row = ta.closest('.item'), dirty = ta.value !== ta.dataset.saved;
  ta.classList.toggle('dirty', dirty);
  const st = items().find(x => x.key === row.dataset.key).state;
  row.querySelector('[data-do=save]').disabled = !dirty;
  row.querySelector('[data-do=approve]').disabled = dirty || st !== 'draft';
  row.querySelector('[data-do=fine]').disabled = dirty || st !== 'needs_update'; }

async function act(btn, action){
  const row = btn.closest('.item'), key = row.dataset.key, k = kind();
  const url = `/api/narration/${action}?lecture=${LECTURE}&lang=${LANG}&kind=${k}&key=${encodeURIComponent(key)}`;
  const r = await fetch(url, {method: 'POST', body: action === 'save' ? JSON.stringify({text: row.querySelector('textarea').value}) : undefined});
  const o = await r.json().catch(() => ({error: 'the server did not answer'}));
  if (!r.ok){ row.querySelector('.err').textContent = o.error; return; }
  const list = items(), i = list.findIndex(x => x.key === key);
  list[i] = o.item; if (k === 'line') R.counts = o.counts; else R.label_counts = o.label_counts;
  row.outerHTML = itemHtml(o.item);                 // only this item is redrawn: what is typed elsewhere stays
  const c = counts(); document.getElementById('counts').textContent = count(c);
  say(action === 'save' ? 'saved and approved' : action === 'fine' ? 'confirmed' : 'approved');
  refreshFilters(); }
function refreshFilters(){ const c = counts();
  document.getElementById('filters').innerHTML = FILTERS.map(([f, name]) => {
    const n = f === 'all' ? c.total : f === 'open' ? c.total - c.approved : c[f];
    return `<button class="${filter === f ? 'on' : 'quiet'}" onclick="setFilter('${f}')">${name} ${n}</button>`; }).join(''); }
async function createSkeleton(){
  const r = await fetch(`/api/narration/add?lecture=${LECTURE}&lang=${LANG}`, {method: 'POST'});
  if (!r.ok){ say((await r.json().catch(() => ({}))).error || 'failed'); return; }
  await load(); }

function setRef(code){ ref = code; try { localStorage.setItem('reviewRef', code); } catch (e) {} render(); }
async function load(){
  const r = await fetch(`/api/narration?lecture=${LECTURE}&lang=${LANG}`);
  if (!r.ok){ document.getElementById('list').innerHTML = '<p class="bad">Cannot load: ' + r.status + '</p>'; return; }
  R = await r.json();
  const others = R.have.filter(l => l !== LANG);
  let want = R.primary !== LANG ? R.primary : others[0];
  try { const s = localStorage.getItem('reviewRef'); if (s && others.includes(s)) want = s; } catch (e) {}
  ref = others.includes(want) ? want : others[0] || '';
  document.getElementById('ref').innerHTML = others.map(l => `<option value="${l}"${l === ref ? ' selected' : ''}>${esc(langInfo(l).name)} · ${esc(langInfo(l).native)}</option>`).join('') || '<option value="">no other language</option>';
  document.getElementById('ref').onchange = e => setRef(e.target.value);
  document.getElementById('langs').innerHTML = R.languages.filter(l => R.have.includes(l.code) || l.code === LANG).map(l =>
    `<a class="btn${l.code === LANG ? ' on' : ''}" href="/narration?lecture=${LECTURE}&lang=${l.code}">${esc(l.native)}</a>`).join('');
  if (/^#label=/.test(location.hash)) tab = 'labels';
  render(); }
load();
