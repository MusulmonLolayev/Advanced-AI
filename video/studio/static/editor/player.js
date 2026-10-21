// The player: plays the two tracks (voice, picture) built by the server, the same ones the export renders.
// It drives a video element and an audio map it is handed, nothing else: the editor (main.js) and the presenter page's
// takes panel (presenter/takes.js) each build one. Classic script.
class Player {
  // v: the video element (the lecture's silent video). urls(): {voice source: audio URL}.
  // ui (all optional): state(playing), clock(T, total), line(k) when playing enters line k, end() when it plays to the end.
  constructor(v, urls, ui = {}){
    Object.assign(this, {v, urls, ui, off: false, vp: [], ap: [], total: 0, T: 0, playing: false, T0: 0, w0: 0, audios: {}, cur: null, spans: [], lastA: null}); }
  // off: a version's scene clip plays in the video itself (with its own sound), not the two tracks
  load(tr, spans, at){ this.pause(); this.vp = this.place(tr.picture); this.ap = this.place(tr.voice);
    this.total = this.vp.length ? this.vp[this.vp.length - 1].t + this.vp[this.vp.length - 1].p[0] : 0;
    this.spans = spans || []; this.seek(at || 0); }
  place(track){ let t = 0; return track.map(p => { const o = {t, p}; t += p[0]; return o; }); }
  find(list, T){ let lo = 0, hi = list.length - 1, k = -1;
    while (lo <= hi){ const m = (lo + hi) >> 1; if (list[m].t <= T + 1e-9){ k = m; lo = m + 1; } else hi = m - 1; }
    return k < 0 ? null : list[k]; }
  audio(src){ const url = this.urls()[src]; if (!url) return null;
    const a = this.audios[src];
    if (!a || a.url !== url){ if (a) a.el.pause(); const el = new Audio(url); el.preload = 'auto'; this.audios[src] = {url, el}; }
    return this.audios[src].el; }
  silence(){ Object.values(this.audios).forEach(a => a.el.pause()); }
  state(){ this.ui.state && this.ui.state(this.off ? !this.v.paused : this.playing); }
  play(){ if (this.off) return this.v.play().catch(() => {});
    if (this.T >= this.total - 0.01) this.T = 0; this.playing = true; this.T0 = this.T; this.w0 = performance.now(); this.state(); }
  pause(){ if (this.off) return this.v.pause();
    this.playing = false; this.v.pause(); this.silence(); this.state(); }
  toggle(){ if (this.off) return this.v.paused ? this.play() : this.pause();
    this.playing ? this.pause() : this.play(); }
  seek(T){ if (this.off){ this.v.currentTime = Math.max(0, T); return; }
    this.T = Math.max(0, Math.min(T, this.total)); this.T0 = this.T; this.w0 = performance.now(); this.sync(true); }
  clock(){ this.ui.clock && this.ui.clock(this.T, this.total); }
  frame(){ const v = this.v;
    if (this.off){ this.T = v.currentTime; this.total = v.duration || 0; this.state(); this.clock(); return; }
    if (this.playing){ this.T = this.T0 + (performance.now() - this.w0) / 1000;
      if (this.T >= this.total){ this.T = this.total; this.pause(); this.sync(false); this.ui.end && this.ui.end(); return; } }
    this.sync(false); }
  // Whether to put a media element at `want`. A forced seek (the user moved) or a jump (a voice piece that does not
  // continue the one before it) always lands exactly; otherwise only drift beyond `tol`, and never while the element
  // is still seeking or buffering: its currentTime then lags the clock, and seeking again each frame restarts the
  // load and replays the same fragment (worst on a slow link).
  static seekNow(el, want, force, jump, tol){
    if (force || jump) return true;
    if (el.seeking || el.readyState < 3) return false;
    return Math.abs(el.currentTime - want) > tol; }
  sync(force){ const v = this.v;
    const T = this.T, pv = this.find(this.vp, T), pa = this.find(this.ap, T);
    if (pv){ const [d, kind, a, b, s] = pv.p, local = T - pv.t;
      if (kind === 'play'){ const want = a + local * s;
        const rate = Math.min(16, Math.max(0.0625, s));       // browsers honour 0.0625 to 16; the squeezes use up to ~3.6
        if (v.playbackRate !== rate) v.playbackRate = rate;
        if (Player.seekNow(v, want, force, false, 0.25)) v.currentTime = want;
        if (this.playing && v.paused) v.play().catch(() => {}); if (!this.playing && !v.paused) v.pause(); }
      else { if (!v.paused) v.pause(); if (Math.abs(v.currentTime - a) > 0.03) v.currentTime = a; } }
    let el = null;
    if (pa && pa.p[1]){ el = this.audio(pa.p[1]);
      if (el){ const want = pa.p[2] + (T - pa.t), q = this.lastA;
        // entering a piece: contiguous with the one before (same source, its position plus its length) plays on
        const entered = pa !== q, same = q && q.p[1] === pa.p[1] && Math.abs(q.p[2] + q.p[0] - pa.p[2]) < 0.005;
        if (Player.seekNow(el, want, force, entered && !same, this.playing ? 0.25 : 0.15)) el.currentTime = want;
        if (this.playing && el.paused) el.play().catch(() => {}); if (!this.playing && !el.paused) el.pause(); } }
    this.lastA = pa;
    if (this.cur && this.cur !== el) this.cur.pause();
    this.cur = el;
    this.clock();
    const sp = this.spans.find(x => T >= x[1] && T < x[2]) || this.spans[this.spans.length - 1];
    if (sp && this.ui.line) this.ui.line(sp[0]); }
}
