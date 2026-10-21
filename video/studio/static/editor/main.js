// Shared state and helpers, the server calls (api, refresh, poll), keys, layout and size switch. Loaded last.
const v = document.getElementById('v');
let D = null, open = new Set(), sel = {}, curLine = 0;
const fmt = s => { s = Math.max(0, s); const m = Math.floor(s / 60); return m + ':' + String(Math.floor(s % 60)).padStart(2, '0'); };
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
function say(t){ const m = document.getElementById('msg'); m.textContent = t; m.style.display = 'block'; clearTimeout(say.t); say.t = setTimeout(() => m.style.display = 'none', 2500); }

// the editor's player, and what it shows of itself: the transport, the timeline cursor, the line on view
const P = new Player(v, () => D.audio, {
  state: playing => { document.getElementById('pp').textContent = playing ? '⏸' : '▶'; },
  clock: (T, total) => { document.getElementById('clock').textContent = fmt(T) + ' / ' + fmt(total); setCursor(total ? 100 * T / total : 0); },
  line: k => { if (k !== curLine){ curLine = k; showNow(); } } });
function setCursor(pct){        // the timeline's cursor and the level strip's under it (that strip shows the whole lecture only)
  document.getElementById('cursor').style.left = pct + '%';
  const l = document.getElementById('lcursor');
  if (l){ l.style.left = pct + '%'; l.style.display = P.off || document.getElementById('mode').textContent !== 'whole lecture' ? 'none' : 'block'; } }

function showNow(){
  if (P.off) return;
  document.getElementById('nowline').textContent = D && D.lines[curLine] ? (curLine + 1) + '. ' + D.lines[curLine][1] : '';
  document.querySelectorAll('.row.cur').forEach(r => r.classList.remove('cur'));
  const r = document.getElementById('row' + curLine); r?.classList.add('cur');
  if (r && P.playing && Date.now() - handScroll > 4000) r.scrollIntoView({block: 'nearest'}); }

function loadAll(at){
  if (P.off) leaveVersion();
  const el = D.edit_list; P.load(el, el.lines, at || 0);
  document.getElementById('mode').textContent = 'whole lecture';
  const tl = document.getElementById('tl'); tl.querySelectorAll('.seg').forEach(x => x.remove());
  const flagged = new Set(Object.values(D.takes).flat().filter(t => t.check && (t.check.missing.length || t.check.extra.length)).map(t => t.id));
  for (const [k, a, b, tid] of el.lines){
    const vm = D.voice[k], orig = !tid && D.settings.missing === 'original';
    const s = document.createElement('div');
    s.className = 'seg' + (tid ? (flagged.has(tid) ? ' flag' : '') : orig ? ' orig' : ' missing') +
      (orig && vm ? (!vm.ok ? ' vbad' : vm.listen ? ' vlisten' : '') : '');
    s.style.left = 100 * a / P.total + '%'; s.style.width = Math.max(0.1, 100 * (b - a) / P.total - 0.05) + '%';
    s.title = (k + 1) + '. ' + D.lines[k][1].slice(0, 80) + (tid ? '' : orig ? ' — original voice' : ' — no take yet, silent') +
      (vm && !vm.ok ? ' — voice check: ' + vm.fails.join(', ') : ''); tl.insertBefore(s, tl.firstChild); }
}
function lineStart(k){ const sp = D.edit_list.lines.find(x => x[0] === k); return sp ? sp[1] : 0; }
function playLine(k){ if (document.getElementById('mode').textContent !== 'whole lecture') loadAll(); P.seek(lineStart(k)); P.play(); }
function playTake(t, at = 0){ if (P.off) leaveVersion(); P.load(t.tracks, [[t.line, 0, t.length, t.id]], at); document.getElementById('mode').textContent = 'take ' + t.id; P.play(); }
document.getElementById('tl').addEventListener('click', e => {
  const r = e.currentTarget.getBoundingClientRect(); P.seek(P.total * (e.clientX - r.left) / r.width); });

(function loop(){ P.frame(); requestAnimationFrame(loop); })();
let handScroll = 0;
['wheel', 'touchmove', 'mousedown'].forEach(n => document.getElementById('right').addEventListener(n, () => handScroll = Date.now(), {passive: true}));
function setSize(w){ document.documentElement.style.setProperty('--lw', w + 'px'); try { localStorage.setItem('studioSize', w); } catch (e) {}
  document.querySelectorAll('#sizes button').forEach(b => b.classList.toggle('on', +b.dataset.w === w)); }
document.getElementById('sizes').innerHTML = [['S', 380], ['M', 520], ['L', 720]].map(([n, w]) => `<button class="quiet" data-w="${w}" onclick="setSize(${w})">${n}</button>`).join('');
{ let w = 520; try { w = +localStorage.getItem('studioSize') || 520; } catch (e) {} setSize(w); }

async function api(url, body){
  const r = await fetch(url + (url.includes('?') ? '&' : '?') + 'build=' + BUILD, {method: 'POST', body: body ? JSON.stringify(body) : undefined});
  if (!r.ok){ say('failed: ' + (await r.text()).replace(/<[^>]+>/g, ' ').trim().slice(0, 160)); return null; }
  await refresh(); return r; }
async function refresh(keepPlace = true){
  const err = document.getElementById('err');         // a failure stays on the page: a toast is gone in 2.5 s
  let r;
  try { r = await fetch('/api/project?build=' + BUILD); } catch (e) { err.textContent = 'Cannot load the project: the server did not answer (' + e.message + ').'; return; }
  if (!r.ok){ let why = ''; try { why = (await r.json()).error; } catch (e) {}
    err.textContent = 'Cannot load the project (HTTP ' + r.status + (why ? '): ' + why : ').'); return; }
  err.textContent = '';
  const first = !D, oldVersion = D && D.video_version; D = await r.json();
  if (!first && D.video_version !== oldVersion){ v.src = D.video + '?v=' + D.video_version; loadAll(); loadLangs(); say('the lecture video was rebuilt'); }
  document.getElementById('missing').value = D.settings.missing;
  if (first){ v.src = D.video + '?v=' + D.video_version; loadAll(); loadLangs();
    const h = location.hash.match(/open=(\d+)/);           // /edit?build=…#open=41 opens line 41
    if (h){ const k = Math.min(+h[1] - 1, D.lines.length - 1); open.add(k); curLine = k; setTimeout(() => document.getElementById('row' + k)?.scrollIntoView({block: 'center'}), 50); } }
  else if (document.getElementById('mode').textContent === 'whole lecture'){ const T = P.T, was = P.playing; loadAll(T); if (was) P.play(); }
  render(); poll(); }
function poll(){
  clearTimeout(poll.t);
  const busy = D.jobs.some(j => j.state === 'queued' || j.state === 'running') || D.sessions.some(s => ['recording', 'recorded', 'processing'].includes(s.state)) ||
    Object.values(D.versions).flat().some(x => MAKING.includes(x.state));
  if (busy) poll.t = setTimeout(refresh, 3000); }
function exportNow(){ const c = document.getElementById('clean').value; try { localStorage.setItem('studioClean', c); } catch (e) {}
  api('/api/export?clean=' + c).then(r => r && say('export queued')); }
try { document.getElementById('clean').value = localStorage.getItem('studioClean') || 'deepfilter'; } catch (e) {}


document.addEventListener('keydown', e => {
  const a = document.activeElement; if (['INPUT', 'SELECT', 'TEXTAREA'].includes(a.tagName) || a.isContentEditable) return;
  if (e.key === ' '){ e.preventDefault(); P.toggle(); }
  else if (e.key === 'ArrowRight'){ e.preventDefault(); playLine(Math.min(curLine + 1, D.lines.length - 1)); }
  else if (e.key === 'ArrowLeft'){ e.preventDefault(); playLine(Math.max(curLine - 1, 0)); }
  else if (e.key === 'Enter'){ open.add(curLine); render(); document.getElementById('row' + curLine)?.scrollIntoView({block: 'center'}); }
});
refresh();
