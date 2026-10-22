# Studio app (React): every screen is live

The redesigned recording studio: one window, a project browser on the left (Module, Lecture, Language) and four mode
tabs on top: **Record, Edit, Script & languages, Export**. Every screen reads and changes the real server and does what
the old page it replaces does: Edit = `/edit?build=`, Record = the presenter page, Script & languages = the review page
`/narration?lecture=&lang=`, Export = the editor's export and the module page's language rows.

    cd video/studio/app
    npm install            # once (react 19.1.0, vite 6.3.5, typescript 5.8.3, all pinned)
    npm run typecheck      # tsc --noEmit
    npm run build          # writes video/studio/static/app/  (gitignored)
    npm run dev            # http://localhost:5173/studio-static/app/ , proxies the server on 127.0.0.1:8080

After `npm run build` the server shows it at `http://127.0.0.1:8080/studio-static/app/index.html` (no restart; through
the tunnel: `http://localhost:8081/studio-static/app/index.html`). Deep links: `#mode=edit&lecture=lecture01&lang=uz&line=14`
(`mode` = record | edit | script | export; `lecture` e.g. `m7_lecture01`; `line` counts from 1 as the editor does).
`studio/run_tests.sh fast` runs typecheck and build; `test_pages` skips `static/app/` (ES modules).

## Layout

    src/styles/tokens.css       colours, 8 px spacing, radii, type scale, fonts: the only place values live
    src/styles/components.css   component styles (class = component name)
    src/styles/shell.css        top bar, project browser, status bar
    src/styles/modes.css        the four modes
    src/api.ts, types.ts        typed GET fetchers and the response shapes
    src/model.ts                line states, sections, edit-list <-> video time, composite levels, long silences
    src/playhead.ts             the playhead as an external store (only Playhead / Timecode / Monitor re-render)
    src/components/             Button IconButton Icon Tabs Chip Panel Meter Track Clip Marker Playhead Timecode
                                Inspector(Section) Toast Waveform(useViewportCanvas, drawEnvelope)
    src/shell/                  TopBar ProjectBrowser StatusBar
    src/modes/                  Edit (+ edit/: ScriptList Monitor Inspector TakeWave Timeline) Record Script Export
    src/snapshot.ts             the module page's counts, copied once (the real app reads them per lecture)

## Tokens

`--bg --panel --panel-2 --raised --line --line-strong` (surfaces), `--text --dim --faint`, one accent `--accent`,
`--record` (red), `--good --warn --bad`, track colours `--track-picture --track-you --track-clone`; spacing
`--sp-1..5` (4, 8, 16, 24, 32), `--hit` 28 px, radii `--r-1..3`, type `--fs-xs..2xl`, `--font` and `--mono` are system
stacks (no web fonts: it runs offline through the ssh tunnel). Focus is a 2 px accent ring (`:focus-visible`).

## Components

Button (default, primary, ghost, danger, record), IconButton (always has a label), Tabs (underline or pills), Chip
(tones good, warn, bad, accent, you, clone, empty), Panel (header + body), Meter (vertical or horizontal, `--level`),
Track (sticky header + wide body), Clip (positioned by the caller in px), Marker (fail, listen, update, silence, line),
Playhead, Timecode (monospace), InspectorSection (collapsible), Toast (`useToast`; `useMock` says what a button would do).

## Where each mode comes from today

| Mode | Replaces | Reads |
|---|---|---|
| Project browser, language switch | `studio()` module page (`/?m=K`), the lecture's language rows | `snapshot.ts` stands in for the page; per-language counts: `GET /api/narration` |
| Top / status bar | editor header: voice server, jobs, last recording | `/api/project` (`voice_server`, `jobs`, `sessions`) |
| Edit | `/edit?build=` (`editor.html`, `static/editor/*.js`) | `/api/project`, `/api/levels?src=` (session and `__original__`), `/api/editor-langs`, the silent video |
| Record | `presenter.py` PAGE + `presenter/takes.js` | `/api/project`, `/api/line`; the real page records through `/upload`, `/api/chunk`, `/api/events`, `/api/finish` |
| Script & languages | `/narration?lecture=&lang=` (`narration.html`, `review.js`) | `/api/narration` (lines, labels, counts, checks, refs) |
| Export | editor header (Export, cleaning, unrecorded lines), module page (Build video, Delete), jobs and exports lists | `/api/project` (`settings`, `jobs`, `exports`), `studio/buildlang.plan` for "Build draft video" |

## Edit mode (live)

`src/api.ts` has a typed POST helper per route of the old editor (same route, parameters and body as `static/editor/*.js`);
`src/actions.ts` wraps them: post, then fetch `/api/project` again; a failure is a toast with the server's message and
changes nothing. While a job, a version or a recording is being made the project is fetched every 2 s, and stops when
idle (`busy` in `model.ts`); the status bar names what is running. `src/player.ts` is `static/editor/player.js` in
TypeScript with the same sync rules (`Player.seekNow`: no re-seek while the element is seeking or buffering; contiguous
pieces of one source never seek). `modes/edit/usePlayer.ts` owns it: the whole edit list, one take (alone or in
context) or a version's scene clip; the playhead store follows the player clock. Keys: Space play / pause, arrows play
the next / previous line, L opens Record on the line. Panel borders (script | monitor | inspector, monitor | timeline)
drag, arrow-key and double-click to reset; sizes are kept in `localStorage` (`studioPanels`). The margin ("keep … s at
line ends") is a timeline-bar field saved through `/api/settings`; recordings are listed, and deleted, in the
inspector's Recordings section. Left out on purpose: "Prepare presenter page" and per-recording `/api/compose`; not
ported from the old page: click on a level strip to play from there, the unrecorded-lines select and cleaning select
(they belong to Export).

## Record mode (live)

The old presenter page (`presenter.py` PAGE + `static/presenter/takes.js`) as components. `src/booth.ts` is its engine:
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
(writes the narration line, then approves it, as review.js does) and still fine post to `/api/narration/{approve,save,fine}`
with `kind=line|label`; the reviews and the language rows are fetched again afterwards, since one approval moves the
other languages' "needs update". Filters: all, needs update, draft, empty, approved. **Uzbek is never voiced or built until
it is approved** (repo-root CLAUDE.md): a banner says so, the Uzbek review says it for each unapproved item, and Build stays
disabled with the server's reason (`studio/buildlang.py` `plan`). "add language" posts `/api/narration/add` (an empty
skeleton, to be drafted by Claude). The language rows with Build video / Build draft video come from
`GET /api/lecture-langs?lecture=` (new, read-only: `review.summary` per language plus the languages that can still be added);
Build posts `/api/narration/build`, and the status bar shows the build job (polled every 2 s while it runs). The project
browser's lecture list is still a snapshot (`snapshot.ts`: there is no API for the module page's lecture list); the open
lecture's rows in it, and the language select, are live.

## Export (live)

Voice cleaning (remembered in `localStorage` `studioClean`, the old editor's key), "lines you have not recorded"
(`/api/settings?key=missing`), Export (`POST /api/export?build&clean=`), the queue (`/api/project` jobs) and the exports
list (each file linked for download, `watch` plays an exported mp4 inline), and "Watch the lecture video": the built video
inline (`/<build>/<build>.mp4`, as `/lecture?build=` shows it). The "your takes vs the cloned voice" summary is
`src/makeup.ts` from `/api/project`; `npm run check` (run by `studio/run_tests.sh fast`) asserts it equals the counts the
server's own fields give. Not placed: "Prepare presenter page" and per-recording `/api/compose` (the module page's
"Build video" of one recording).
