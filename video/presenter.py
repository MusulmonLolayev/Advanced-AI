"""A presenter copy of a built video, for explaining it live in your own voice.

Writes <build>/presenter/: the video without its audio (picture copied) and presenter.html, a local page that plays it
and pauses just before each narration line starts, so every line's animation has finished and you talk over it for as
long as you like. Space (or P) pauses and plays: pressed while a line plays it pauses right there, pressed again it
carries on, and once a line has finished it plays the next one. → plays the next line (pressed while a line plays,
it jumps to that line's end; a presentation clicker sends it). The video plays at 1/1.1 of its speed, and each
recording logs the speed so the build matches. ← shows the
start of the current line (again: the line before), N moves the notes (the line's text, and the next
one): under the picture, at the right, hidden; the choice is remembered. While a line plays, its words light up at
the pace of the original narration (the subtitle chunks' times, spread over the words), so you can keep up. F is full screen, M picks the microphone (with a level meter; the choice is remembered), R records your voice
(press R again to stop). While recording, the page sends the recording to the server every second (and keeps each
piece in the browser until the server has it, so a closed tab or a dropped tunnel loses nothing: the next visit
sends what was left), logs where each line starts, and X marks a mistake: the take of the line on screen is
rejected and the line starts over, so you say it again without stopping. The studio's editor (/edit) cuts the
session into one take per line. presenter.html#line=41 opens at line 41 (to record just that line again). Lines are found in each scene's subtitles: chunks of one line follow each other
0.1 s apart, a new line starts after a longer gap (>= 0.23 s).

    uv run python presenter.py out/agents_course_en        # then open out/agents_course_en/presenter/presenter.html
"""
import json
import subprocess
import sys
from pathlib import Path

GAP = 0.15                 # chunks of one line are exactly 0.1 s apart; lines are >= 0.23 s apart


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                 "stream=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True, check=True).stdout)


def cues(srt):
    out = []
    for block in Path(srt).read_text().strip().split("\n\n"):
        rows = block.splitlines()
        if len(rows) >= 3:
            a, b = (sum(float(x) * m for x, m in zip(t.replace(",", ".").split(":"), (3600, 60, 1)))
                    for t in rows[1].split(" --> "))
            out.append((a, b, " ".join(rows[2:])))
    return out


def lines(build):
    """[(start s, text, [(chunk start, chunk end, chunk text)], scene index)] for every narration line of the joined
    video."""
    parts = [Path(r.split("'")[1]) for r in (build / "parts.txt").read_text().splitlines() if r.startswith("file")]
    joined = [Path(r.split("'")[1]) for r in (build / "joined.txt").read_text().splitlines() if r.startswith("file")]
    out, off = [], 0.0
    for n, (scene, j) in enumerate(zip(parts, joined)):
        prev_end = None
        for a, b, text in cues(scene.with_suffix(".srt")) if scene.with_suffix(".srt").exists() else []:
            chunk = [round(off + a, 3), round(off + b, 3), text]
            if prev_end is None or a - prev_end > GAP:
                out.append([off + a, text, [chunk], n])
            else:
                out[-1][1] += " " + text
                out[-1][2].append(chunk)
            prev_end = b
        off += duration(j)
    return [(round(t, 3), s, c, n) for t, s, c, n in out], off


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Presenter</title>
<style>
:root{--bg:#000;--fg:#eee;--dim:#888;--accent:#8fb8de}
html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:18px/1.45 system-ui,sans-serif}
#wrap{display:flex;height:100%}
video{flex:1;min-width:0;min-height:0;background:#000;object-fit:contain}
#notes{width:30%;max-width:520px;padding:18px 22px;box-sizing:border-box;overflow:auto;border-left:1px solid #222}
body.below #wrap{flex-direction:column}
body.below video{width:100%}
body.below #notes{width:100%;max-width:none;max-height:30vh;border-left:0;border-top:1px solid #222;
  padding:10px 6vw 34px;text-align:center}
body.below #cur{font-size:30px;line-height:1.35}
body.below #next{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
body.below .lab{display:none}
body.hidden #notes{display:none}
.lab{color:var(--dim);font-size:13px;letter-spacing:.04em;text-transform:uppercase;margin-top:14px}
#cur{font-size:22px}#next{color:var(--dim);margin-top:6px}
#cur span{color:#9a9a9a;transition:color .12s}
#cur span.said{color:#fff}
#bar{position:fixed;left:0;bottom:0;right:0;padding:6px 12px;font-size:13px;color:var(--dim);background:#000c}
#rec{position:fixed;top:10px;left:12px;font-size:15px;color:#e5484d;display:none}
#mic{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#111;border:1px solid #333;
  border-radius:8px;padding:18px 22px;width:min(460px,90vw);display:none}
#mic select{width:100%;font:inherit;background:#222;color:var(--fg);border:1px solid #444;padding:6px}
#lvl{height:10px;background:#222;border-radius:5px;margin-top:12px;overflow:hidden}
#lvl div{height:100%;width:0;background:var(--accent)}
</style></head><body>
<div id="wrap"><video id="v" src="VIDEO" preload="auto"></video>
<div id="notes"><div class="lab">now · <span id="num"></span></div><div id="cur"></div>
<div class="lab">next</div><div id="next"></div></div></div>
<div id="rec"></div>
<div id="mic"><div class="lab" style="margin-top:0">microphone</div><select id="micsel"></select>
<div id="lvl"><div></div></div><div class="lab">speak to test the level · M or Esc closes</div></div>
<div id="bar">Space pause / play · → next line (while playing: jump to its end) · ← back · X mistake: retake this line · N notes: below / right / off · F full screen · M microphone · R record</div>
<script>
const L = LINES, BUILD = "BUILD", v = document.getElementById('v'), recEl = document.getElementById('rec');
// recording: the microphone, and every moment the picture starts or stops, so the video can be rebuilt around the voice
let rec = null, t0 = 0, ev = [], session = null, seq = 0, sendQ = Promise.resolve(), waiting = 0, evTimer = null;
function log(kind, k){ if (rec && t0){ const e = [(performance.now() - t0) / 1000, kind, v.currentTime, v.playbackRate];
  if (k !== undefined) e.push(k); ev.push(e); } }
v.addEventListener('playing', () => log('play'));
v.defaultPlaybackRate = v.playbackRate = 1 / 1.1;                         // the narration's pace felt fast
v.addEventListener('pause', () => log('hold'));
v.addEventListener('waiting', () => log('hold'));
v.addEventListener('seeked', () => { if (v.paused) log('hold'); });   // a jump while held: hold the new frame
// every piece is kept in the browser (IndexedDB) until the server has it; sent in order, retried until it gets there
const sleep = ms => new Promise(r => setTimeout(r, ms));
function idb(){ return new Promise((ok, no) => { const r = indexedDB.open('presenterChunks', 1);
  r.onupgradeneeded = () => r.result.createObjectStore('c'); r.onsuccess = () => ok(r.result); r.onerror = () => no(r.error); }); }
async function idbDo(mode, f){ try { const d = await idb(); return await new Promise((ok, no) => {
  const tx = d.transaction('c', mode), out = f(tx.objectStore('c')); tx.oncomplete = () => ok(out && out.result);
  tx.onerror = () => no(tx.error); }); } catch (e) { return null; } }
const keep = (key, val) => idbDo('readwrite', s => s.put(val, key)), drop = key => idbDo('readwrite', s => s.delete(key));
async function pending(){ const d = await idb().catch(() => null); if (!d) return [];
  return new Promise(ok => { const out = [], tx = d.transaction('c', 'readonly'), cur = tx.objectStore('c').openCursor();
    cur.onsuccess = () => { const c = cur.result; if (c){ out.push([c.key, c.value]); c.continue(); } else ok(out); };
    cur.onerror = () => ok(out); }); }
async function send(url, body){
  for (let wait = 500;; wait = Math.min(wait * 2, 8000)){
    let r = null;
    try { r = await fetch(url, {method: 'POST', body}); } catch (e) {}       // offline: wait and try again
    if (r && r.ok) return;
    if (r && r.status === 400) throw new Error(await r.text());           // refused: retrying will not help
    status(); await sleep(wait); } }
function queue(key, url, body){ waiting++; status();
  sendQ = sendQ.then(() => send(url, body)).then(() => drop(key)).catch(e => { recEl.textContent = 'NOT saved: ' + e; })
               .finally(() => { waiting--; status(); }); return sendQ; }
function status(){
  if (!rec && !waiting) return;
  recEl.style.display = 'block';
  recEl.textContent = (rec ? '● REC' + (rec.micName ? ' — ' + rec.micName : '') : 'saving…') +
    (waiting > 2 ? ' — ' + waiting + ' pieces waiting for the server' : ''); }
function chunk(name, k, blob){ const key = `${BUILD}|${name}|${String(k).padStart(6, '0')}`;
  keep(key, {build: BUILD, name, seq: k, blob}); queue(key, `/api/chunk?build=${BUILD}&name=${name}&seq=${k}`, blob); }
function events(name){ const key = `${BUILD}|${name}|events`, body = JSON.stringify(ev);
  keep(key, {build: BUILD, name, events: body}); queue(key, `/api/events?build=${BUILD}&name=${name}`, body); }
async function recover(){                       // pieces a closed tab never sent: send them now, then close that session
  const left = (await pending()).filter(([k, v]) => v.build === BUILD).sort((a, b) => a[0] < b[0] ? -1 : 1);
  const names = [...new Set(left.map(([k, v]) => v.name))];
  for (const [key, val] of left){
    if (val.blob) queue(key, `/api/chunk?build=${BUILD}&name=${val.name}&seq=${val.seq}`, val.blob);
    else queue(key, `/api/events?build=${BUILD}&name=${val.name}`, val.events); }
  for (const n of names) queue(`${BUILD}|${n}|finish`, `/api/finish?build=${BUILD}&name=${n}`, '');
  if (names.length){ await sendQ; recEl.style.display = 'block';
    recEl.innerHTML = 'recovered an unsent recording: ' + names.join(', ') + ' — <a href="/edit?build=' + BUILD + '" style="color:#8fb8de">open the editor</a>'; } }
// the microphone: the one chosen with M (remembered in this browser), else the default
const micEl = document.getElementById('mic'), micSel = document.getElementById('micsel'),
      lvl = document.querySelector('#lvl div');
let micId = '', meter = null;
try { micId = localStorage.getItem('presenterMic') || ''; } catch (e) {}
function audio(id){ return {audio: {echoCancellation: false, autoGainControl: true, ...(id ? {deviceId: {exact: id}} : {})}}; }
async function openStream(){                    // the chosen microphone; if it is gone, the default one
  if (micId){ try { return await navigator.mediaDevices.getUserMedia(audio(micId)); } catch (e) {} }
  return navigator.mediaDevices.getUserMedia(audio(''));
}
function stopMeter(){ if (meter){ meter.stream.getTracks().forEach(t => t.stop()); meter.ctx.close(); meter = null; } lvl.style.width = 0; }
async function startMeter(){
  stopMeter();
  const stream = await openStream(), ctx = new AudioContext(), an = ctx.createAnalyser();
  an.fftSize = 1024; ctx.createMediaStreamSource(stream).connect(an);
  const buf = new Float32Array(an.fftSize); meter = {stream, ctx};
  const m = meter;
  (function draw(){ if (meter !== m) return; an.getFloatTimeDomainData(buf);
    let peak = 0; for (const x of buf) peak = Math.max(peak, Math.abs(x));
    lvl.style.width = Math.min(100, peak * 100) + '%'; requestAnimationFrame(draw); })();
  return stream;
}
async function toggleMic(){
  if (micEl.style.display === 'block'){ micEl.style.display = 'none'; stopMeter(); micSel.blur(); return; }
  if (rec) return;                               // not while recording
  let stream;
  try { stream = await startMeter(); }           // asking once lets the browser show the devices' names
  catch (e){ alert('No microphone: open this page through http://localhost (see the ssh -L tunnel). ' + e); return; }
  const used = stream.getAudioTracks()[0].getSettings().deviceId;
  const devs = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'audioinput');
  micSel.innerHTML = '';
  devs.forEach((d, k) => { const o = document.createElement('option'); o.value = d.deviceId;
    o.textContent = d.label || ('microphone ' + (k + 1)); o.selected = d.deviceId === used; micSel.appendChild(o); });
  micEl.style.display = 'block'; micSel.focus();
}
micSel.addEventListener('change', async () => {
  micId = micSel.value; try { localStorage.setItem('presenterMic', micId); } catch (e) {}
  try { await startMeter(); } catch (e){ alert('Cannot open this microphone: ' + e); } });
async function toggleRec(){
  if (rec){ log('stop'); rec.stop(); return; }
  if (micEl.style.display === 'block') toggleMic();
  let stream;
  try { stream = await openStream(); }
  catch (e){ alert('No microphone: open this page through http://localhost (see the ssh -L tunnel). ' + e); return; }
  ev = []; seq = 0;
  session = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const name = session;
  rec = new MediaRecorder(stream, {mimeType: 'audio/webm;codecs=opus'});
  rec.micName = stream.getAudioTracks()[0].label;
  rec.ondataavailable = e => { if (e.data.size) chunk(name, seq++, e.data); };
  rec.onstart = () => { t0 = performance.now(); ev.push([0, v.paused ? 'hold' : 'play', v.currentTime, v.playbackRate]);
    if (!v.paused || stopAt !== null) ev.push([0, 'line', L[i][0], v.playbackRate, i]);
    evTimer = setInterval(() => events(name), 5000); status(); };
  rec.onstop = async () => { stream.getTracks().forEach(t => t.stop()); clearInterval(evTimer);
    rec = null; events(name); t0 = 0;
    queue(`${BUILD}|${name}|finish`, `/api/finish?build=${BUILD}&name=${name}`, '');
    await sendQ;
    if (recEl.textContent.startsWith('NOT')) return;
    recEl.style.display = 'block';
    recEl.innerHTML = 'saved: ' + name + ' — <a href="/edit?build=' + BUILD + '" style="color:#8fb8de">open the editor</a>';
    counts(); };
  rec.start(1000); }
function retake(){                              // X: this line's take is a mistake; start the line over
  if (!rec) return;
  log('retake', i); v.pause(); stopAt = null; v.currentTime = L[i][0]; nxt = i; show();
  recEl.textContent = '● REC — retake line ' + (i + 1); }
let takeCount = {};
async function counts(){ try { const r = await fetch(`/api/counts?build=${BUILD}`); if (r.ok){ takeCount = await r.json(); show(); } } catch (e) {} }
let i = 0, stopAt = null;                       // i: the line on screen; stopAt: where playing stops
// the line's words, each with the moment the original voice reached it (a chunk's time spread over its words by length)
const cur = document.getElementById('cur');
let words = [];
function lineWords(k){
  cur.textContent = ''; words = [];
  for (const [a, b, text] of (L[k] ? L[k][2] : [])){
    const ws = text.split(/\\s+/).filter(Boolean), n = ws.reduce((x, w) => x + w.length + 1, 0);
    let c = 0;
    for (const w of ws){ const el = document.createElement('span'); el.textContent = w + ' ';
      words.push([a + (b - a) * c / n, el]); cur.appendChild(el); c += w.length + 1; } } }
function said(){ const t = v.currentTime; for (const [ws, el] of words) el.classList.toggle('said', t >= ws + 0.03); }
const MODES = ['below', 'right', 'hidden'];
let mode = 'below';
try { mode = MODES.includes(localStorage.getItem('presenterNotes')) ? localStorage.getItem('presenterNotes') : 'below'; } catch (e) {}
function place(m){ mode = m; document.body.classList.remove(...MODES); document.body.classList.add(m);
  try { localStorage.setItem('presenterNotes', m); } catch (e) {} }
function show(){ const n = takeCount[i] || 0;
  document.getElementById('num').textContent = (i+1)+' / '+L.length + (n ? ' · ' + n + (n > 1 ? ' takes' : ' take') : '');
  lineWords(i); said();
  document.getElementById('next').textContent = L[i+1] ? L[i+1][1] : '— end —'; }
function play(k){ i = Math.max(0, Math.min(k, L.length-1)); nxt = i + 1; v.currentTime = L[i][0];
  stopAt = L[i+1] ? L[i+1][0] - 0.04 : null; show(); log('line', i); v.play(); }
let nxt = 0;                                    // the line the next press plays
function next(){
  if (!v.paused){ v.pause(); if (stopAt !== null) v.currentTime = stopAt; stopAt = null; return; }  // finish this line now
  if (stopAt !== null){ v.play(); return; }      // a line paused with P: carry on
  if (nxt < L.length) play(nxt); }
function toggle(){                             // Space / P: pause here, carry on, or start the next line
  if (!v.paused){ v.pause(); return; }
  if (stopAt !== null){ v.play(); return; }      // paused mid-line: carry on
  if (nxt < L.length) play(nxt); }
function back(){                                // the current line's first frame; pressed again, the line before
  v.pause(); stopAt = null;
  if (Math.abs(v.currentTime - L[i][0]) < 0.05) i = Math.max(0, i - 1);
  v.currentTime = L[i][0]; nxt = i; show(); }
function tick(){ said(); if (stopAt !== null && !v.paused && v.currentTime >= stopAt){ v.pause(); v.currentTime = stopAt; stopAt = null; }
  requestAnimationFrame(tick); }
document.addEventListener('keydown', e => {
  if (micEl.style.display === 'block'){         // the picker is open: arrows choose a microphone
    if (e.key === 'Escape' || e.key === 'm' || e.key === 'M'){ e.preventDefault(); toggleMic(); }
    return; }
  if (e.key === 'm' || e.key === 'M') toggleMic();
  else if (e.key === ' ' || e.key === 'p' || e.key === 'P'){ e.preventDefault(); toggle(); }
  else if (e.key === 'ArrowRight' || e.key === 'PageDown'){ e.preventDefault(); next(); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp'){ e.preventDefault(); back(); }
  else if (e.key === 'r' || e.key === 'R') toggleRec();
  else if (e.key === 'x' || e.key === 'X') retake();
  else if (e.key === 'n' || e.key === 'N') place(MODES[(MODES.indexOf(mode) + 1) % MODES.length]);
  else if (e.key === 'f' || e.key === 'F'){ document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
});
const at = location.hash.match(/line=(\\d+)/);       // presenter.html#line=41: start at line 41
if (at){ i = Math.max(0, Math.min(+at[1] - 1, L.length - 1)); nxt = i; v.currentTime = L[i][0]; }
place(mode); show(); requestAnimationFrame(tick); counts(); recover();
</script></body></html>"""


def main(build):
    build = Path(build)
    final = build / f"{build.name}.mp4"
    out = build / "presenter"
    out.mkdir(exist_ok=True)
    silent = out / f"{build.name}_silent.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(final), "-map", "0:v", "-c", "copy", "-an", "-movflags", "+faststart",
                    str(silent)], check=True)
    ls, total = lines(build)
    if abs(total - duration(final)) > 0.5:
        sys.exit(f"scene lengths add up to {total:.1f} s but the video is {duration(final):.1f} s: rejoin first")
    (out / "presenter.html").write_text(PAGE.replace("VIDEO", f"{silent.name}?v={int(silent.stat().st_mtime)}")
                                        .replace("LINES", json.dumps(ls, ensure_ascii=False)).replace("BUILD", build.name))
    (out / "lines.json").write_text(json.dumps(ls, ensure_ascii=False, indent=1))
    print(f"{len(ls)} lines; open {out / 'presenter.html'}")


if __name__ == "__main__":
    main(sys.argv[1])
