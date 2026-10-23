"""The browser half of test_app_browser.py, run in the system Python (the one with Playwright; the project's venv has none):
the React app driven in headless Chromium with a fake microphone against a scratch server. See test_app_browser.py.

    python3 studio/app_browser_check.py <server url> <build> <lecture stem> <narration dir> <chrome> [screenshot dir]
"""
import difflib
import json
import re
import sys
import time
import unittest
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

URL, B, STEM, NAR, CHROME = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]), sys.argv[5]
SHOTS = Path(sys.argv[6]) if len(sys.argv) > 6 else None
del sys.argv[2:]                                                             # the rest is for unittest, not for us


class App(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url, cls.nar = URL, NAR
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=CHROME, args=[
            "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream", "--autoplay-policy=no-user-gesture-required"])
        cls.ctx = cls.browser.new_context(viewport={"width": 1920, "height": 1080}, permissions=["microphone"])
        cls.page = cls.ctx.new_page()
        cls.errors, cls.reqs, cls.dialogs = [], [], []
        cls.page.on("console", lambda m: cls.errors.append(m.text) if m.type == "error" else None)
        cls.page.on("pageerror", lambda e: cls.errors.append(str(e)))
        cls.page.on("request", lambda r: cls.reqs.append((r.method, r.url, r.post_data if ("/api/events" in r.url or "/api/edit" in r.url) else None)) if r.method == "POST" else None)
        # no native dialog may appear any more: the app asks with its own <dialog class="dialog">
        cls.page.on("dialog", lambda d: (cls.dialogs.append(d.message), d.dismiss()))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    # ─── helpers ───
    def shot(self, name):
        if SHOTS:
            self.page.screenshot(path=str(SHOTS / f"{name}_1920.png"))
            self.page.set_viewport_size({"width": 1366, "height": 768})
            self.page.wait_for_timeout(500)
            self.page.screenshot(path=str(SHOTS / f"{name}_1366.png"))
            self.page.set_viewport_size({"width": 1920, "height": 1080})

    def get(self, path):
        return json.load(urllib.request.urlopen(self.url + path, timeout=30))

    def project(self):
        return self.get(f"/api/project?build={B}")

    def wait(self, test, what, timeout=60):
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = test()
            if r:
                return r
            time.sleep(0.25)
        self.fail(f"timed out waiting for {what}")

    def open(self, mode, line=1, lang="en"):
        """Load the app at a deep link (a reload: the address is read at start and followed after)."""
        self.page.goto(f"{self.url}/#mode={mode}&lecture={STEM}&lang={lang}&line={line}")
        self.page.reload()

    def ask(self, button=None, key=None):
        """The in-app dialog: wait for it, return its title, then press a button (by its label) or a key."""
        d = self.page.locator("dialog.dialog[open]")
        d.wait_for(timeout=6000)
        title = d.locator(".dialog-title").inner_text()
        if button:
            d.get_by_role("button", name=button, exact=True).click()
        if key:
            self.page.keyboard.press(key)
        d.wait_for(state="detached", timeout=6000)
        return title

    def posts(self, part):
        return [r for r in self.reqs if part in r[1]]

    def shape(self, ev):
        """The event kinds (and line indexes) without times; a hold/play pair under 50 ms after playing began is the browser's
        'waiting' blip, not an action."""
        out = []
        for n, e in enumerate(ev):
            if e[1] == "play" and out and out[-1][0] == "hold" and ev[n - 1][0] and e[0] - ev[n - 1][0] < 0.05 and any(x[0] == "play" for x in out):
                out.pop()
                continue
            out.append([e[1]] + e[4:])
        return out

    # ─── 1 ───
    def test_1_the_front_door_and_the_address(self):
        p = self.page
        p.goto(self.url + "/")
        p.wait_for_selector(".browser .tree-row.lec")                            # the project browser is live (/api/lectures)
        self.assertIn("Lecture 99", p.inner_text(".browser"))
        p.goto(f"{self.url}/edit?build={B}")                                      # an old address: redirected to its screen
        p.wait_for_selector(".edit")
        self.assertRegex(p.evaluate("location.hash"), rf"mode=edit&lecture={STEM}&lang=en")
        p.evaluate(f"location.hash = '#mode=script&lecture={STEM}&lang=en'")         # the address changes under the app: it follows
        p.wait_for_selector(".mgrid .mg-row")
        p.evaluate(f"location.hash = '#mode=record&lecture={STEM}&lang=en&line=2'")
        p.wait_for_selector(".booth video")
        self.assertIn("line 2 /", p.inner_text(".prompter-bar"))

    # ─── 2 ───
    def test_2_record_a_take_and_a_session(self):
        p = self.page
        self.open("record", line=2)
        p.wait_for_selector('.input-panel .chip:has-text("live")', timeout=15000)
        vals = []                                                                  # the fake microphone beeps now and then
        for _ in range(60):
            t = p.inner_text("[data-testid=db]")
            vals.append(-100.0 if t.startswith("—") else float(re.match(r"(-?\d+)", t).group(1)))
            if max(vals) > -60 and min(vals) == -100.0:
                break
            p.wait_for_timeout(250)
        self.assertGreater(max(vals), -60)
        self.assertLess(min(vals), -90)
        p.select_option("#cin", "1")
        self.reqs.clear()
        p.keyboard.press("l")                                                      # one take of line 2
        p.wait_for_selector(".rec-badge", timeout=6000)
        p.wait_for_timeout(3000)
        p.keyboard.press("l")
        p.wait_for_selector(".rec-badge", state="detached", timeout=8000)
        p.wait_for_timeout(1500)
        chunks = self.posts("/api/chunk")
        seqs = [int(re.search(r"seq=(\d+)", r[1]).group(1)) for r in chunks]
        self.assertEqual(seqs, list(range(len(seqs))))
        self.assertGreaterEqual(len(seqs), 3)
        name = re.search(r"name=([^&]+)", chunks[0][1]).group(1)
        self.assertRegex(name, r"^\d{4}-\d\d-\d\dT\d\d-\d\d-\d\d$")
        order = [("chunk" if "/api/chunk" in r[1] else "events" if "/api/events" in r[1] else "finish") for r in self.reqs if "/api/" in r[1]]
        self.assertEqual(order[-2:], ["events", "finish"])
        ev = json.loads(self.posts("/api/events")[-1][2])
        self.assertEqual(self.shape(ev), [["hold"], ["line", 1], ["hold"], ["play"], ["hold"], ["stop"]])
        self.wait(lambda: any(s["name"] == name and s["state"] == "ready" for s in self.project()["sessions"]), "the session to be processed")
        p.wait_for_selector(".takes-panel .strip-take[data-take]", timeout=15000)
        self.assertEqual(len(self.project()["takes"]["1"]), 1)
        # a whole session: R, Space (plays the line), X (a mistake), R
        self.reqs.clear()
        p.keyboard.press("r")
        p.wait_for_selector(".rec-badge", timeout=6000)
        p.keyboard.press("Space")
        p.wait_for_timeout(2500)
        p.keyboard.press("x")
        p.wait_for_timeout(3000)
        p.keyboard.press("r")
        p.wait_for_selector(".rec-badge", state="detached", timeout=8000)
        p.wait_for_timeout(1500)
        ev = json.loads(self.posts("/api/events")[-1][2])
        self.assertEqual(self.shape(ev), [["hold"], ["line", 2], ["hold"], ["play"], ["retake", 2], ["hold"], ["hold"], ["stop"]])
        self.assertEqual(len(self.posts("/api/finish")), 1)
        # leaving the booth while recording asks first, then stops and saves it
        p.keyboard.press("r")
        p.wait_for_selector(".rec-badge", timeout=6000)
        p.wait_for_timeout(1500)
        n_finish = len(self.posts("/api/finish"))
        p.keyboard.press("2")
        d = p.locator("dialog.dialog[open]")
        d.wait_for(timeout=6000)
        self.assertEqual(d.locator(".dialog-title").inner_text(), "Leave and stop recording?")
        self.assertEqual(p.evaluate("document.activeElement.textContent"), "Leave")   # focus on the confirm button
        p.keyboard.press("Escape")                                                  # Esc cancels: still in the booth, still recording
        d.wait_for(state="detached", timeout=6000)
        p.wait_for_timeout(800)
        self.assertEqual(p.locator(".edit").count(), 0)
        self.assertEqual(p.locator(".rec-badge").count(), 1)
        self.assertEqual(len(self.posts("/api/finish")), n_finish)
        p.keyboard.press("2")
        self.assertEqual(self.ask(button="Leave"), "Leave and stop recording?")
        p.wait_for_selector(".edit", timeout=8000)
        self.assertEqual(self.dialogs, [])
        self.wait(lambda: len(self.project()["sessions"]) == 3 and all(s["state"] == "ready" for s in self.project()["sessions"]), "three sessions")

    def cut_a_part_by_hand(self):
        """Part of test 3 (it needs the take test 3 later deletes with its recording): drag, Delete, drawn and shorter, restore."""
        p = self.page
        p.set_viewport_size({"width": 1366, "height": 768})                                   # the size the instructor works at
        p.wait_for_selector(".take .takewave")
        p.locator(".take .takewave").first.scroll_into_view_if_needed()
        p.wait_for_timeout(300)
        tid = p.locator(".take").first.get_attribute("data-take")
        take = p.locator(".take").first
        self.assertIn("Drag on the wave to select a part, then ✂ or Delete to cut it.", p.inner_text(".inspector"))
        row = lambda: next(t for ts in self.project()["takes"].values() for t in ts if t["id"] == tid)
        shown = lambda: float(take.locator(".take-head .mono").first.inner_text().replace(" s", ""))
        wave = take.locator(".takewave")
        box = wave.bounding_box()
        y = box["y"] + box["height"] / 2
        at = lambda f: box["x"] + box["width"] * f

        def drag(f0, f1):
            nonlocal box, y                                                                 # a selection scrolls its card into view: measure again
            box = wave.bounding_box()
            y = box["y"] + box["height"] / 2
            p.mouse.move(at(f0), y)
            p.mouse.down()
            p.mouse.move(at((f0 + f1) / 2), y, steps=4)
            p.mouse.move(at(f1), y, steps=4)
            p.mouse.up()

        before = row()
        self.assertEqual(before["edit"].get("cuts", []), [])
        len0 = before["length"]
        self.assertAlmostEqual(shown(), len0, delta=0.06)
        self.reqs.clear()
        # a click without a drag keeps playing from there and selects nothing
        p.mouse.click(at(0.5), y)
        p.wait_for_timeout(500)
        self.assertEqual(take.locator(".wave-sel").count(), 0)
        self.assertIn("YOUR VOICE", p.inner_text(".screen-tag"))
        p.click("button:has-text('back to the lecture')")
        # a drag shorter than 0.05 s selects nothing
        tiny = 0.04 / before["raw_length"]
        drag(0.4, 0.4 + tiny * 0.9)
        self.assertEqual(take.locator(".wave-sel").count(), 0)
        # a real drag: the span shows with its length and the bar offers play / cut / clear; Esc clears; the trim handles still work
        drag(0.3, 0.6)
        take.locator(".wave-sel").wait_for(timeout=3000)
        bar = take.locator('[data-bar=selection]')
        for name in ("play selection", "cut this part", "clear selection"):
            self.assertEqual(bar.get_by_role("button", name=re.compile(name)).count(), 1, name)
        self.assertEqual(self.posts("/api/edit"), [])
        p.keyboard.press("Escape")
        self.assertEqual(take.locator(".wave-sel").count(), 0)
        drag(0.3, 0.6)
        take.locator(".wave-sel").wait_for(timeout=3000)
        cutbtn = take.get_by_role("button", name="cut this part")
        sb, wb = take.locator(".wave-sel").bounding_box(), wave.bounding_box()
        a = (sb["x"] - wb["x"]) / wb["width"] * before["raw_length"]
        b = a + float(re.search(r"cut (\d+\.\d+) s", cutbtn.inner_text()).group(1))
        self.assertAlmostEqual(b - a, 0.3 * before["raw_length"], delta=0.1)
        self.assertAlmostEqual(a, 0.3 * before["raw_length"], delta=0.15)
        self.assertTrue(self.uncovered(cutbtn), "the cut button is inside the 1366x768 viewport and nothing covers it")
        if SHOTS:
            p.screenshot(path=str(SHOTS / "cut_floating.png"))
        # Delete cuts it: one POST /api/edit with the cut in the take's own seconds
        p.keyboard.press("Delete")
        edits = self.wait(lambda: self.posts("/api/edit"), "the cut to be posted")
        self.assertEqual(len(edits), 1)
        body = json.loads(edits[0][2])
        self.assertEqual(set(body), {"cuts"})
        self.assertEqual(len(body["cuts"]), 1)
        ca, cb = body["cuts"][0]
        self.assertAlmostEqual(cb - ca, b - a, delta=0.0051)                                # the length the button showed
        self.assertAlmostEqual(ca, a, delta=0.12)
        self.assertAlmostEqual(ca * 100, round(ca * 100), places=6)                         # on the 0.01 s grid
        # after the refetch: the cut is drawn, the line under the wave says so, and the take is shorter by the cut
        take.locator(".cut-hand").wait_for(timeout=8000)
        self.assertEqual(take.locator(".cut-hand").count(), 1)
        self.assertIn("1 part cut", take.locator("[data-bar=cuts]").inner_text())
        self.wait(lambda: abs(row()["length"] - (len0 - (cb - ca))) <= 0.02, "the take to be shorter by the cut")
        self.assertEqual(row()["edit"]["cuts"], [[ca, cb]])
        self.wait(lambda: abs(shown() - row()["length"]) <= 0.06, "the displayed length to follow")
        self.assertEqual(take.locator(".wave-sel").count(), 0)
        # a second selection next to the cut (for the picture), then Esc
        drag(0.75, 0.9)
        take.locator(".wave-sel").wait_for(timeout=3000)
        if SHOTS:
            take.screenshot(path=str(SHOTS / "take_cut.png"))
        p.keyboard.press("Escape")
        # click the cut -> restore: the cuts are empty again and the take is back to its length
        self.reqs.clear()
        take.locator(".cut-hand").click()
        take.locator("[data-bar=cut]").get_by_role("button", name="restore", exact=True).click()
        edits = self.wait(lambda: self.posts("/api/edit"), "the restore to be posted")
        self.assertEqual(json.loads(edits[-1][2]), {"cuts": []})
        self.wait(lambda: row()["edit"].get("cuts", []) == [] and abs(row()["length"] - len0) <= 0.02, "the take to be whole again")
        self.wait(lambda: take.locator(".cut-hand").count() == 0, "the cut to disappear from the wave")
        self.cut_in_the_wide_editor(take, row, len0)
        p.set_viewport_size({"width": 1920, "height": 1080})

    def uncovered(self, loc):
        """The element is wholly inside the viewport and is what the pointer would hit at its centre."""
        return loc.evaluate("""el => {
            const r = el.getBoundingClientRect()
            if (r.left < 0 || r.top < 0 || r.right > innerWidth || r.bottom > innerHeight) return false
            const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)
            return !!hit && (el === hit || el.contains(hit))
        }""")

    def cut_in_the_wide_editor(self, take, row, len0):
        """"edit parts" opens the big editor: a wide wave, zoom, the same select / Delete / restore, and the cuts list."""
        p = self.page
        small = take.locator(".takewave").bounding_box()["width"]
        # one trim button, not three: "trim silence" (tooltip says what it does) and "undo trims"; no "fit start / end / both"
        self.assertEqual(take.get_by_role("button", name="trim silence").count(), 1)
        self.assertIn("first and last word, keeping", take.get_by_role("button", name="trim silence").get_attribute("title"))
        self.assertEqual(take.get_by_role("button", name=re.compile("^fit ")).count(), 0)
        self.assertEqual(take.get_by_role("button", name="undo trims").count(), 1)
        self.assertEqual(take.get_by_text("line ends").count(), 0)
        take.get_by_role("button", name="edit parts").click()
        d = p.locator("dialog.take-editor[open]")
        d.wait_for(timeout=6000)
        self.assertEqual(d.get_by_role("button", name="trim silence").count(), 1)
        self.assertEqual(d.get_by_role("button", name="undo trims").count(), 1)
        wave = d.locator(".takewave")
        wb = wave.bounding_box()
        self.assertGreater(wb["width"], max(2.5 * small, 900))
        y = wb["y"] + wb["height"] / 2
        at = lambda f: wb["x"] + wb["width"] * f
        loaded = lambda: [[round(x[0], 2), x[1], None if x[2] is None else round(x[2], 2)] for x in json.loads(d.get_attribute("data-loaded-voice"))]
        saved_voice = lambda: [[round(x[0], 2), x[1], None if x[2] is None else round(x[2], 2)] for x in row()["tracks"]["voice"]]
        # play, then trim the start by about a second: the player follows the take's new tracks, and playing again plays the new take
        d.get_by_role("button", name="play", exact=True).click()
        p.wait_for_timeout(500)
        self.wait(lambda: loaded() == saved_voice(), "the player to hold the take's tracks")
        old_voice = saved_voice()
        self.reqs.clear()
        hb = d.locator(".trim-handle.in").bounding_box()
        self.assertGreaterEqual(hb["width"], 10)
        self.assertIn("start", d.locator(".trim-handle.in").inner_text())
        self.assertIn("end", d.locator(".trim-handle.out").inner_text())
        hy = hb["y"] + hb["height"] / 2
        p.mouse.move(hb["x"] + hb["width"] / 2, hy)
        p.mouse.down()
        p.mouse.move(hb["x"] + hb["width"] / 2 + wb["width"] * 0.3 / 2, hy, steps=4)
        p.mouse.move(hb["x"] + hb["width"] / 2 + wb["width"] * 0.3, hy, steps=4)
        self.assertRegex(d.locator(".trim-handle.in").inner_text(), r"start \d+\.\d+ s")       # its time while dragging
        p.mouse.up()
        p.wait_for_timeout(1500)
        edits = self.wait(lambda: self.posts("/api/edit"), "the trim to be posted")
        body = json.loads(edits[-1][2])
        self.assertEqual(set(body), {"trim_in"})
        trim = body["trim_in"]
        self.assertGreater(trim, 0.5)
        d.locator('[data-save=saved]').wait_for(timeout=8000)
        self.assertIn("✓ saved", d.locator(".te-save").inner_text())
        self.wait(lambda: row()["edit"].get("trim_in") == trim, "the trim to be saved")
        self.wait(lambda: loaded() == saved_voice() and saved_voice() != old_voice, "the player to load the trimmed take")
        if d.get_by_role("button", name="pause", exact=True).count():                             # still playing: pause, then play again
            d.get_by_role("button", name="pause", exact=True).click()
        d.get_by_role("button", name="play", exact=True).click()
        p.wait_for_timeout(400)
        self.assertEqual(loaded(), saved_voice())
        self.assertGreaterEqual(min(x[2] for x in loaded() if x[1] is not None), trim - 0.02)    # nothing before the trim is played
        if d.get_by_role("button", name="pause", exact=True).count():
            d.get_by_role("button", name="pause", exact=True).click()
        hb = d.locator(".trim-handle.in").bounding_box()                                            # put the start back
        p.mouse.move(hb["x"] + hb["width"] / 2, hy)
        p.mouse.down()
        p.mouse.move(wb["x"] - 20, hy, steps=6)
        p.mouse.up()
        self.wait(lambda: not row()["edit"].get("trim_in"), "the trim to be taken back")
        self.wait(lambda: loaded() == saved_voice(), "the player to load the whole take again")
        self.reqs.clear()
        p.mouse.move(at(0.4), y)
        p.mouse.down()
        p.mouse.move(at(0.5), y, steps=4)
        p.mouse.move(at(0.6), y, steps=4)
        p.mouse.up()
        d.locator(".wave-sel").wait_for(timeout=3000)
        self.assertTrue(self.uncovered(d.get_by_role("button", name="cut this part")))
        p.keyboard.press("Escape")                                                          # clears the selection, the dialog stays
        self.assertEqual(d.locator(".wave-sel").count(), 0)
        self.assertTrue(p.locator("dialog.take-editor[open]").count() == 1)
        d.get_by_role("button", name="zoom in").click()                                     # 1.5x: the wave is wider than the scroll area
        p.wait_for_timeout(300)
        self.assertGreater(d.locator(".takewave").bounding_box()["width"], 1.4 * wb["width"])
        d.get_by_role("button", name="zoom out").click()
        p.wait_for_timeout(300)
        p.mouse.move(at(0.4), y)
        p.mouse.down()
        p.mouse.move(at(0.5), y, steps=4)
        p.mouse.move(at(0.6), y, steps=4)
        p.mouse.up()
        d.locator(".wave-sel").wait_for(timeout=3000)
        p.keyboard.press("Delete")
        edits = self.wait(lambda: self.posts("/api/edit"), "the cut from the wide editor")
        body = json.loads(edits[-1][2])
        self.assertEqual(set(body), {"cuts"})
        self.assertEqual(len(body["cuts"]), 1)
        ca, cb = body["cuts"][0]
        self.assertAlmostEqual(cb - ca, 0.2 * row()["raw_length"], delta=0.1)
        d.locator(".cut-hand").wait_for(timeout=8000)
        self.assertEqual(d.locator(".te-cuts .chip-btn").count(), 1)
        cut_voice = lambda: saved_voice()
        self.wait(lambda: loaded() == saved_voice() and len(saved_voice()) != len(old_voice) or loaded() == saved_voice() and saved_voice() != old_voice, "the player to hold the cut take")
        d.get_by_role("button", name=re.compile("^(play|pause)$")).click()
        p.wait_for_timeout(400)
        self.assertEqual(loaded(), saved_voice())
        d.get_by_role("button", name=re.compile("^(play|pause)$")).click()
        self.wait(lambda: abs(row()["length"] - (len0 - (cb - ca))) <= 0.02, "the take to be shorter")
        if SHOTS:
            p.screenshot(path=str(SHOTS / "cut_dialog.png"))
        d.locator(".te-cuts .chip-btn").click()                                             # restore from the list
        self.wait(lambda: row()["edit"].get("cuts", []) == [], "the cut to be restored")
        d.get_by_role("button", name="Close").click()
        d.wait_for(state="detached", timeout=6000)

    # ─── 3 ───
    def test_3_edit(self):
        p = self.page
        self.open("edit", line=1)
        p.wait_for_selector(".script-list .line-row")
        p.wait_for_timeout(1500)
        tc = lambda: p.eval_on_selector(".transport .timecode", "e => e.textContent")
        secs = lambda t: int(t.split(":")[0]) * 60 + float(t.split(":")[1])
        t0, v0 = secs(tc()), p.eval_on_selector("video", "v => v.currentTime")
        p.click('button[aria-label^="Play"]')
        p.wait_for_timeout(3000)
        t1, v1 = secs(tc()), p.eval_on_selector("video", "v => v.currentTime")
        p.keyboard.press("Space")
        self.assertGreater(t1 - t0, 2.2)
        self.assertGreater(v1 - v0, 2.2)
        self.assertTrue(p.eval_on_selector("video", "v => v.paused"))
        # a take: trim its start handle
        p.click("#line-1")
        p.wait_for_selector(".take .trim-handle.in")
        h = p.locator(".take .trim-handle.in").first.bounding_box()
        self.reqs.clear()
        p.mouse.move(h["x"] + 1, h["y"] + h["height"] / 2)
        p.mouse.down()
        p.mouse.move(h["x"] + 40, h["y"] + h["height"] / 2, steps=5)
        p.mouse.up()
        p.wait_for_timeout(1200)
        edits = self.posts("/api/edit")
        self.assertEqual(len(edits), 1)
        self.assertEqual(set(json.loads(edits[0][2])), {"trim_in"})
        # a click on the level strip plays the take from there
        box = p.locator(".take .takewave").first.bounding_box()
        p.mouse.click(box["x"] + box["width"] * 0.6, box["y"] + box["height"] / 2)
        p.wait_for_timeout(600)
        self.assertIn("YOUR VOICE", p.inner_text(".screen-tag"))
        p.click("button:has-text('back to the lecture')")
        p.click(".take button:has-text('undo trims')")
        p.wait_for_timeout(800)
        self.cut_a_part_by_hand()
        # the margin
        inp = p.locator('input[aria-label="margin at line ends, seconds"]')
        inp.fill("0.5")
        inp.press("Enter")
        p.wait_for_timeout(800)
        st = self.posts("/api/settings")
        self.assertTrue(st and "key=margin" in st[-1][1] and "value=0.5" in st[-1][1], st)
        self.assertEqual(inp.input_value(), "0.5")
        # delete a recording after the confirm
        p.click("summary:has-text('Recordings')")
        n = p.locator(".session").count()
        victim = p.locator('.session button[aria-label^="Delete recording"]').first.get_attribute("aria-label").replace("Delete recording ", "")
        btn = p.locator('.session button[aria-label^="Delete recording"]').first
        # Esc cancels: the dialog shows its title, focus is on Cancel (danger), and nothing is sent
        n_del = len([r for r in self.reqs if "/api/delete" in r[1]])
        btn.click()
        d = p.locator("dialog.dialog[open]")
        d.wait_for(timeout=6000)
        self.assertEqual(d.locator(".dialog-title").inner_text(), f"Delete recording {victim}?")
        self.assertIn("cannot be undone", d.locator(".dialog-body").inner_text())
        self.assertEqual(p.evaluate("document.activeElement.textContent"), "Cancel")
        self.shot("dialog_delete")
        p.keyboard.press("Escape")
        d.wait_for(state="detached", timeout=6000)
        p.wait_for_timeout(500)
        self.assertEqual(len([r for r in self.reqs if "/api/delete" in r[1]]), n_del)
        self.assertEqual(p.locator(".session").count(), n)
        btn.click()
        self.assertEqual(self.ask(button="Delete recording"), f"Delete recording {victim}?")
        p.wait_for_timeout(1500)
        self.assertTrue(any("/api/delete" in r[1] and f"name={victim}" in r[1] for r in self.reqs))
        self.assertEqual(p.locator(".session").count(), n - 1)
        # convert a recording to the cloned voice: the button posts /api/process with clean=cloned (stubbed: no voice server here)
        p.route("**/api/process*", lambda r: r.fulfill(status=200, body=""))
        self.reqs.clear()
        conv = p.locator('.session button:has-text("convert to cloned voice")').first
        who = conv.locator("xpath=..").locator(".mono").first.get_attribute("title")
        conv.click()
        p.wait_for_timeout(800)
        pr = self.posts("/api/process")
        self.assertTrue(pr and "clean=cloned" in pr[-1][1] and f"name={who}" in pr[-1][1] and f"build={B}" in pr[-1][1], pr)
        p.unroute("**/api/process*")
        # merge: a stubbed ready version (no real one exists in the scratch project); Esc cancels, nothing is posted
        def stub(route):
            body = route.fetch().json()
            row = {"n": 1, "base": None, "texts": {}, "state": "ready", "error": "", "created": 1.0, "changed": [], "report": {}, "video": None, "line_starts": {}}
            body["versions"] = {sc: [row] for sc in body["scenes"]}
            route.fulfill(json=body)
        p.route("**/api/project?*", stub)
        p.reload()
        mb = p.locator('button[title="put it in the lecture"]').first
        mb.wait_for(state="attached", timeout=8000)
        if not mb.is_visible():
            p.click("summary:has-text('-voice versions')")
        mb.click()
        d = p.locator("dialog.dialog[open]")
        d.wait_for(timeout=6000)
        self.assertEqual(d.locator(".dialog-title").inner_text(), "Merge v1 into the lecture?")
        self.assertEqual(p.evaluate("document.activeElement.textContent"), "Merge")
        self.shot("dialog_merge")
        p.keyboard.press("Escape")
        d.wait_for(state="detached", timeout=6000)
        p.wait_for_timeout(500)
        self.assertEqual(self.posts("/api/merge"), [])
        p.unroute("**/api/project?*")
        self.shot("edit")

    # ─── 4 ───
    def test_4_script_and_languages(self):
        p = self.page
        self.open("script")
        p.wait_for_selector(".mgrid .mg-row")
        key = p.locator(".mg-row").first.get_attribute("data-key")
        cell = lambda k, lang: p.locator(f'.mg-row[data-key="{k}"] .mg-cell[data-lang="{lang}"]')
        state = lambda lang, k: next(x["state"] for x in self.get(f"/api/narration?lecture={STEM}&lang={lang}")["lines"] if x["key"] == k)
        self.assertEqual(cell(key, "en").get_attribute("data-state"), "draft")
        cell(key, "en").click()
        p.click('button:text-is("approve")')
        self.wait(lambda: state("en", key) == "approved", "the approval")
        # an edit: only that line of the narration file changes
        keys = [r.get_attribute("data-key") for r in p.locator(".mg-row").all()]
        k2 = keys[1]
        path = self.nar / f"{STEM}.md"
        before = path.read_text()
        cell(k2, "en").click()
        ta = p.locator('textarea[aria-label="text"]')
        ta.fill(ta.input_value() + " (edited in the test)")
        self.assertTrue(p.locator('button:text-is("approve")').is_disabled())
        p.click('button:has-text("save edit")')
        self.wait(lambda: path.read_text() != before, "the file to change")
        diff = [l for l in difflib.unified_diff(before.splitlines(), path.read_text().splitlines(), lineterm="", n=0) if l[0] in "+-" and not l.startswith(("+++", "---"))]
        self.assertEqual(len(diff), 2, diff)
        self.assertIn("(edited in the test)", diff[1])
        self.wait(lambda: state("en", k2) == "approved", "the saved line to be approved")
        # still fine: change the Uzbek of the approved line; the English needs an update; confirm it
        cell(key, "uz").click()
        ta = p.locator('textarea[aria-label="text"]')
        ta.fill(ta.input_value() + " Qoʻshimcha soʻz.")
        p.click('button:has-text("save edit")')
        self.wait(lambda: state("en", key) == "needs_update", "the English to need an update")
        p.wait_for_timeout(500)
        cell(key, "en").click()
        p.click('button:has-text("still fine")')
        self.wait(lambda: state("en", key) == "approved", "still fine")
        # the Uzbek rule: some Uzbek is not approved, so Build is disabled with the reason, and the server refuses too
        self.assertIn("never voiced or built", p.inner_text(".uz-rule"))
        btn = p.locator('.lang-strip tr[data-lang="uz"] button:has-text("Build")')
        self.assertTrue(btn.is_disabled())
        self.assertIn("Uzbek is built only when every line and label is approved", p.inner_text('.build-note[data-lang="uz"]'))
        r = p.evaluate(f"fetch('/api/narration/build?lecture={STEM}&lang=uz',{{method:'POST'}}).then(async r => [r.status, await r.text()])")
        self.assertEqual(r[0], 400)
        self.assertIn("approved", r[1])
        self.shot("script")
        self.errors[:] = [e for e in self.errors if "status of 400" not in e]            # the refusal above is on purpose

    # ─── 5 ───
    def test_5_export(self):
        p = self.page
        fake = {"on": False}

        def proj(route):
            r = route.fetch()
            d = r.json()
            if fake["on"]:
                d["jobs"].append({"build": B, "kind": "export", "key": "export", "state": "running", "error": "", "updated": time.time(), "detail": "encoding"})
                d["exports"].append({"name": f"{B}_edited.mp4", "url": f"/{B}/presenter/export/{B}_edited.mp4", "size": 137000000, "time": time.time()})
            route.fulfill(response=r, body=json.dumps(d))
        p.route("**/api/project*", proj)
        p.route("**/api/export*", lambda r: (fake.update(on=True), r.fulfill(status=200, body="")))     # the export itself is not run here
        self.open("export")
        p.wait_for_selector(".stats")
        api = self.project()
        you = len([l for l in api["edit_list"]["lines"] if l[3]])
        self.assertEqual(p.inner_text("[data-testid=n-you]"), str(you))
        self.assertEqual(you, len(api["used"]))
        self.assertEqual(p.inner_text("[data-testid=n-rest]"), str(len(api["lines"]) - you))
        self.assertTrue(p.evaluate("document.querySelector('input[name=clean]:checked').parentElement.innerText.startsWith('cloned')"))   # the default
        p.locator('label.rcard:has(b:text-is("voice"))').click()
        self.assertEqual(p.evaluate("localStorage.getItem('studioClean')"), "voice")
        self.reqs.clear()
        other = p.evaluate("document.querySelector('input[name=missing]:not(:checked)').parentElement.innerText.startsWith('Silent') ? 'silent' : 'original'")
        p.locator("input[name=missing]:not(:checked)").locator("xpath=..").click()
        p.wait_for_timeout(1000)
        st = self.posts("/api/settings")
        self.assertTrue(st and "key=missing" in st[-1][1] and f"value={other}" in st[-1][1], st)
        p.click("#export-now")
        p.wait_for_timeout(1500)
        ex = self.posts("/api/export")
        self.assertTrue(ex and "clean=voice" in ex[-1][1] and f"build={B}" in ex[-1][1], ex)
        self.assertIn("running", p.inner_text('.jobs-list li[data-kind="export"]'))
        self.assertGreaterEqual(p.locator('.exp-list a[href$="_edited.mp4"]').count(), 1)
        p.click("button:has-text('Watch the lecture video')")
        p.wait_for_selector("video.watch-video")
        self.assertIn(f"/{B}/{B}.mp4", p.get_attribute("video.watch-video", "src"))
        self.shot("export")
        p.unroute("**/api/project*")
        self.errors[:] = [e for e in self.errors if "status of 404" not in e]

    def test_9_no_console_errors(self):
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=1)
