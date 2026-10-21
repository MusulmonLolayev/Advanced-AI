// Voice level: the strip of one take (envelope, silences, picture, removed spans, draggable trim handles) and the
// lecture strip under the timeline (the whole edit list's level, long silences in amber).
// Classic script: shares D, open, curLine, P, edit, takeById, playTake, render … with the other editor scripts.
const LV = {step: 0.02, cache: {}, thr: {}, bad: {}, pending: {}, lec: null, version: null, drag: null, paint: 0};
const FLOOR = -80, SHOW_LO = -60, SHOW_HI = -10;           // dB: what digital silence reads as; the range drawn
const STRIP_H = 72, PAD = 8, SNAP = 0.05, MIN_PAUSE = 0.5, ORIGINAL_SRC = '__original__';
const COL = {};                                             // colours, read from the page's CSS variables once
function colours(){
  if (COL.acc) return COL;
  const s = getComputedStyle(document.documentElement);
  for (const k of ['acc', 'warn', 'bad', 'fg', 'dim']) COL[k] = s.getPropertyValue('--' + k).trim() || '#999';
  return COL; }

// ─── the data: one array of dB values (20 ms apart) per voice source, fetched once ───
function needLevels(src){
  if (LV.cache[src]) return LV.cache[src];
  if (LV.bad[src] || LV.pending[src]) return null;
  LV.pending[src] = fetch('/api/levels?build=' + BUILD + '&src=' + encodeURIComponent(src))
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(o => { LV.step = o.step; LV.cache[src] = Int8Array.from(o.db); LV.thr[src] = quietBelow(LV.cache[src]); })
    .catch(() => { LV.bad[src] = true; })
    .finally(() => { delete LV.pending[src]; LV.lec = null; redrawLevels(); });
  return null; }
function quietBelow(a){        // the server's rule for a pause (studio/media.silences): a third of the way from the room to the voice
  const h = new Array(FLOOR * -1 + 1).fill(0);
  for (const v of a) h[Math.min(-FLOOR, Math.max(0, v - FLOOR))]++;
  const pct = p => { let c = 0; for (let i = 0; i < h.length; i++){ c += h[i]; if (c >= p * a.length) return i + FLOOR; } return 0; };
  const floor = pct(0.10), voice = pct(0.95);
  return floor + (voice - floor) / 3; }
function redrawLevels(){
  if (LV.paint) return;
  LV.paint = requestAnimationFrame(() => { LV.paint = 0; drawStrips(); drawLecture(); }); }

// ─── what an edit removes: mirrors studio/timeline.plan (test_pages checks the two agree) ───
function mergeSpans(spans){
  const out = [];
  for (const [a, b] of spans.map(([p, q]) => p <= q ? [p, q] : [q, p]).sort((x, y) => x[0] - y[0] || x[1] - y[1])){
    if (out.length && a <= out[out.length - 1][1]) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b);
    else if (b > a) out.push([a, b]); }
  return out; }
function validSqueezes(sq){
  const out = []; let prev = 0;
  for (const [x, y, n] of sq.map(([a, b, n]) => [Math.min(a, b), Math.max(a, b), n]).sort((p, q) => p[0] - q[0] || p[1] - q[1] || p[2] - q[2])){
    if (n > 1e-9 && n < y - x - 1e-9 && x >= prev - 1e-9){ out.push([x, y, n]); prev = y; } }
  return out; }
function fastForward(picture, spans){          // picture: [[from, to, 'play' | 'hold']]
  const still = mergeSpans(picture.filter(p => p[2] === 'hold').map(p => [p[0], p[1]]));
  const cuts = [], sq = [];
  for (const [lo, hi] of spans){
    let t = lo;
    for (let [x, y] of still.concat([[hi, hi]])){
      x = Math.min(Math.max(x, lo), hi); y = Math.min(Math.max(y, lo), hi);
      const p = x - t;
      if (p > 1e-9 && Math.max(p / 4, 0.15) < p - 1e-9) sq.push([t, x, Math.max(p / 4, 0.15)]);
      if (y > x) cuts.push([x, y]);
      t = Math.max(t, y); } }
  return [mergeSpans(cuts), sq]; }
function planOf(edit, picture, total){        // -> {cuts, sq}: cuts merged, squeezes the ones squeeze() honours
  const ends = [];
  if (edit.trim_in) ends.push([0, Math.min(edit.trim_in, total)]);
  if (edit.trim_out) ends.push([Math.max(total - edit.trim_out, 0), total]);
  const [c, s] = fastForward(picture, ends);
  return {cuts: mergeSpans((edit.cuts || []).concat(edit.auto_cuts || [], c)), sq: validSqueezes((edit.squeeze || []).concat(s))}; }
function editedTime(plan, total, tt){          // where raw take time tt lands in the edited take (kept parts, squeezed ones faster)
  const f = plan.sq.map(([x, y, n]) => [x, y, (y - x) / n]);
  const pts = [...new Set([0, total, ...plan.cuts.flat(), ...f.flatMap(s => [s[0], s[1]])].map(x => Math.min(Math.max(x, 0), total)))].sort((a, b) => a - b);
  let out = 0;
  for (let i = 0; i + 1 < pts.length; i++){
    const u = pts[i], v = pts[i + 1], m = (u + v) / 2;
    if (v - u <= 1e-9 || plan.cuts.some(([a, b]) => a < m && m < b)) continue;
    const s = f.find(([a, b]) => a < m && m < b);
    out += Math.max(Math.min(v, tt) - u, 0) / (s ? s[2] : 1); }
  return out; }

// ─── the strip of one take ───
function stripOf(cv){ return takeById(cv.dataset.take); }
function liveTrims(t){
  const d = LV.drag;
  return d && d.id === t.id ? [d.tin, d.tout] : [t.edit.trim_in || 0, t.edit.trim_out || 0]; }
function pattern(g, rgb){        // diagonal hatching on a tinted ground
  const c = document.createElement('canvas'); c.width = c.height = 8;
  const h = c.getContext('2d');
  h.fillStyle = 'rgba(' + rgb + ',0.22)'; h.fillRect(0, 0, 8, 8);
  h.strokeStyle = 'rgba(' + rgb + ',0.9)'; h.lineWidth = 1.5; h.beginPath();
  h.moveTo(-2, 10); h.lineTo(10, -2); h.moveTo(-2, 2); h.lineTo(2, -2); h.moveTo(6, 10); h.lineTo(10, 6); h.stroke();
  return g.createPattern(c, 'repeat'); }
function keptText(lead, trim, where){
  if (lead > 0){ const k = lead - trim;
    return k >= -0.005 ? [Math.max(k, 0).toFixed(1) + ' s ' + where, false] : ['cuts ' + (-k).toFixed(1) + ' s into the voice', true]; }
  return trim > 0 ? ['trimmed ' + trim.toFixed(2) + ' s, no silence found here: may cut the voice', true] : ['under 0.4 s ' + where, false]; }
function drawStrip(cv){
  const t = stripOf(cv); if (!t || !cv.clientWidth) return;
  const col = colours(), dpr = window.devicePixelRatio || 1, W = cv.clientWidth, H = STRIP_H, total = t.raw_length;
  cv.width = Math.round(W * dpr); cv.height = H * dpr;
  const g = cv.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0);
  const X = tt => PAD + tt / total * (W - 2 * PAD), TT = x => (x - PAD) / (W - 2 * PAD) * total;
  const envTop = 16, envBot = 58, bandTop = 61, bandBot = 70;
  g.fillStyle = '#141414'; g.fillRect(0, 0, W, H);
  for (const [a, b] of t.pauses) if (b - a >= MIN_PAUSE){                 // silences of half a second or more
    g.fillStyle = 'rgba(215,180,106,0.13)'; g.fillRect(X(a), envTop, X(b) - X(a), envBot - envTop);
    if (X(b) - X(a) >= 34){ g.fillStyle = col.warn; g.font = '11px system-ui'; g.textAlign = 'center';
      g.fillText((b - a).toFixed(1) + ' s', (X(a) + X(b)) / 2, (envTop + envBot) / 2 + 4); } }
  const lv = needLevels(t.session);                                       // the envelope: the loudest value in each pixel
  g.textAlign = 'left';
  if (lv){
    g.fillStyle = col.acc; g.globalAlpha = 0.85;
    for (let px = 0; px < W; px += 1){
      const i0 = Math.floor((t.t_in + TT(px)) / LV.step), i1 = Math.max(i0 + 1, Math.floor((t.t_in + TT(px + 1)) / LV.step));
      if (px < PAD || px > W - PAD || i0 < 0) continue;
      let m = FLOOR; for (let i = i0; i < i1 && i < lv.length; i++) if (lv[i] > m) m = lv[i];
      const h = Math.max(0, Math.min(1, (m - SHOW_LO) / (SHOW_HI - SHOW_LO))) * (envBot - envTop);
      if (h > 0) g.fillRect(px, envBot - h, 1, h); }
    g.globalAlpha = 1; }
  else { g.fillStyle = col.dim; g.font = '12px system-ui'; g.fillText(LV.bad[t.session] ? 'no level for this recording' : 'loading the level…', PAD + 4, 40); }
  g.strokeStyle = '#2a2a2a'; g.beginPath(); g.moveTo(0, envBot + 0.5); g.lineTo(W, envBot + 0.5); g.stroke();
  for (const [a, b, kind] of t.raw_picture){                              // the picture: still dark, playing lighter
    g.fillStyle = kind === 'play' ? '#6d8fb0' : '#2c2c2c'; g.fillRect(X(a), bandTop, Math.max(1, X(b) - X(a)), bandBot - bandTop); }
  if (t.words){                                                           // the words, where they were said; none on top of another
    g.font = '10px system-ui'; g.fillStyle = '#bbb'; let right = -1e9;
    for (const [w, a] of t.words.heard){ const x = X(a), wd = g.measureText(w).width;
      if (x < right + 3 || x + wd > W - 2) continue; g.fillText(w, x, 11); right = x + wd; } }
  const [tin, tout] = liveTrims(t), plan = planOf(Object.assign({}, t.edit, {trim_in: tin, trim_out: tout}), t.raw_picture, total);
  const fills = [[plan.sq, pattern(g, '120,170,235')], [plan.cuts, pattern(g, '229,72,77')]];     // squeezed blue, then cut red over it
  for (const [spans, pat] of fills){ g.fillStyle = pat; for (const s of spans) g.fillRect(X(s[0]), 0, Math.max(1, X(s[1]) - X(s[0])), H); }
  const hx = [X(tin), X(total - tout)];                                    // the two handles: a line and a grip
  hx.forEach((x, i) => { g.fillStyle = '#eee'; g.fillRect(x - 1, 0, 2, H);
    g.beginPath(); g.rect(i ? x - 9 : x - 1, 0, 10, 20); g.fill();
    g.fillStyle = '#222'; for (const dx of [3, 6]) g.fillRect((i ? x - 9 : x - 1) + dx, 5, 1, 10); });
  const [s1, bad1] = keptText(t.lead, tin, 'before the first word'), [s2, bad2] = keptText(t.tail, tout, 'after the last word');
  const cap = cv.parentElement.querySelectorAll('.lvcap span');
  if (cap.length){ cap[0].textContent = '▏' + s1; cap[0].className = bad1 ? 'bad' : ''; cap[1].textContent = s2 + '▕'; cap[1].className = bad2 ? 'bad' : ''; }
  cv._geo = {X, TT, hx, total, W}; }
function drawStrips(){ document.querySelectorAll('.row.open canvas.lvc').forEach(drawStrip); }

// dragging a handle sets trim_in / trim_out (snapped to 0.05 s); saved on release, through the same edit() as everything
document.addEventListener('pointerdown', e => {
  const cv = e.target.closest && e.target.closest('canvas.lvc'); if (!cv || !cv._geo) return;
  const t = stripOf(cv), r = cv.getBoundingClientRect(), x = e.clientX - r.left, geo = cv._geo;
  const [tin, tout] = liveTrims(t), d = geo.hx.map(h => Math.abs(h - x));
  if (Math.min(...d) > 9) return;
  e.preventDefault(); cv.setPointerCapture(e.pointerId);
  LV.drag = {id: t.id, which: d[0] <= d[1] ? 0 : 1, tin, tout, cv, moved: false, done: false}; });
document.addEventListener('pointermove', e => {
  const cv = e.target.closest && e.target.closest('canvas.lvc');
  const d = LV.drag;
  if (!d){ if (cv && cv._geo){ const x = e.clientX - cv.getBoundingClientRect().left; cv.style.cursor = cv._geo.hx.some(h => Math.abs(h - x) <= 9) ? 'ew-resize' : 'pointer'; } return; }
  if (d.done) return;
  const t = stripOf(d.cv), geo = d.cv._geo, x = e.clientX - d.cv.getBoundingClientRect().left;
  const tt = Math.min(Math.max(Math.round(geo.TT(x) / SNAP) * SNAP, 0), geo.total);
  const room = Math.max(geo.total - 0.1, 0);                               // the two handles never cross
  if (d.which === 0) d.tin = Math.min(tt, Math.max(room - d.tout, 0)); else d.tout = Math.min(geo.total - tt, Math.max(room - d.tin, 0));
  d.moved = true; drawStrip(d.cv); });
document.addEventListener('pointerup', async e => {
  const d = LV.drag; if (!d) return;
  d.done = true;
  const t = stripOf(d.cv), r6 = v => Math.round(v * 100) / 100, ch = {};      // only the handle that moved: the other keeps its owner
  if (d.moved && t){
    if (r6(d.tin) !== r6(t.edit.trim_in || 0)) ch.trim_in = r6(d.tin) || null;
    if (r6(d.tout) !== r6(t.edit.trim_out || 0)) ch.trim_out = r6(d.tout) || null; }
  if (Object.keys(ch).length) await edit(d.id, ch);
  LV.drag = null; LV.justDragged = d.moved; setTimeout(() => LV.justDragged = false, 0); redrawLevels(); });
document.addEventListener('click', e => {                                 // a click on the strip plays the take from there
  const cv = e.target.closest && e.target.closest('canvas.lvc'); if (!cv || !cv._geo || LV.justDragged) return;
  const t = stripOf(cv), geo = cv._geo, tt = Math.min(Math.max(geo.TT(e.clientX - cv.getBoundingClientRect().left), 0), geo.total);
  const at = editedTime(planOf(t.edit, t.raw_picture, geo.total), geo.total, tt) + Math.max(-(t.edit.nudge || 0), 0);
  playTake(t, at); });

// ─── the lecture strip: the level of the whole edit list; silences of the chosen length or more in amber ───
function longSilence(){ let v = 1; try { v = parseFloat(localStorage.getItem('studioLongSilence')) || 1; } catch (e) {} return v; }
function setLongSilence(v){ v = Math.max(0.2, parseFloat(v) || 1); try { localStorage.setItem('studioLongSilence', v); } catch (e) {} drawLecture(); }
function lectureLevels(){          // {db, quiet, n, total} for D's edit list, once per refresh; null while a source is still coming
  if (LV.lec && LV.lec.D === D) return LV.lec;
  if (LV.version !== D.video_version){ delete LV.cache[ORIGINAL_SRC]; delete LV.thr[ORIGINAL_SRC]; LV.version = D.video_version; }
  const voice = D.edit_list.voice, srcs = [...new Set(voice.map(p => p[1]).filter(Boolean))];
  let wait = false; for (const s of srcs) if (!needLevels(s) && !LV.bad[s]) wait = true;
  if (wait) return null;
  const total = voice.reduce((a, p) => a + p[0], 0), n = Math.round(total * 50);
  const db = new Int8Array(n).fill(FLOOR), quiet = new Uint8Array(n).fill(1);     // a silent piece stays at the floor, quiet
  let t = 0;
  for (const [d, src, pos] of voice){
    const i0 = Math.round(t * 50), i1 = Math.min(n, Math.round((t + d) * 50)); t += d;
    const a = src && LV.cache[src]; if (!a) continue;
    const j0 = Math.round(pos * 50), th = LV.thr[src];
    for (let i = i0; i < i1; i++){ const v = j0 + i - i0 < a.length ? a[j0 + i - i0] : FLOOR; db[i] = v; quiet[i] = v <= th ? 1 : 0; } }
  return LV.lec = {D, db, quiet, n, total, broken: srcs.some(s => LV.bad[s])}; }
function longSilences(lec, minSec){  // [{a, b, line}] in edit-list seconds: runs of quiet frames, across line boundaries
  const out = [], need = Math.max(1, Math.ceil(minSec * 50 - 1e-9)), spans = D.edit_list.lines;
  let s = -1;
  for (let i = 0; i <= lec.n; i++){
    const q = i < lec.n && lec.quiet[i];
    if (q && s < 0) s = i;
    else if (!q && s >= 0){ if (i - s >= need){ const a = s / 50, sp = spans.find(x => a >= x[1] && a < x[2]) || spans[spans.length - 1];
        out.push({a, b: i / 50, line: sp ? sp[0] : 0}); } s = -1; } }
  return out; }
function drawLecture(){
  const cv = document.getElementById('lvc'); if (!cv || !D) return;
  const lec = lectureLevels(), cnt = document.getElementById('silcount');
  const col = colours(), dpr = window.devicePixelRatio || 1, W = cv.clientWidth, H = 36;
  cv.width = Math.round(W * dpr); cv.height = H * dpr;
  const g = cv.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = '#141414'; g.fillRect(0, 0, W, H);
  if (!lec){ cnt.textContent = 'loading the voice level…'; LV.sil = []; return; }
  const sil = LV.sil = longSilences(lec, longSilence()), sx = a => a / lec.total * W;
  const h = v => Math.max(0, Math.min(1, (v - SHOW_LO) / (SHOW_HI - SHOW_LO))) * (H - 2);
  for (let px = 0; px < W; px++){      // a pixel is many seconds: the peak, faint, and the mean level, solid (pauses pull it down)
    const i0 = Math.floor(px / W * lec.n), i1 = Math.max(i0 + 1, Math.floor((px + 1) / W * lec.n));
    let m = FLOOR, sum = 0; for (let i = i0; i < i1; i++){ if (lec.db[i] > m) m = lec.db[i]; sum += lec.db[i]; }
    g.globalAlpha = 0.3; g.fillStyle = col.acc; if (h(m) > 0) g.fillRect(px, H - h(m), 1, h(m));
    g.globalAlpha = 0.95; const hm = h(sum / (i1 - i0)); if (hm > 0) g.fillRect(px, H - hm, 1, hm); }
  g.globalAlpha = 0.9; g.fillStyle = col.warn;                             // the long silences, over it, at least 3 px wide
  for (const s of sil) g.fillRect(Math.floor(sx(s.a)), 0, Math.max(3, Math.ceil(sx(s.b) - sx(s.a))), H);
  g.globalAlpha = 1;
  const tot = sil.reduce((a, s) => a + s.b - s.a, 0);
  cnt.textContent = (lec.broken ? 'some levels are missing · ' : '') + sil.length + ' long silence' + (sil.length === 1 ? '' : 's') + ', ' + tot.toFixed(1) + ' s'; }
function silenceNear(T){  // the silence under a click on the strip, within 6 px
  const cv = document.getElementById('lvc'), lec = LV.lec; if (!lec || !LV.sil) return null;
  const px = lec.total / cv.clientWidth, slack = 6 * px;
  return LV.sil.filter(s => T >= s.a - slack && T <= s.b + slack).sort((p, q) => Math.abs(p.a - T) - Math.abs(q.a - T))[0] || null; }
function showSilence(s){
  if (document.getElementById('mode').textContent !== 'whole lecture') loadAll();
  P.seek(s.a); open.add(s.line); curLine = s.line; render();
  document.getElementById('row' + s.line)?.scrollIntoView({block: 'center'}); }
function gotoSilence(dir){
  const sil = LV.sil || [];
  if (!sil.length){ say('no silence of ' + longSilence() + ' s or more'); return; }
  if (document.getElementById('mode').textContent !== 'whole lecture') loadAll();
  const T = P.T, hit = dir > 0 ? sil.find(s => s.a > T + 0.05) : sil.slice().reverse().find(s => s.a < T - 0.05);
  if (!hit){ say(dir > 0 ? 'no more long silences after this' : 'no long silence before this'); return; }
  showSilence(hit); }
document.getElementById('lvc').addEventListener('click', e => {
  const r = e.currentTarget.getBoundingClientRect(), lec = LV.lec; if (!lec) return;
  const T = lec.total * (e.clientX - r.left) / r.width, s = silenceNear(T);
  if (s) return showSilence(s);
  if (document.getElementById('mode').textContent !== 'whole lecture') loadAll();
  P.seek(T); });
window.addEventListener('resize', redrawLevels);
