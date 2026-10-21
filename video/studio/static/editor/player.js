// The player: plays the two tracks (voice, picture) built by the server, the same ones the export renders.
// Classic script: shares globals (v, D, curLine, fmt …, declared in main.js) with the other editor scripts.
const P = {
  // off: a version's scene clip plays in the video itself (with its own sound), not the two tracks
  off: false, vp: [], ap: [], total: 0, T: 0, playing: false, T0: 0, w0: 0, audios: {}, cur: null, spans: [],
  load(tr, spans, at){ this.pause(); this.vp = this.place(tr.picture); this.ap = this.place(tr.voice);
    this.total = this.vp.length ? this.vp[this.vp.length - 1].t + this.vp[this.vp.length - 1].p[0] : 0;
    this.spans = spans || []; this.seek(at || 0); },
  place(track){ let t = 0; return track.map(p => { const o = {t, p}; t += p[0]; return o; }); },
  find(list, T){ let lo = 0, hi = list.length - 1, k = -1;
    while (lo <= hi){ const m = (lo + hi) >> 1; if (list[m].t <= T + 1e-9){ k = m; lo = m + 1; } else hi = m - 1; }
    return k < 0 ? null : list[k]; },
  audio(src){ const url = D.audio[src]; if (!url) return null;
    if (!this.audios[src]){ const a = new Audio(url); a.preload = 'auto'; this.audios[src] = a; } return this.audios[src]; },
  play(){ if (this.off) return v.play().catch(() => {});
    if (this.T >= this.total - 0.01) this.T = 0; this.playing = true; this.T0 = this.T; this.w0 = performance.now(); document.getElementById('pp').textContent = '⏸'; },
  pause(){ if (this.off) return v.pause();
    this.playing = false; v.pause(); Object.values(this.audios).forEach(a => a.pause()); document.getElementById('pp').textContent = '▶'; },
  toggle(){ if (this.off) return v.paused ? this.play() : this.pause();
    this.playing ? this.pause() : this.play(); },
  seek(T){ if (this.off){ v.currentTime = Math.max(0, T); return; }
    this.T = Math.max(0, Math.min(T, this.total)); this.T0 = this.T; this.w0 = performance.now(); this.sync(true); },
  frame(){ if (this.off){ this.T = v.currentTime; this.total = v.duration || 0;
      document.getElementById('pp').textContent = v.paused ? '▶' : '⏸';
      document.getElementById('clock').textContent = fmt(this.T) + ' / ' + fmt(this.total);
      setCursor(this.total ? 100 * this.T / this.total : 0); return; }
    if (this.playing){ this.T = this.T0 + (performance.now() - this.w0) / 1000;
      if (this.T >= this.total){ this.T = this.total; this.pause(); } }
    this.sync(false); },
  sync(force){
    const T = this.T, pv = this.find(this.vp, T), pa = this.find(this.ap, T);
    if (pv){ const [d, kind, a, b, s] = pv.p, local = T - pv.t;
      if (kind === 'play'){ const want = a + local * s;
        const rate = Math.min(16, Math.max(0.0625, s));       // browsers honour 0.0625 to 16; the squeezes use up to ~3.6
        if (v.playbackRate !== rate) v.playbackRate = rate;
        if (force || Math.abs(v.currentTime - want) > 0.25) v.currentTime = want;
        if (this.playing && v.paused) v.play().catch(() => {}); if (!this.playing && !v.paused) v.pause(); }
      else { if (!v.paused) v.pause(); if (Math.abs(v.currentTime - a) > 0.03) v.currentTime = a; } }
    let el = null;
    if (pa && pa.p[1]){ el = this.audio(pa.p[1]);
      if (el){ const want = pa.p[2] + (T - pa.t);
        if (force || Math.abs(el.currentTime - want) > 0.15) el.currentTime = want;
        if (this.playing && el.paused) el.play().catch(() => {}); if (!this.playing && !el.paused) el.pause(); } }
    if (this.cur && this.cur !== el) this.cur.pause();
    this.cur = el;
    document.getElementById('clock').textContent = fmt(T) + ' / ' + fmt(this.total);
    setCursor(this.total ? 100 * T / this.total : 0);
    const sp = this.spans.find(x => T >= x[1] && T < x[2]) || this.spans[this.spans.length - 1];
    if (sp && sp[0] !== curLine){ curLine = sp[0]; showNow(); }
  },
};

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

