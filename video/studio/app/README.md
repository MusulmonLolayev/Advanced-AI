# Studio app (React): every screen is live

The recording studio: one window and one workspace (no mode tabs): the script list, the monitor (or the recording booth while
**Record** is on) and the timeline. Two buttons in the top bar open the rest: **Script & languages** (a drawer from the right) and
**Export** (a large dialog). The project browser (Module, Lecture, Language) starts as an icon rail. It is the studio's only front end: the old HTML pages (the editor, the
presenter page with its takes panel, the narration review page, the module and lecture pages) are gone, and their addresses
redirect here. Every screen reads and changes the real server and does what the old page it replaced did.

    cd video/studio/app
    npm install            # once (react 19.1.0, vite 6.3.5, typescript 5.8.3, all pinned)
    npm run typecheck      # tsc --noEmit
    npm run build          # writes video/studio/static/app/  (gitignored); the server serves it at /
    npm run check          # the Export numbers and the level strip's plan equal the server's (esbuild + node)
    npm run dev            # http://localhost:5173/ , proxies the server on 127.0.0.1:8080

The server (`serve_presenter.py`, 8080) serves the build at `/` (no restart after a build; `Cache-Control: no-cache` on the
page, the hashed assets cached for good); through the tunnel: **`http://localhost:8081/`**. Deep links:
`/#lecture=m7_lecture01&lang=uz&line=14&rec=1&panel=export&watch=lecture` (`rec=1` the booth is on; `panel` = script | export;
`line` counts from 1; `watch=lecture` or a recording's name plays it inline in the Export dialog). The old `mode=` names still
work: `mode=record` is `rec=1`, `mode=edit` the plain workspace, `mode=script` and `mode=export` the panels. The same names work in
the query (`/?mode=script&lecture=…`), which is what the old addresses redirect to (`serve_presenter.old_route`): `/?m=N`,
`/lecture?build=`, `/edit?build=`, `/watch?build=&name=`, `/narration?lecture=&lang=`, `<build>/presenter/presenter.html`.
The app follows the address when it changes (`hashchange`). `studio/run_tests.sh` builds and checks it, and
`test_app_browser` drives it in headless Chromium.

## Layout

    src/styles/tokens.css       colours, 8 px spacing, radii, type scale, fonts: the only place values live
    src/styles/components.css   component styles (class = component name)
    src/styles/shell.css        top bar, project browser, status bar
    src/styles/modes.css        the workspace, the booth, the Script and Export screens
    src/api.ts, types.ts        typed fetchers (GET) and actions (POST) and the response shapes
    src/actions.ts              every action: post, fetch the project again, toast the server's message on failure
    src/booth.ts, upload.ts     the recording engine and its chunk queue (Record)
    src/player.ts, makeup.ts    the two-track player; the Export summary (check_makeup.ts tests it)
    src/model.ts                line states, sections, edit-list <-> video time, composite levels, long silences
    src/playhead.ts             the playhead as an external store (only Playhead / Timecode / Monitor re-render)
    src/components/             Button IconButton Icon Tabs Chip Panel Meter Track Clip Marker Playhead Timecode
                                InspectorSection ContextMenu PanelDialog Toast Dialog (useDialog().confirm) Waveform(useViewportCanvas, drawEnvelope)
    src/shell/                  TopBar ProjectBrowser StatusBar
    src/modes/                  Workspace (+ edit/: ScriptList Monitor Timeline clipMenu panels TakeWave TakeEditor) BoothPanel Script Export

## Tokens

`--bg --panel --panel-2 --raised --line --line-strong` (surfaces), `--text --dim --faint`, one accent `--accent`,
`--record` (red), `--good --warn --bad`, track colours `--track-picture --track-you --track-clone`; spacing
`--sp-1..5` (4, 8, 16, 24, 32), `--hit` 28 px, radii `--r-1..3`, type `--fs-xs..2xl`, `--font` and `--mono` are system
stacks (no web fonts: it runs offline through the ssh tunnel). Focus is a 2 px accent ring (`:focus-visible`).

## Components

Button (default, primary, ghost, danger, record), IconButton (always has a label), Tabs (underline or pills), Chip
(tones good, warn, bad, accent, you, clone, empty), Panel (header + body), Meter (vertical or horizontal, `--level`),
Track (sticky header + wide body), Clip (positioned by the caller in px), Marker (fail, listen, update, silence, line),
Playhead, Timecode (monospace), InspectorSection (collapsible), Toast (`useToast`).

## Where each screen reads

| Screen | Replaced | Reads |
|---|---|---|
| Project browser, language switch | the module page (`/?m=K`) | `GET /api/lectures` (modules, lectures, languages: counts, build state, shared files) |
| Top / status bar | the editor header: voice server, jobs, last recording | `/api/project` (`voice_server`, `jobs`, `sessions`), `/api/lecture-langs` (build jobs) |
| Edit | `/edit?build=` | `/api/project`, `/api/levels?src=` (session and `__original__`), `/api/editor-langs`, `/api/line`, the silent video |
| Record | the presenter page (`presenter.html`, its takes panel) | `/api/project`, `/api/line`, `<build>/presenter/lines.json`; records through `/api/chunk`, `/api/events`, `/api/finish` |
| Script & languages | `/narration?lecture=&lang=` | `/api/narration` (lines, labels, counts, checks, refs), `/api/lecture-langs` |
| Export | the editor header (Export, cleaning, unrecorded lines), the module page (Build video) | `/api/project` (`settings`, `jobs`, `exports`), `/api/lecture-langs` |

## The workspace (live)

`src/api.ts` has a typed POST helper per route of the old editor (the same routes, parameters and bodies the old editor sent);
`src/actions.ts` wraps them: post, then fetch `/api/project` again; a failure is a toast with the server's message and
changes nothing. While a job, a version or a recording is being made the project is fetched every 2 s, and stops when
idle (`busy` in `model.ts`); the status bar names what is running. `src/player.ts` is the old editor's player in
TypeScript with the same sync rules (`Player.seekNow`: no re-seek while the element is seeking or buffering; contiguous
pieces of one source never seek). `modes/edit/usePlayer.ts` owns it: the whole edit list, one take (alone or in
context) or a version's scene clip; the playhead store follows the player clock. Keys: Space play / pause, arrows play
the next / previous line, L opens Record on the line. Panel borders (script | monitor, monitor | timeline)
drag, arrow-key and double-click to reset; sizes are kept in `localStorage` (`studioPanels`). The margin ("keep … s at
line ends") is a timeline-bar field saved through `/api/settings`; recordings are listed, and deleted, in the
timeline bar's Recordings… dialog. Left out on purpose: "Prepare presenter page" and per-recording `/api/compose`; not
ported from the old page: click on a level strip to play from there, the unrecorded-lines select and cleaning select
(they belong to Export).

Recordings (Recordings… in the timeline bar): each shows its voice profile; one not made with `cloned` has **convert to cloned voice**
(`POST /api/process?build&name&clean=cloned`, "converting…" while its `process` job runs) and a cloned one has **your voice /
cloned voice** buttons that play the whole recording before and after conversion (`audio_alt` and `audio` of `/api/project`;
per recording, not per take). `cloned` is also the default in Export's voice cleaning.

## Keys

One map for the whole studio (Alt, Ctrl and Meta combinations are left to the browser; nothing fires while a field has the focus or a
dialog is open; the buttons show their key only in the tooltip):

| Where | Key | Does |
|---|---|---|
| anywhere | **B** | Record on / off (off while recording asks "Leave and stop recording?") |
| anywhere | **S** | the Script & languages drawer, on / off |
| anywhere | **E** | the Export dialog, on / off |
| drawers, dialogs, menus | Esc | close |
| workspace (Record off) | Space | play / pause the lecture's edit list |
| workspace | → ← | play the next / previous line |
| workspace | **L** | Record turns on and records one take of the selected line, after the count-in |
| workspace | menu key, Shift+F10 | the context menu of the selected clip (↑ ↓ Enter, → opens a submenu, ← / Esc back) |
| booth (Record on) | Space, P | pause / play the line; starts the next line |
| booth | → PgDn / ← PgUp | next line (playing: jump to its end) / back to the line start, then the line before |
| booth | **L** | record one take of this line (stops 1 s after the line, or at → / L) |
| booth | **R** | start / stop recording the session |
| booth | **X** | mistake while recording: the line starts over |
| booth | **T** | show / hide the takes of this line |
| booth | **M** | microphone select |
| booth | **N** | notes (the teleprompter): below / right / hidden |
| booth | **F** | full screen |
| booth | Esc | stop watching a take, cancel the count-in |

B, S and E are the only keys the studio added for the panels; the booth uses Space P → ← PgUp PgDn L R X T M N F Esc and the
workspace Space → ← L, so none of the three clashes with them.

## The booth (Record on; was the Record mode)

The old presenter page as components (it lives on only as the offline copy `presenter.py` writes). `src/booth.ts` is its engine:
the silent video plays line by line (Space, →, ←), the microphone is recorded with `getUserMedia` (same constraints) and
`MediaRecorder` (`audio/webm;codecs=opus`, one piece a second), every moment the picture plays, holds or jumps is logged
with the same event shapes (`play`, `hold`, `line`, `retake`, `stop`), and there are the two modes: R a whole session,
L one take of the line on screen (it stops 1 s after the line, or at → / L). X marks a mistake and starts the line over.
`src/upload.ts` is the chunk queue: `POST /api/chunk?build&name&seq` in order, kept in IndexedDB (same database and keys
as the old page) until the server has it, retried with a growing wait, recovered on the next visit; then
`/api/events` (also every 5 s) and `/api/finish`. A session is named by its start second, `YYYY-MM-DDTHH-MM-SS` (UTC).
New over the old page: a count-in (off, 1, 2, 3, 5 s; default 3; remembered with the microphone in `localStorage`), a
real input meter (AnalyserNode, rms and peak in dBFS, CLIP above -1 dBFS), and the takes panel with the Edit actions
(`use`, `mistake`, `hide`) and the editor's player for `watch` / `in context` on the booth's own video. The prompter
lights words by the narration's chunk times (`<build>/presenter/lines.json`), as the old page does. Leaving Record,
switching lecture or language while recording asks first (and stops and saves the recording); closing the tab warns
while recording or while pieces are unsent; on a page that is not a secure context it shows "Recording needs https or the
ssh tunnel (http://localhost:8081)" instead of the record buttons. Not ported: `N` (notes position) and the offline copy.

## Script & languages (live)

The lines (or labels) × languages grid and the review panel use `GET /api/narration` per language. approve, save edit
(writes the narration line, then approves it, as the old review page did) and still fine post to `/api/narration/{approve,save,fine}`
with `kind=line|label`; the reviews and the language rows are fetched again afterwards, since one approval moves the
other languages' "needs update". Filters: all, needs update, draft, empty, approved. **Uzbek is never voiced or built until
it is approved** (repo-root CLAUDE.md): a banner says so, the Uzbek review says it for each unapproved item, and Build stays
disabled with the server's reason (`studio/buildlang.py` `plan`). "add language" posts `/api/narration/add` (an empty
skeleton, to be drafted by Claude). The language rows with Build video / Build draft video come from
`GET /api/lecture-langs?lecture=` (read-only: `review.summary` per language plus the languages that can still be added);
Build posts `/api/narration/build`, and the status bar shows the build job (polled every 2 s while it runs). The project
browser reads `GET /api/lectures` (`studio/review.py` `lecture_list`: the old module page's facts, without the slow build
plan) and is reloaded after an approval, an added language or a build.

## Export (live)

Voice cleaning (defaults to the profile the lecture's recordings use, "cloned" if any is; not kept in the browser; the exports list shows each file's time and profile; links carry `?v=<mtime>`), "lines you have not recorded"
(`/api/settings?key=missing`), Export (`POST /api/export?build&clean=`), the queue (`/api/project` jobs) and the exports
list (each file linked for download, `watch` plays an exported mp4 inline), and "Watch the lecture video": the built video
inline (`/<build>/<build>.mp4`, as `/lecture?build=` shows it). The "your takes vs the cloned voice" summary is
`src/makeup.ts` from `/api/project`; `npm run check` (run by `studio/run_tests.sh fast`) asserts it equals the counts the
server's own fields give. Not placed: per-recording `/api/compose` (the old module page's "Build video" of one recording; its `Watch` is
`watch=<recording>` in Export). A build with no presenter page shows "Prepare presenter page" in Edit and Record
(`POST /api/prepare`, polled until `lines.json` exists).

## Edit layout

No inspector column: the script list and the monitor (16:9 picture as large as its stage allows, the line's text under it, a one-line strip) sit above the timeline. Takes live on the timeline's YOU lane; a right-click (or the ⋯ button, the menu key, Shift+F10) on a YOU, PICTURE or CLONE clip opens its menu (`edit/clipMenu.ts`), whose "…" items open dialogs (`PanelDialog`, `TakeEditor`) hosting the panels in `edit/panels.tsx`. The project browser starts as the icon rail (`studioBrowser` in localStorage).
