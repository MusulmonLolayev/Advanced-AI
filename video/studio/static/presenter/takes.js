// The presenter page's takes panel: every take of the line on screen, from every usable session, to watch (as it will
// appear in the video, or between the end of the line before and the start of the line after), choose, mark, delete and
// trim, and to record again with L. One request per line (/api/line); polled every 3 s while something is processing.
// Classic script, loaded after the page's own: it uses its globals (v, i, L, BUILD, rec, watching, stopAt, nxt, say, show),
// the editor's player.js (Player) and levels.js (LV, drawStrips). Without them (the offline copy) there is no panel.
(() => {
if (typeof Player === 'undefined' || typeof LV === 'undefined') return;
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const enc = encodeURIComponent, el = id => document.getElementById(id);
const root = document.createElement('div'), btn = document.createElement('button');
root.id = 'takes'; btn.id = 'tkbtn'; btn.textContent = 'takes (T)';
root.innerHTML = `<div class="tkhead"><b>Takes</b><span class="dim" id="tkline"></span>
  <button class="rec" data-act="record" title="record one take of this line (L)">● record a take</button>
  <button class="quiet" data-act="close" title="close (T)">✕</button></div><div id="tklist"></div>`;
const list = root.querySelector('#tklist'), tkline = root.querySelector('#tkline');
el('outer').appendChild(root); document.body.appendChild(btn);
let data = null, open = false, want = -1, timer = 0, watch = null, player = null, clockText = '';

// ─── the data ───
async function load(){
  clearTimeout(timer);
  if (!open || rec) return;
  const k = i;
  let d = null, why = '';
  try { const r = await fetch(`/api/line?build=${BUILD}&line=${k}`);
    if (r.ok) d = await r.json(); else why = 'HTTP ' + r.status + ' ' + ((await r.json().catch(() => ({}))).error || ''); }
  catch (e) { why = e.message; }
  if (k !== i) return;                                     // moved on to another line meanwhile
  if (!d){ list.innerHTML = `<p class="bad">Cannot load the takes of this line: ${esc(why)}</p>`; timer = setTimeout(load, 5000); return; }
  data = d; want = k; render();
  if (d.busy || d.pending.some(p => p.state !== 'failed')) timer = setTimeout(load, 3000); }
function sync(){                                           // called when the line on screen may have changed
  if (!open || rec) return;
  if (want === i && data) return;
  if (watch) endWatch(true);
  data = null; tkline.textContent = `line ${i + 1} / ${L.length}`; list.innerHTML = '<p class="dim">loading the takes…</p>'; load(); }
function setOpen(on){
  open = on; root.classList.toggle('open', on); btn.style.display = on ? 'none' : '';
  if (on){ want = -1; sync(); } else { endWatch(); clearTimeout(timer); } }
function toggle(){ if (rec){ say('The takes panel is closed while recording.'); return; } setOpen(!open); }
btn.addEventListener('click', () => { toggle(); btn.blur(); });

// ─── the page ───
const when = n => { const m = /^\d+-(\d+)-(\d+)T(\d+)-(\d+)/.exec(n); return m ? `${m[2]}.${m[1]} ${m[3]}:${m[4]}` : n; };
const secs = x => x.toFixed(1) + ' s';
function render(){
  if (LV.drag && !LV.drag.done) return;                    // a handle is being dragged: its canvas stays
  const d = data, keep = root.scrollTop, ts = d.takes;
  tkline.textContent = `line ${d.line + 1} / ${d.lines}`;
  const state = {recording: 'recording…', recorded: 'waiting…', processing: 'processing…', failed: 'failed'};
  const take = (t, n) => {
    const e = t.edit, used = t.id === d.chosen, w = watch && watch.id === t.id;
    const off = (a, b) => Math.abs(a - b) > 1e-3;
    return `<div class="tk${used ? ' used' : ''}${t.rejected ? ' bad' : ''}${w ? ' watching' : ''}" data-take="${esc(t.id)}">
  <div class="tkrow"><span class="tkname">T${n + 1}</span> <span class="tklen">${secs(t.length)}</span>
    <span class="dim mono" title="${esc(t.id)}">${esc(when(t.session))}${t.raw_length - t.length > 0.05 ? ' · recorded ' + secs(t.raw_length) : ''}</span>
    ${used ? '<span class="good" title="your recording is used for this line in the editor preview and in the export; the lecture video itself keeps the cloned or synthetic voice">used in your edit</span>' : ''}${t.rejected ? '<span class="bad">mistake</span>' : ''}</div>
  <div class="tkrow">${w && !watch.ctx ? '<button data-act="stop">■ stop</button>' : '<button data-act="watch" title="the take as it will appear in the video">▶ watch</button>'}
    ${w && watch.ctx ? '<button data-act="stop">■ stop</button>' : '<button data-act="ctx" title="the end of the line before, this take, the start of the line after">▶ in context</button>'}
    ${used ? '' : '<button data-act="use">use this one</button>'}
    <button class="quiet" data-act="mistake">${t.rejected ? 'not a mistake' : 'mistake'}</button>
    <button class="quiet" data-act="del" title="hide this take">delete</button><span class="tkclock">${w ? esc(clockText) : ''}</span></div>
  <div class="lvl"><canvas class="lvc" data-take="${esc(t.id)}" title="drag the two handles to trim the start and the end; click to play from there"></canvas>
    <div class="lvcap mono"><span></span><span></span></div></div>
  <div class="tkrow">
    <button data-act="fit-start" ${off(t.fit[0], e.trim_in || 0) ? '' : 'disabled'} title="keep ${t.margin} s before the first word">fit start</button>
    <button data-act="fit-end" ${off(t.fit[1], e.trim_out || 0) ? '' : 'disabled'} title="keep ${t.margin} s after the last word">fit end</button>
    <button data-act="fit-both" ${off(t.fit[0], e.trim_in || 0) || off(t.fit[1], e.trim_out || 0) ? '' : 'disabled'}>fit both</button>
    <button class="quiet" data-act="reset" ${e.trim_in || e.trim_out ? '' : 'disabled'}>reset ends</button></div></div>`; };
  const pend = p => `<div class="tk"><div class="tkrow"><span class="tkname">…</span>
    <span class="${p.state === 'failed' ? 'bad' : 'warn'}">${state[p.state] || esc(p.state)}${p.state === 'failed' ? ' ' + esc(p.error) : ''}</span>
    <span class="dim mono">${esc(when(p.session))} · ${secs(p.seconds)}</span></div></div>`;
  list.innerHTML = `<div class="tktext">${esc(d.text)}</div>
    <div class="tknote">${ts.length ? 'The video uses the take marked “used”: the one you pick, else the newest that is not a mistake. A new take becomes the used one unless you picked another.' : ''}</div>
    ${ts.map(take).join('') || (d.pending.length ? '' : '<p class="dim">No take of this line yet. Press L to record one.</p>')}
    ${d.pending.map(pend).join('')}`;
  root.scrollTop = keep; drawStrips(); }

// ─── watching: the page's own video, driven by the editor's two-track player ───
function glue(parts){                                      // tracks end to end; a shorter track is padded like the edit list
  const out = {voice: [], picture: []};
  for (const tr of parts){
    const v = tr.voice.slice(), p = tr.picture.slice(), gap = v.reduce((a, x) => a + x[0], 0) - p.reduce((a, x) => a + x[0], 0);
    if (gap > 1e-6){ const last = p[p.length - 1]; p.push([gap, 'hold', last ? (last[1] === 'play' ? last[3] : last[2]) : 0, null, 1]); }
    else if (gap < -1e-6) v.push([-gap, null, null]);
    out.voice.push(...v); out.picture.push(...p); }
  return out; }
const span = tr => tr.picture.reduce((a, x) => a + x[0], 0);
function startWatch(t, ctx, at = 0){
  if (rec){ say('Watching is not possible while recording.'); return; }
  if (!player) player = new Player(v, () => data ? data.audio : {}, {
    clock: (T, total) => { const c = watch && watch.cut;
      clockText = (c ? (T < c[0] ? 'end of the line before · ' : T < c[1] ? 'this take · ' : 'start of the line after · ') : '') + T.toFixed(1) + ' / ' + total.toFixed(1) + ' s';
      const e = list.querySelector('.tk.watching .tkclock'); if (e) e.textContent = clockText; },
    end: () => endWatch() });
  const c = data.context, before = span(c.before), mine = span(t.tracks);
  const tracks = ctx ? glue([c.before, t.tracks, c.after]) : t.tracks;
  watching = true; stopAt = null;                          // the page's own view logs nothing while a take plays
  watch = {id: t.id, ctx, cut: ctx ? [before, before + mine] : null};
  player.load(tracks, [[t.line, 0, span(tracks), t.id]], at);               // in context: from the end of the line before
  player.play(); render(); loop(); }
function loop(){ if (!watch) return; player.frame(); requestAnimationFrame(loop); }
function endWatch(quiet){                                  // quiet: the line is changing anyway
  if (!watch) return;
  player.pause(); watch = null; watching = false; clockText = '';
  v.playbackRate = v.defaultPlaybackRate; stopAt = null; v.currentTime = L[i][0]; v.pause(); nxt = i;
  if (!quiet){ if (data) render(); show(); } }
function key(e){                                           // while a take plays: Space pauses it, Esc ends it; the rest ends it
  if (e.key === ' '){ e.preventDefault(); player.toggle(); return true; }
  if (e.key === 'Escape'){ e.preventDefault(); endWatch(); return true; }
  if (['ArrowLeft', 'ArrowRight', 'PageUp', 'PageDown', 'l', 'L', 'r', 'R', 't', 'T'].includes(e.key)) endWatch();
  return false; }

// ─── the buttons ───
async function api(url, body){
  const r = await fetch(url + (url.includes('?') ? '&' : '?') + 'build=' + BUILD, {method: 'POST', body: body ? JSON.stringify(body) : undefined});
  if (!r.ok){ say('failed: ' + (await r.text()).replace(/<[^>]+>/g, ' ').trim().slice(0, 160)); return null; }
  await load(); return r; }
const edit = (id, ch) => api('/api/edit?take=' + enc(id), ch);
LV.host = {take: id => data && data.takes.find(t => t.id === id), edit, play: (t, at) => startWatch(t, false, at)};
root.addEventListener('click', async e => {
  const b = e.target.closest('button[data-act]'); if (!b) return;
  b.blur();
  const act = b.dataset.act, row = b.closest('[data-take]'), id = row && row.dataset.take;
  const t = id && data && data.takes.find(x => x.id === id);
  if (act === 'record') recordTake();
  else if (act === 'close') setOpen(false);
  else if (act === 'watch') startWatch(t, false);
  else if (act === 'ctx') startWatch(t, true);
  else if (act === 'stop') endWatch();
  else if (act === 'use') api(`/api/choose?line=${data.line}&take=${enc(id)}`);
  else if (act === 'mistake') edit(id, {rejected: !t.rejected});
  else if (act === 'del'){ if (confirm('Delete this take?')){ if (watch && watch.id === id) endWatch(); edit(id, {deleted: true}); } }
  else if (act.startsWith('fit-')) api(`/api/fit?take=${enc(id)}&end=${act.slice(4)}`);
  else if (act === 'reset') edit(id, {trim_in: null, trim_out: null}); });

window.Takes = {sync, toggle, key, stopWatch: () => endWatch(),
  recorded: one => { if (open) load(); else if (one) setOpen(true); }};     // a recording ended: look again (one take: open the panel)
window.addEventListener('resize', () => data && !rec && drawStrips());
if (/line=\d+/.test(location.hash)) setOpen(true);          // presenter.html#line=41 opens with the takes of line 41
})();
