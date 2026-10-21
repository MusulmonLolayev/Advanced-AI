// Versions of a rewritten scene: save a line as a new version, watch it, rewrite it again, merge it or discard it.
// A version is a draft of the whole scene (see studio/versions.py); the lecture changes only when one is merged.
let baseFor = {}, watchLine = 0;     // baseFor: line -> "Scene/vN", the version the narration box grows from
const MAKING = ['queued', 'voicing', 'rendering'];
const sceneVersions = k => (D.versions && D.versions[D.scenes[k]]) || [];
const making = k => sceneVersions(k).some(x => MAKING.includes(x.state));
const vdot = k => sceneVersions(k).some(x => x.state === 'ready') ?
  `<span class="vdot" title="its scene (${esc(D.scenes[k])}) has a version waiting to be merged: open the line"></span>` : '';

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

function versionHtml(k, x, scene){
  const merging = D.jobs.some(j => j.kind === 'merge' && j.key === scene + '/v' + x.n && ['queued', 'running'].includes(j.state));
  const rep = Object.values(x.report || {}), n = x.changed.length;
  const vc = !rep.length ? '' : rep.some(r => !r.ok) ? '<span class="bad">voice check fails</span>'
    : rep.some(r => r.listen) ? '<span class="warn">voice check passes, listen</span>' : 'voice check passes';
  const state = merging ? '<span class="warn">merging…</span>' : {queued: '<span class="warn">waiting…</span>', voicing: '<span class="warn">voicing…</span>',
    rendering: '<span class="warn">rendering…</span>', ready: '<span class="good">ready</span>', failed: '<span class="bad">failed</span>',
    merged: '<span class="dim">merged</span>', stale: '<span class="warn">made before the last merge</span>'}[x.state];
  const when = new Date(x.created * 1000).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', hour12: false});
  const btn = (label, js, tip, quiet = true) => `<button ${quiet ? 'class="quiet"' : ''} onclick="${js}" title="${tip}">${label}</button>`;
  const ready = x.state === 'ready' && !merging;
  return `<div class="ver${x.state === 'stale' || x.state === 'merged' ? ' old' : ''}">
    <div><b>v${x.n}</b> · ${n ? n + ' line' + (n === 1 ? '' : 's') + ' changed' : 'same words, new takes'}${vc ? ' · ' + vc : ''} · ${when} · ${state}
      ${x.base ? `<span class="dim">(grew from v${x.base})</span>` : ''}</div>
    <div class="ctl">${x.video ? btn('▶ watch', `watchVersion('${scene}', ${x.n}, ${k})`, 'the whole scene, from this line, with its own sound', false) : ''}
      ${ready ? btn('rewrite again', `rewriteAgain(${k}, '${scene}', ${x.n})`, 'load this version\'s text of the line into the box; the next version grows from it') : ''}
      ${ready ? btn('merge', `mergeVersion('${scene}', ${x.n})`, 'put it in the lecture', false) : ''}
      ${x.state === 'merged' || ['voicing', 'rendering'].includes(x.state) || merging ? '' : btn('discard', `discardVersion('${scene}', ${x.n})`, 'delete this version')}</div>
    ${x.error ? `<p class="bad">${esc(x.error)}</p>` : ''}
    ${x.changed.map(c => `<div class="vdiff"><span class="dim">line ${+c + 1}</span> ${x.state === 'merged' ? esc(x.texts[c]) : wordDiff(D.lines[+c][1], x.texts[c])}</div>`).join('')}</div>`; }

function narrHtml(k){
  if (!D.editable) return '';
  const vm = D.voice[k], base = baseFor[k], scene = D.scenes[k], vs = sceneVersions(k), busy = making(k);
  return `<div class="narr"><div class="ctl"><label>narration — save a rewrite as a new version of its scene (${esc(scene)}): the ${D.engine === 'navoiy' ? 'cloned' : 'synthetic'} voice says it and the scene is rendered on its own (a few minutes). Watch it, rewrite again, then merge it into the lecture.</label></div>
    ${vm ? `<p class="${vm.ok ? (vm.listen ? 'warn' : 'dim') : 'bad'}">Voice check: ${vm.ok ? (vm.listen ? 'passes, but listen' : 'passes') : 'fails (' + esc(vm.fails.join(', ')) + ')'} · heard: “${esc(vm.heard)}”</p>` : ''}
    <textarea id="nar${k}">${esc(D.lines[k][1])}</textarea>
    <div class="ctl"><button ${busy ? 'disabled' : ''} onclick="saveVersion(${k})" title="${busy ? 'a version of this scene is still being made' : 'the lecture is not changed until you merge'}">save as new version</button>
    ${D.engine === 'navoiy' ? `<button class="quiet" ${busy ? 'disabled' : ''} onclick="revoiceAsIs(${k})" title="same words, new takes; the old clip stays if it scores better">re-voice as is</button>` : ''}
    ${base ? `<span class="warn">grows from ${esc(base.split('/')[1])} <a href="#" onclick="event.preventDefault(); delete baseFor[${k}]; render()">(from the lecture instead)</a></span>` : ''}
    <span class="dim">Uzbek apostrophes are fixed for you (o'n → oʻn). In the bilingual file the English line is left as it was.</span></div>
    ${vs.length ? `<div class="ctl"><label>Versions of ${esc(scene)}</label></div>${vs.slice().reverse().map(x => versionHtml(k, x, scene)).join('')}` : ''}</div>`; }

function currentText(k){            // what the next version would start from for this line
  const b = baseFor[k] && sceneVersions(k).find(x => 'v' + x.n === baseFor[k].split('/')[1]);
  return (b && b.texts[k]) || D.lines[k][1]; }
function newVersion(k, body){
  const q = '/api/version?line=' + k + (baseFor[k] ? '&base=' + encodeURIComponent(baseFor[k]) : '');
  return api(q, body).then(r => { if (r){ delete baseFor[k]; say('queued: a new version of ' + D.scenes[k]); } }); }
function saveVersion(k){
  const text = document.getElementById('nar' + k).value.trim();
  if (text === currentText(k).trim()) return say('the text is unchanged' + (D.engine === 'navoiy' ? ': use “re-voice as is”' : ''));
  newVersion(k, {text}); }
function revoiceAsIs(k){ newVersion(k); }
function rewriteAgain(k, scene, n){
  const x = sceneVersions(k).find(y => y.n === n); if (!x) return;
  baseFor[k] = scene + '/v' + n; document.getElementById('nar' + k).value = x.texts[k] || D.lines[k][1];
  render(); document.getElementById('nar' + k).focus(); }
function mergeVersion(scene, n){
  if (!confirm('Merge v' + n + ' into the lecture? The narration file gets its texts, the scene and the lecture video are replaced (about a minute), and your recordings move to the new timings. The previous video is kept as before_merge.')) return;
  api('/api/version/merge?scene=' + scene + '&n=' + n).then(r => r && say('merging v' + n)); }
function discardVersion(scene, n){
  if (confirm('Discard v' + n + ' of ' + scene + '? Its files are deleted.')) api('/api/version/discard?scene=' + scene + '&n=' + n); }

// ─── watching: the version's whole scene plays in the main video, with its own sound ───
function watchVersion(scene, n, k){
  const x = sceneVersions(k).find(y => y.n === n); if (!x || !x.video) return;
  P.pause(); P.off = true; watchLine = k; v.muted = false; v.playbackRate = 1;
  const at = x.line_starts[k] || 0;
  v.addEventListener('loadedmetadata', () => { v.currentTime = at; v.play().catch(() => {}); }, {once: true});
  v.src = x.video;
  document.getElementById('mode').textContent = 'v' + n + ' of ' + scene;
  document.getElementById('back').style.display = '';
  document.getElementById('nowline').textContent = 'Watching v' + n + ' of ' + scene + ': the whole scene, from line ' + (k + 1) + ', with its own sound.';
  document.getElementById('tl').querySelectorAll('.seg').forEach(s => s.remove()); }
function leaveVersion(){          // loadAll() calls this: the edit-list player takes the video element back
  P.off = false; v.pause(); v.muted = true; v.src = D.video + '?v=' + D.video_version;
  document.getElementById('back').style.display = 'none'; document.getElementById('mode').textContent = 'whole lecture'; }
function backToLecture(){ loadAll(lineStart(watchLine)); }
