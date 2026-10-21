"""Drives the presenter page in headless Chromium with a fake microphone (run by test_presenter_browser.py, with the
system Python that has Playwright): the takes panel opens at #line=2; ← goes to the line's start and then to the line
before, → plays the line; X outside a recording says what it does, and inside one logs a retake; L records one take
that stops by itself 1 s after the line, finishes its session and shows the take; a second L adds another; ▶ watch
plays a take on the page's own video, alone and with its neighbours; "use this one" changes the used take; mistake and
delete change the list.

    python3 studio/presenter_browser_check.py <server url> <build> <chrome> [screenshot dir]
"""
import glob
import json
import sys
import time
import unittest
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = (glob.glob(str(Path.home() / ".cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"))
          or glob.glob(str(Path.home() / ".cache/ms-playwright/chromium-*/chrome-linux/chrome")) or [None])[-1]


HEARD = """(() => { window.__heard = []; window.__aseeks = [];
  const d = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'currentTime');
  Object.defineProperty(HTMLMediaElement.prototype, 'currentTime', {configurable: true, get(){ return d.get.call(this); },
    set(x){ if (this.tagName === 'AUDIO') window.__aseeks.push(performance.now()); d.set.call(this, x); }});
  const sync = Player.prototype.sync;
  Player.prototype.sync = function(f){ const r = sync.call(this, f), c = this.cur;
    if (this.playing && c && !c.paused && !c.seeking && c.readyState >= 3) window.__heard.push([performance.now(), c.src, c.currentTime]);
    return r; }; })()"""


def backsteps(heard, seeks):
    """([(wall ms, from, to) where the voice heard moved back by more than 20 ms with no seek in between], number of seeks)."""
    back, prev = [], None
    for t, src, ct in heard:
        if prev and prev[1] == src and ct < prev[2] - 0.02 and not any(prev[0] < s <= t for s in seeks):
            back.append((t, prev[2], ct))
        prev = (t, src, ct)
    return back, len(seeks)


def check(url, B, chrome, shots=None):
    """Drive the presenter page at `url` (a server holding the fixture lecture `B`); raises on the first thing that is wrong."""
    pw = sync_playwright().start()
    browser = pw.chromium.launch(executable_path=chrome, args=[
        "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream", "--autoplay-policy=no-user-gesture-required"])
    page = browser.new_page(viewport={"width": 1366, "height": 768}, permissions=["microphone"])
    tc = unittest.TestCase()
    fail = tc.fail
    get = lambda path: json.loads(urllib.request.urlopen(url + path, timeout=30).read())      # noqa: E731
    line = lambda k: get(f"/api/line?build={B}&line={k}")                                       # noqa: E731

    def until(test, what, timeout=60):
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = test()
            if r:
                return r
            time.sleep(0.25)
        fail(f"timed out waiting for {what}")

    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("dialog", lambda d: d.accept())
    ev = lambda js: page.evaluate(js)                                                      # noqa: E731
    page.goto(f"{url}/{B}/presenter/presenter.html#line=2")
    page.wait_for_function("document.getElementById('v').readyState >= 3")

    # #line=2 opens the panel at line 2 (index 1); nothing recorded yet
    page.wait_for_selector("#takes.open .tkhead")
    tc.assertIn("line 2 / 4", page.inner_text("#takes .tkhead"))
    page.wait_for_function("document.getElementById('tklist').innerText.includes('No take of this line yet')")
    tc.assertEqual(ev("i"), 1)
    tc.assertAlmostEqual(ev("v.currentTime"), 3.0, delta=0.1)

    # X without a recording says what it does
    page.keyboard.press("x")
    msg = page.inner_text("#msg")
    tc.assertEqual(msg, "X marks a mistake while recording. Press R to record, or L to record a take of just this line.")
    tc.assertIn("T takes of this line", page.inner_text("#bar"))
    tc.assertIn("L record a take of this line", page.inner_text("#bar"))

    # → plays the line; ← goes to its start, and again to the line before
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!document.getElementById('v').paused && document.getElementById('v').currentTime > 3.3")
    tc.assertEqual(ev("i"), 1)
    page.keyboard.press("ArrowLeft")
    tc.assertEqual((ev("i"), ev("v.paused")), (1, True))
    tc.assertAlmostEqual(ev("v.currentTime"), 3.0, delta=0.05)
    page.keyboard.press("ArrowLeft")
    tc.assertEqual(ev("i"), 0)
    tc.assertAlmostEqual(ev("v.currentTime"), 0.0, delta=0.05)
    page.wait_for_function("document.querySelector('#takes .tkhead')?.innerText.includes('line 1 / 4')")     # the panel follows
    page.keyboard.press("ArrowRight")                                                                  # line 1 plays
    page.wait_for_function("!document.getElementById('v').paused")
    tc.assertEqual(ev("i"), 0)
    page.wait_for_function("document.getElementById('v').currentTime > 0.4")                           # a human's pace, not a burst of keys
    page.keyboard.press("ArrowRight")                                                                  # pressed while playing: its end
    tc.assertTrue(ev("v.paused"))
    page.wait_for_timeout(300)
    page.keyboard.press("ArrowRight")                                                                  # line 2 plays
    page.wait_for_function("i === 1 && !document.getElementById('v').paused && document.getElementById('v').currentTime > 3.3")
    page.keyboard.press("ArrowLeft")                                                                   # back to line 2's start
    tc.assertEqual((ev("i"), ev("v.paused")), (1, True))
    tc.assertAlmostEqual(ev("v.currentTime"), 3.0, delta=0.05)
    page.wait_for_function("document.querySelector('#takes .tkhead')?.innerText.includes('line 2 / 4')")

    # X during a recording logs a retake (R records the whole run, as before)
    page.keyboard.press("r")
    page.wait_for_function("document.body.classList.contains('recording')")
    tc.assertFalse(page.is_visible("#takes"))                      # the drawer is gone while recording: the video has the room
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!document.getElementById('v').paused")
    page.wait_for_timeout(600)
    page.keyboard.press("x")
    tc.assertTrue(ev("ev.some(e => e[1] === 'retake' && e[4] === 1)"))
    tc.assertTrue(ev("ev.some(e => e[1] === 'line' && e[4] === 1)"))
    page.keyboard.press("ArrowRight")                                                                  # the line again, to its end
    page.wait_for_function("!document.getElementById('v').paused")
    page.wait_for_function("document.getElementById('v').paused && stopAt === null", timeout=15000)
    page.keyboard.press("r")                                                                           # stop
    page.wait_for_function("!rec")
    first = until(lambda: next((s for s in line(1)["sessions"] if s["state"] == "ready"), None), "session 1 processed")
    d = line(1)
    tc.assertEqual([t["rejected"] for t in d["takes"]], [True, False])
    page.wait_for_function("document.querySelectorAll('#takes .tk[data-take]').length === 2")
    tc.assertEqual(page.locator("#takes .tk.bad").count(), 1)                                        # the mistake is struck through

    # L: one take of this line; it stops 1 s after the line's end, and finishes the session
    t0 = time.time()
    page.keyboard.press("l")
    page.wait_for_function("document.body.classList.contains('single')")
    tc.assertIn("recording take of line 2", page.inner_text("#onetake"))
    tc.assertIn("→ or L to stop", page.inner_text("#onetake"))
    tc.assertFalse(page.is_visible("#takes"))
    page.wait_for_function("!document.body.classList.contains('recording')", timeout=20000)
    took = time.time() - t0
    tc.assertGreater(took, 3.3 + 1.0 - 0.5)                         # the 3 s line at 1/1.1 speed, then 1 s
    tc.assertLess(took, 3.3 + 1.0 + 3.0)
    page.wait_for_selector("#takes.open")
    until(lambda: len(line(1)["takes"]) == 3, "the new take")
    page.wait_for_function("document.querySelectorAll('#takes .tk[data-take]').length === 3")
    d = line(1)
    tc.assertEqual(d["chosen"], d["takes"][-1]["id"])                # the newest that is not a mistake is used
    tc.assertIn("used in your edit", page.locator("#takes .tk[data-take]").nth(2).inner_text())
    tc.assertEqual(get(f"/api/counts?build={B}")["1"], 2)

    # L again, stopped by → before the line is over; both takes are kept
    page.keyboard.press("l")
    page.wait_for_function("document.body.classList.contains('single')")
    page.wait_for_timeout(1000)
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!document.body.classList.contains('recording')", timeout=10000)
    until(lambda: len(line(1)["takes"]) == 4, "the second new take")
    page.wait_for_function("document.querySelectorAll('#takes .tk[data-take]').length === 4")
    d = line(1)
    newest, middle = d["takes"][3]["id"], d["takes"][2]["id"]
    tc.assertEqual(d["chosen"], newest)
    tc.assertEqual(len({t["session"] for t in d["takes"]}), 3)       # three sessions, takes of the same line
    tc.assertEqual(page.locator("#takes canvas.lvc").count(), 4)

    # ▶ watch plays a take on the page's video, with nothing logged; "in context" plays the joins too
    before_events = ev("ev.length")
    row = page.locator(f'#takes .tk[data-take="{middle}"]')
    row.locator('button[data-act="watch"]').click()
    page.wait_for_function("watching === true")
    page.wait_for_function("!document.getElementById('v').paused")
    page.wait_for_timeout(300)                                       # the player's first seek lands (the page sat elsewhere)
    c0 = ev("v.currentTime")
    page.wait_for_timeout(700)
    tc.assertGreater(ev("v.currentTime"), c0 + 0.2)
    tc.assertIn("/", page.inner_text("#takes .tk.watching .tkclock"))
    tc.assertEqual(ev("ev.length"), before_events)
    page.keyboard.press("Escape")
    tc.assertEqual((ev("watching"), ev("v.paused")), (False, True))
    tc.assertAlmostEqual(ev("v.currentTime"), 3.0, delta=0.05)         # back at the line's start
    cdp = page.context.new_cdp_session(page)                           # a slow link (1 Mbps, 100 ms), nothing cached
    cdp.send("Network.enable")
    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 300, "downloadThroughput": 6000, "uploadThroughput": 6000})
    ev(HEARD)                                                          # log the voice actually heard, and every seek of it
    row.locator('button[data-act="ctx"]').click()
    page.wait_for_function("watching === true")
    tc.assertIn("end of the line before", page.inner_text("#takes .tk.watching .tkclock"))
    page.wait_for_function("document.querySelector('#takes .tk.watching .tkclock')?.innerText.startsWith('this take')", timeout=10000)
    page.wait_for_function("document.querySelector('#takes .tk.watching .tkclock')?.innerText.startsWith('start of the line after')", timeout=15000)
    page.wait_for_function("watching === false", timeout=15000)          # played to its end by itself
    tc.assertTrue(ev("v.paused"))
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
    back, seeks = backsteps(ev("window.__heard"), ev("window.__aseeks"))
    tc.assertEqual(back, [], "the voice heard went backwards (a fragment repeated)")
    tc.assertLessEqual(seeks, 6, "the voice was re-seeked over and over")
    # a stopped watch with L pressed: no recording while one is playing is not possible, the other way round is refused
    row.locator('button[data-act="watch"]').click()
    page.wait_for_function("watching === true")
    page.keyboard.press("l")                                              # L ends the watch, then records
    page.wait_for_function("watching === false && document.body.classList.contains('single')")
    page.keyboard.press("l")                                              # stop that take at once
    page.wait_for_function("!document.body.classList.contains('recording')", timeout=10000)
    until(lambda: len(line(1)["takes"]) == 5, "the fifth take")
    page.wait_for_function("document.querySelectorAll('#takes .tk[data-take]').length === 5")
    newest = line(1)["takes"][4]["id"]

    # use this one changes the used take
    tc.assertEqual(line(1)["chosen"], newest)
    row = page.locator(f'#takes .tk[data-take="{middle}"]')
    row.locator('button[data-act="use"]').click()
    until(lambda: line(1)["chosen"] == middle, "the choice")
    page.wait_for_function(f"document.querySelector('#takes .tk.used').dataset.take === {json.dumps(middle)}")
    tc.assertEqual(line(1)["picked"], middle)

    # mistake / not a mistake, the end controls, delete
    row = page.locator(f'#takes .tk[data-take="{newest}"]')
    row.locator('button[data-act="mistake"]').click()
    until(lambda: next(t for t in line(1)["takes"] if t["id"] == newest)["rejected"], "the mistake")
    page.wait_for_function(f"document.querySelector('.tk[data-take={json.dumps(newest)}]').classList.contains('bad')")
    page.locator(f'#takes .tk[data-take="{newest}"] button[data-act="mistake"]').click()
    until(lambda: not next(t for t in line(1)["takes"] if t["id"] == newest)["rejected"], "not a mistake")
    t = next(t for t in line(1)["takes"] if t["id"] == middle)
    if abs(t["fit"][1] - (t["edit"].get("trim_out") or 0)) > 1e-3:
        page.locator(f'#takes .tk[data-take="{middle}"] button[data-act="fit-end"]').click()
        until(lambda: next(t for t in line(1)["takes"] if t["id"] == middle)["edit"].get("trim_out"), "fit end")
    if shots:
        page.evaluate("document.getElementById('takes').scrollTop = 0")
        page.wait_for_timeout(800)
        page.screenshot(path=str(Path(shots) / "presenter_takes_two.png"))
    page.locator(f'#takes .tk[data-take="{newest}"] button[data-act="del"]').click()
    until(lambda: newest not in [t["id"] for t in line(1)["takes"]], "delete")
    page.wait_for_function("document.querySelectorAll('#takes .tk[data-take]').length === 4")
    tc.assertEqual(line(1)["chosen"], middle)                      # still the one picked

    # T closes and opens the panel; moving to another line follows it
    page.keyboard.press("t")
    tc.assertFalse(page.is_visible("#takes"))
    page.keyboard.press("t")
    tc.assertTrue(page.is_visible("#takes"))
    page.keyboard.press("ArrowLeft")
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("document.querySelector('#takes .tkhead')?.innerText.includes('line 1 / 4')")
    page.wait_for_function("document.getElementById('tklist').innerText.includes('No take of this line yet')")
    tc.assertEqual(errors, [])
    page.close()

    # the editor, which shares the player and the level strip, still plays and draws
    ed = browser.new_page(viewport={"width": 1366, "height": 768})
    ed.on("pageerror", lambda e: errors.append(str(e)))
    ed.goto(f"{url}/edit?build={B}")
    ed.wait_for_selector(".row")
    ed.wait_for_function("D && P.total > 0")
    ed.keyboard.press("ArrowRight")                                    # the editor's → plays the next line
    ed.wait_for_function("P.playing && P.T > 0.5")
    ed.keyboard.press(" ")
    tc.assertFalse(ed.evaluate("P.playing"))
    ed.click("#row1 .head")
    ed.wait_for_selector("#row1 canvas.lvc")
    ed.wait_for_function("(() => { const c = document.querySelector('#row1 canvas.lvc'); return c && c.width > 0 && !!LV.cache[takeById(c.dataset.take).session]; })()")
    ed.locator("#row1 button", has_text="play this take").first.click()
    ed.wait_for_function("P.playing && document.getElementById('mode').textContent.startsWith('take ')")
    tc.assertEqual(errors, [])
    browser.close()
    pw.stop()


if __name__ == "__main__":
    check(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else CHROME,
          sys.argv[4] if len(sys.argv) > 4 else None)
    print("presenter page: ok")
