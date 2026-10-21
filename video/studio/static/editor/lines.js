// The page: the side panel, one row per line (takes, trim, cuts, words) and the narration box.
function chosenId(k){ const sp = D.edit_list.lines.find(x => x[0] === k); return sp ? sp[3] : null; }
function render(){
  document.getElementById('sessions').innerHTML = D.sessions.map(s =>
    `<li><span class="mono">${esc(s.name)}</span> · ${s.stale ? '<span class="dim">earlier build of the video: not used</span>' :
      ({recording: '<span class="warn">recording…</span> ' + s.chunks + ' s', recorded: '<span class="warn">waiting</span>',
        processing: '<span class="warn">cleaning the voice…</span>', ready: (s.seconds / 60).toFixed(1) + ' min · ' + esc(s.clean),
        failed: '<span class="bad">failed</span> ' + esc(s.error)}[s.state] || esc(s.state))}</li>`).join('') || '<li class="dim">none yet: press ● Record</li>';
  document.getElementById('banner').innerHTML = D.old_page ? `<p style="margin:0 16px" class="warn">This lecture's presenter page was prepared before the editor:
    rewriting a line needs it prepared again. <button onclick="fetch('/api/prepare?build=' + BUILD, {method: 'POST'}).then(() => say('preparing: about a minute'))">prepare it again</button></p>` : '';
  const vs = D.voice_server;
  document.getElementById('vs').innerHTML = !vs ? '' : `<h2>Cloned voice</h2><p>${vs.up ? '<span class="good">server running</span>' : '<span class="dim">server off</span>'}
    ${vs.up ? (vs.pid ? `<button class="quiet" onclick="api('/api/voice-server?action=stop')">stop</button>` : '<span class="dim">(not started here)</span>')
            : `<button onclick="api('/api/voice-server?action=start'); say('starting: about a minute')">start</button>`}</p>
    <p class="dim">Re-voicing starts it when needed. It uses the GPU while it runs.</p>`;
  document.getElementById('jobs').innerHTML = D.jobs.slice(-6).reverse().map(j =>
    `<li>${esc(j.kind)} <span class="dim">${esc(j.key).slice(0, 40)}</span> · <span class="${j.state === 'failed' ? 'bad' : j.state === 'done' ? 'good' : 'warn'}">${esc(j.state)}</span> ${esc(j.error || j.detail || '')}</li>`).join('') || '<li class="dim">none</li>';
  document.getElementById('exports').innerHTML = D.exports.map(f =>
    `<li><a href="${f.url}" ${f.name.endsWith('.mp4') ? 'target="_blank"' : 'download'}>${esc(f.name)}</a> <span class="dim">${(f.size / 1e6).toFixed(1)} MB</span></li>`).join('') || '<li class="dim">none yet</li>';
  const scroll = window.scrollY, focus = document.activeElement, drafts = {};
  document.querySelectorAll('#lines textarea').forEach(t => { drafts[t.id] = [t.value, t === focus, t.selectionStart, t.selectionEnd]; });
  if (LV.drag && !LV.drag.done) return;                // a handle is being dragged: its canvas stays
  document.getElementById('lines').innerHTML = D.lines.map((l, k) => rowHtml(k, l)).join('');
  for (const [id, [val, had, a, b]] of Object.entries(drafts)){     // a refresh keeps what is being typed
    const t = document.getElementById(id); if (!t) continue;
    t.value = val; if (had){ t.focus(); t.setSelectionRange(a, b); } }
  window.scrollTo(0, scroll); showNow(); syncHeader(); drawStrips(); drawLecture(); }

function rowHtml(k, l){
  const takes = D.takes[k] || [], cid = chosenId(k), s = sel[k] || cid || (takes[takes.length - 1] || {}).id;
  const t = takes.find(x => x.id === s), ct = takes.find(x => x.id === cid);
  const ck = ct && ct.check, odd = ck ? ck.extra.length + ck.changed.length + ck.weak.length : 0;
  const flag = !ck ? '' : ck.missing.length ? `<span class="bad" title="not heard: ${esc(ck.missing.join(' '))}">${ck.missing.length} missed</span>`
    : odd ? `<span class="warn" title="extra, heard differently or unclear words: open the line">${odd} to check</span>` : '<span class="good">script ✓</span>';
  const chips = takes.map((x, n) => `<span class="chip${x.id === cid ? ' chosen' : ''}${x.rejected ? ' rejected' : ''}${open.has(k) && x.id === s ? ' sel' : ''}"
      onclick="event.stopPropagation(); pick(${k}, '${x.id}')" title="${esc(x.id)} · ${x.length.toFixed(1)} s${x.rejected ? ' · marked a mistake' : ''}">T${n + 1}</span>`).join('');
  const li = langInfo(k), lflag = li && li.state === 'needs_update' ? langChip(li.state) : '';
  const vm = D.voice[k], vflag = !vm ? '' : !vm.ok ? `<span class="bad" title="the voice check heard: ${esc(vm.heard)}">voice: ${esc(vm.fails.join(', '))}</span>`
    : vm.listen ? '<span class="warn" title="the voice check put this line on the listen list">listen</span>' : '';
  return `<div class="row${open.has(k) ? ' open' : ''}${k === curLine ? ' cur' : ''}" id="row${k}">
  <div class="head" onclick="toggleRow(${k})"><span class="num">${k + 1}</span><span class="text">${esc(l[1])}</span>
   <span class="side">${vdot(k)} ${lflag} ${vflag} ${flag} ${chips || `<span class="dim">${D.settings.missing === 'original' ? 'original voice' : 'no take'}</span>`} <span class="dim mono">${ct ? ct.length.toFixed(1) + ' s' : ''}</span>
    <button class="quiet" onclick="event.stopPropagation(); playLine(${k})" title="preview from here">▶</button>
    <a class="btn" href="/${BUILD}/presenter/presenter.html#line=${k + 1}" target="_blank" onclick="event.stopPropagation()" title="record this line again">●</a></span></div>
  ${langBanner(k)}
  <div class="detail">${t ? detailHtml(k, t, cid) : '<p class="dim">No take of this line yet. Press ● to record it: the presenter opens at this line.</p>'}${narrHtml(k)}${langBox(k)}</div></div>`; }


function detailHtml(k, t, cid){
  const e = t.edit, cuts = (e.cuts || []), auto = (e.auto_cuts || []), sqz = (e.squeeze || []), tg = t.tighten;
  const tools = auto.length || sqz.length || (e.auto || []).length;
  const inCut = (a, b) => cuts.concat(auto).some(([x, y]) => a >= x - 1e-3 && b <= y + 1e-3);
  let words = '';
  if (t.words){
    const extra = new Set((t.check ? t.check.extra : []).map(x => x[1].toFixed(3)));
    const changed = (t.check ? t.check.changed : []);
    const isChanged = a => changed.some(c => a >= c[2] - 1e-3 && a <= c[3] + 1e-3);
    const pauses = t.pauses.filter(p => p[1] - p[0] >= 0.8);
    let pi = 0;
    words = '<div class="words">' + t.words.heard.map(([w, a, b]) => {
      let pre = ''; while (pi < pauses.length && pauses[pi][0] <= a){ pre += `<span class="pause">⏸${(pauses[pi][1] - pauses[pi][0]).toFixed(1)}s</span>`; pi++; }
      return pre + `<span class="w${extra.has((+a).toFixed(3)) ? ' extra' : isChanged(a) ? ' changed' : ''}${inCut(a, b) ? ' cut' : ''}" title="${a.toFixed(2)}–${b.toFixed(2)} s · click to cut or keep"
        onclick="cutWord('${t.id}', ${a}, ${b})">${esc(w)}</span>`; }).join(' ') + '</div>';
    if (t.check && t.check.missing.length) words += `<p class="bad">Not heard: ${esc(t.check.missing.join(' · '))}</p>`;
    if (changed.length) words += `<p class="warn">Heard differently (the recogniser may be wrong; listen): ${changed.map(c => esc(c[0]) + ' → ' + esc(c[1])).join(' · ')}</p>`;
    if (t.check && t.check.weak.length) words += `<p class="warn">Unclear: ${esc(t.check.weak.join(' · '))}</p>`;
  }
  const job = D.jobs.find(j => j.kind === 'words' && (j.state === 'queued' || j.state === 'running'));
  const hand = k => e[k] && !(e.auto || []).includes(k);      // a trim set by hand, not by the tightening tool
  return `<div class="lvl"><canvas class="lvc" data-take="${t.id}" title="drag the two handles to trim the start and the end; click to play from there"></canvas>
    <div class="lvcap mono"><span></span><span></span></div></div>
  <div class="ctl"><label>line ends (margin ${t.margin} s)</label>
    <button onclick="api('/api/fit?take=${encodeURIComponent(t.id)}&end=start')" ${Math.abs(t.fit[0] - (e.trim_in || 0)) > 1e-3 ? '' : 'disabled'} title="trim the start so ${t.margin} s of silence stays before the first word (${t.fit[0].toFixed(2)} s)">fit start</button>
    <button onclick="api('/api/fit?take=${encodeURIComponent(t.id)}&end=end')" ${Math.abs(t.fit[1] - (e.trim_out || 0)) > 1e-3 ? '' : 'disabled'} title="trim the end so ${t.margin} s of silence stays after the last word (${t.fit[1].toFixed(2)} s)">fit end</button>
    <button onclick="api('/api/fit?take=${encodeURIComponent(t.id)}&end=both')" ${Math.abs(t.fit[0] - (e.trim_in || 0)) > 1e-3 || Math.abs(t.fit[1] - (e.trim_out || 0)) > 1e-3 ? '' : 'disabled'}>fit both</button>
    <button class="quiet" onclick="edit('${t.id}', {trim_in: null, trim_out: null})" ${e.trim_in || e.trim_out ? '' : 'disabled'} title="put both ends back to the recording's own">reset ends</button>
    <span class="dim">start ${(e.trim_in || 0).toFixed(2)} s${hand('trim_in') ? ' (by hand)' : ''} · end ${(e.trim_out || 0).toFixed(2)} s${hand('trim_out') ? ' (by hand)' : ''}</span></div>
  <div class="ctl">
    <button onclick="playTake(D.takes[${k}].find(x => x.id === '${t.id}'))">▶ play this take</button>
    ${t.id === cid ? '<span class="good" title="your recording is used for this line in the editor preview and in the export; the lecture video itself keeps the cloned or synthetic voice">used in your edit</span>' : `<button onclick="api('/api/choose?line=${k}&take=${encodeURIComponent(t.id)}')" title="use this recording for the line in your edit (preview and export)">use this take</button>`}
    <button class="quiet" onclick="edit('${t.id}', {rejected: ${!t.rejected}})">${t.rejected ? 'not a mistake' : 'mark as a mistake'}</button>
    <button class="quiet" onclick="if (confirm('Hide this take?')) edit('${t.id}', {deleted: true})">hide</button>
    <span class="dim mono">${esc(t.id)} · ${t.raw_length.toFixed(1)} s recorded → ${t.length.toFixed(1)} s</span></div>
  <div class="ctl">
    <label>picture later / sooner than the voice</label>
    <input type="range" min="-2" max="2" step="0.05" value="${e.nudge || 0}" oninput="this.nextElementSibling.value=this.value" onchange="edit('${t.id}', {nudge: +this.value})">
    <input type="number" step="0.05" value="${e.nudge || 0}" onchange="edit('${t.id}', {nudge: +this.value})"> s</div>
  <div class="ctl"><label>cuts</label>${cuts.map(([a, b], n) => `<span class="chip" onclick="dropCut('${t.id}', ${n})" title="click to remove">${a.toFixed(2)}–${b.toFixed(2)} s ✕</span>`).join(' ') || '<span class="dim">none</span>'}
    ${auto.length || sqz.length ? `<span class="dim" title="made by tightening">+ tightened: ${auto.reduce((a, [x, y]) => a + y - x, 0).toFixed(1)} s of pauses cut${sqz.length ? ', ' + sqz.reduce((a, [x, y, n]) => a + y - x - n, 0).toFixed(1) + ' s squeezed' : ''}</span>` : ''}
    <button onclick="api('/api/shrink?take=${encodeURIComponent(t.id)}')" ${tg.gain > 0 ? '' : 'disabled'} title="shorten the pauses inside the take, and trim the ends to keep ${t.margin} s around the voice (a trim you set by hand stays)">${tightenLabel(tg)}</button>
    ${tools ? `<button class="quiet" onclick="api('/api/unshrink?take=${encodeURIComponent(t.id)}')" title="takes back the pause cuts and the trims the tool set; your own cuts, hand-set trims and nudge stay">undo tightening</button>` : ''}
    ${cuts.length ? `<button class="quiet" onclick="edit('${t.id}', {cuts: []})">clear cuts</button>` : ''}</div>
  <div class="ctl">${t.words ? `<button onclick="api('/api/cut-extras?take=${encodeURIComponent(t.id)}')" ${t.check && t.check.extra.length ? '' : 'disabled'}>cut the ${t.check ? t.check.extra.length : 0} extra word${t.check && t.check.extra.length === 1 ? '' : 's'}</button>` : ''}
    <button class="quiet" onclick="api('/api/words?take=${encodeURIComponent(t.id)}')" ${job ? 'disabled' : ''}>${t.words ? 'transcribe again' : 'transcribe and check against the script'}</button></div>
  ${words}`; }

function tightenLabel(tg){
  if (tg.gain <= 0) return 'tightened: nothing more to gain';
  const parts = []; if (tg.pauses) parts.push(tg.pauses + ' pause' + (tg.pauses === 1 ? '' : 's'));
  if (tg.start) parts.push('start ' + tg.start.toFixed(1) + ' s'); if (tg.end) parts.push('end ' + tg.end.toFixed(1) + ' s');
  return 'tighten: ' + (parts.join(', ') || tg.gain.toFixed(1) + ' s'); }
function syncHeader(){        // the header's two settings follow the server (the margin) and the browser (the long-silence length)
  const m = document.getElementById('margin'), l = document.getElementById('longsil');
  if (m && document.activeElement !== m) m.value = D.settings.margin;
  if (l && document.activeElement !== l) l.value = longSilence(); }
async function tightenAll(){ const r = await api('/api/shrink'); if (r){ const o = await r.json().catch(() => null); if (o) say('tightened: ' + o.saved.toFixed(1) + ' s saved across the lecture'); } }
function toggleRow(k){ open.has(k) ? open.delete(k) : open.add(k); render(); }
function pick(k, id){ sel[k] = id; open.add(k); render(); }
function edit(id, changes){ return api('/api/edit?take=' + encodeURIComponent(id), changes); }
function takeById(id){ return Object.values(D.takes).flat().find(t => t.id === id); }
function dropCut(id, n){ const c = (takeById(id).edit.cuts || []).slice(); c.splice(n, 1); edit(id, {cuts: c}); }
function cutWord(id, a, b){
  const t = takeById(id), cuts = (t.edit.cuts || []).map(x => x.slice());
  const hit = cuts.findIndex(([x, y]) => a >= x - 1e-3 && b <= y + 1e-3);
  if (hit >= 0) cuts.splice(hit, 1); else cuts.push([Math.max(0, a - 0.03), b + 0.03]);
  edit(id, {cuts}); }

// Languages: the same line in the lecture's other languages (status, text, a link to its review page), and the banner
// of a line another language changed under (studio/review.py editor_langs; the review page is /narration).
let LANGS = null;
const STATE_WORD = {approved: 'approved', needs_update: 'needs update', draft: 'draft', empty: 'empty'};
async function loadLangs(){
  try { const r = await fetch('/api/editor-langs?build=' + BUILD); if (r.ok){ LANGS = await r.json(); if (D) render(); } } catch (e) {} }
const langInfo = k => LANGS && LANGS.lines[k];
const langChip = (state, more = '') => `<span class="lchip ${state}">${STATE_WORD[state]}${more}</span>`;
function langBanner(k){
  const i = langInfo(k); if (!i || i.state !== 'needs_update') return '';
  return `<div class="lbanner"><b>needs update</b> ${Object.entries(i.changed).map(([l, x]) =>
      `<span class="dim">${esc(l)} changed:</span> <span class="vdiff">${wordDiff(x.old, x.new)}</span>`).join(' ')}
    <button onclick="event.stopPropagation(); stillFine('${esc(i.key)}')" title="this line is still right: approve it again against the other languages as they are now">still fine</button>
    <a class="btn" href="/narration?lecture=${LANGS.lecture}&lang=${LANGS.lang}#line=${encodeURIComponent(i.key)}" target="_blank" onclick="event.stopPropagation()">edit in the review</a></div>`; }
function langBox(k){
  const i = langInfo(k); if (!i || !i.others.length) return '';
  return `<div class="narr langbox"><div class="dim">Other languages</div>${i.others.map(o =>
    `<div class="lrow"><b>${esc(o.lang)}</b> ${langChip(o.state)} <a href="${o.review}" target="_blank">review</a><div>${esc(o.text)}</div></div>`).join('')}</div>`; }
async function stillFine(key){
  const r = await fetch(`/api/narration/fine?lecture=${LANGS.lecture}&lang=${LANGS.lang}&kind=line&key=${encodeURIComponent(key)}`, {method: 'POST'});
  if (!r.ok) say('failed: ' + ((await r.json().catch(() => ({}))).error || r.status));
  await loadLangs(); }
document.addEventListener('visibilitychange', () => { if (!document.hidden) loadLangs(); });
