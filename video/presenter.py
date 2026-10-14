"""A presenter copy of a built video, for explaining it live in your own voice.

Writes <build>/presenter/: the video without its audio (picture copied) and presenter.html, a local page that plays it
and pauses just before each narration line starts, so every line's animation has finished and you talk over it for as
long as you like. Space or → plays the next line (pressed while a line plays, it jumps to that line's end), P pauses mid-line, ← shows the
start of the current line (again: the line before), N shows or hides the notes (the line's text,
and the next one), F is full screen, R records your voice
(press R again to stop; it is saved on the server, and compose_recording.py turns it into a video). Lines are found in each scene's subtitles: chunks of one line follow each other
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
    """[(start s, text)] for every narration line of the joined video."""
    parts = [Path(r.split("'")[1]) for r in (build / "parts.txt").read_text().splitlines() if r.startswith("file")]
    joined = [Path(r.split("'")[1]) for r in (build / "joined.txt").read_text().splitlines() if r.startswith("file")]
    out, off = [], 0.0
    for scene, j in zip(parts, joined):
        prev_end = None
        for a, b, text in cues(scene.with_suffix(".srt")) if scene.with_suffix(".srt").exists() else []:
            if prev_end is None or a - prev_end > GAP:
                out.append([off + a, text])
            else:
                out[-1][1] += " " + text
            prev_end = b
        off += duration(j)
    return [(round(t, 3), s) for t, s in out], off


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Presenter</title>
<style>
:root{--bg:#000;--fg:#eee;--dim:#888;--accent:#8fb8de}
html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:18px/1.45 system-ui,sans-serif}
#wrap{display:flex;height:100%}
video{flex:1;min-width:0;height:100%;background:#000;object-fit:contain}
#notes{width:30%;max-width:520px;padding:18px 22px;box-sizing:border-box;overflow:auto;border-left:1px solid #222}
#notes.hidden{display:none}
.lab{color:var(--dim);font-size:13px;letter-spacing:.04em;text-transform:uppercase;margin-top:14px}
#cur{font-size:22px}#next{color:var(--dim)}
#bar{position:fixed;left:0;bottom:0;right:0;padding:6px 12px;font-size:13px;color:var(--dim);background:#000c}
#rec{position:fixed;top:10px;left:12px;font-size:15px;color:#e5484d;display:none}
</style></head><body>
<div id="wrap"><video id="v" src="VIDEO" preload="auto"></video>
<div id="notes"><div class="lab">now · <span id="num"></span></div><div id="cur"></div>
<div class="lab">next</div><div id="next"></div></div></div>
<div id="rec"></div><div id="bar">Space / → next line (while playing: jump to its end) · ← back · P pause · N notes · F full screen · R record</div>
<script>
const L = LINES, BUILD = "BUILD", v = document.getElementById('v'), recEl = document.getElementById('rec');
// recording: the microphone, and every moment the picture starts or stops, so the video can be rebuilt around the voice
let rec = null, t0 = 0, ev = [], chunks = [];
function log(kind){ if (rec && t0) ev.push([(performance.now() - t0) / 1000, kind, v.currentTime]); }
v.addEventListener('playing', () => log('play'));
v.addEventListener('pause', () => log('hold'));
v.addEventListener('waiting', () => log('hold'));
v.addEventListener('seeked', () => { if (v.paused) log('hold'); });   // a jump while held: hold the new frame
async function upload(name, kind, body){
  const r = await fetch(`/upload?build=${BUILD}&name=${name}&kind=${kind}`, {method: 'POST', body});
  if (!r.ok) throw new Error(await r.text()); }
async function toggleRec(){
  if (rec){ log('stop'); rec.stop(); return; }
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: false, autoGainControl: true}}); }
  catch (e){ alert('No microphone: open this page through http://localhost (see the ssh -L tunnel). ' + e); return; }
  chunks = []; ev = [];
  rec = new MediaRecorder(stream, {mimeType: 'audio/webm;codecs=opus'});
  rec.ondataavailable = e => chunks.push(e.data);
  rec.onstart = () => { t0 = performance.now(); ev.push([0, v.paused ? 'hold' : 'play', v.currentTime]);
    recEl.style.display = 'block'; recEl.textContent = '● REC'; };
  rec.onstop = async () => { stream.getTracks().forEach(t => t.stop());
    const name = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    recEl.textContent = 'saving…';
    try { await upload(name, 'webm', new Blob(chunks, {type: 'audio/webm'}));
          await upload(name, 'json', JSON.stringify(ev));
          recEl.textContent = 'saved: ' + name; }
    catch (e){ recEl.textContent = 'NOT saved: ' + e; }
    rec = null; t0 = 0; };
  rec.start(1000); }
let i = 0, stopAt = null;                       // i: the line on screen; stopAt: where playing stops
function show(){ document.getElementById('num').textContent = (i+1)+' / '+L.length;
  document.getElementById('cur').textContent = L[i] ? L[i][1] : '';
  document.getElementById('next').textContent = L[i+1] ? L[i+1][1] : '— end —'; }
function play(k){ i = Math.max(0, Math.min(k, L.length-1)); nxt = i + 1; v.currentTime = L[i][0];
  stopAt = L[i+1] ? L[i+1][0] - 0.04 : null; show(); v.play(); }
let nxt = 0;                                    // the line the next press plays
function next(){
  if (!v.paused){ v.pause(); if (stopAt !== null) v.currentTime = stopAt; stopAt = null; return; }  // finish this line now
  if (stopAt !== null){ v.play(); return; }      // a line paused with P: carry on
  if (nxt < L.length) play(nxt); }
function back(){                                // the current line's first frame; pressed again, the line before
  v.pause(); stopAt = null;
  if (Math.abs(v.currentTime - L[i][0]) < 0.05) i = Math.max(0, i - 1);
  v.currentTime = L[i][0]; nxt = i; show(); }
function tick(){ if (stopAt !== null && !v.paused && v.currentTime >= stopAt){ v.pause(); v.currentTime = stopAt; stopAt = null; }
  requestAnimationFrame(tick); }
document.addEventListener('keydown', e => {
  if (e.key === ' ' || e.key === 'ArrowRight' || e.key === 'PageDown'){ e.preventDefault(); next(); }
  else if (e.key === 'p' || e.key === 'P'){ e.preventDefault(); if (!v.paused) v.pause(); else if (stopAt !== null) v.play(); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp'){ e.preventDefault(); back(); }
  else if (e.key === 'r' || e.key === 'R') toggleRec();
  else if (e.key === 'n' || e.key === 'N') document.getElementById('notes').classList.toggle('hidden');
  else if (e.key === 'f' || e.key === 'F'){ document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
});
show(); requestAnimationFrame(tick);
</script></body></html>"""


def main(build):
    build = Path(build)
    final = build / f"{build.name}.mp4"
    out = build / "presenter"
    out.mkdir(exist_ok=True)
    silent = out / f"{build.name}_silent.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(final), "-map", "0:v", "-c", "copy", "-an",
                    str(silent)], check=True)
    ls, total = lines(build)
    if abs(total - duration(final)) > 0.5:
        sys.exit(f"scene lengths add up to {total:.1f} s but the video is {duration(final):.1f} s: rejoin first")
    (out / "presenter.html").write_text(PAGE.replace("VIDEO", silent.name)
                                        .replace("LINES", json.dumps(ls, ensure_ascii=False)).replace("BUILD", build.name))
    (out / "lines.json").write_text(json.dumps(ls, ensure_ascii=False, indent=1))
    print(f"{len(ls)} lines; open {out / 'presenter.html'}")


if __name__ == "__main__":
    main(sys.argv[1])
