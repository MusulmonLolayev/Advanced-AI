"""The server's front door: `/` is the React app (never cached, hashed assets cached for good), the old pages' addresses
(/?m=N, /lecture, /edit, /watch, /narration, <build>/presenter/presenter.html) answer 302 with the app's deep link, and
/api/lectures lists the project browser's modules, lectures and languages. A real server on a free port, a scratch root.

    uv run python -m unittest discover -s studio -p 'test_routes.py' -t .        (from video/)
"""
import http.client
import importlib
import json
import os
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

NARRATION = """## Lecture opening
0. **Birinchi qator.**
   *Line one.*
### 1-boʻlim · Section 1 — Nega agent? · Why an agent?
1. **Ikkinchi qator.**
   *Line two.*
"""
UZ = "lecture98_uz_navoiy"


class Routes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = cls.root = Path(cls.tmp.name) / "out"
        root.mkdir()
        nar = Path(cls.tmp.name) / "narration"
        nar.mkdir()
        (nar / "lecture98.md").write_text(NARRATION)
        (nar / "labels.yaml").write_text("{}\n")
        cls.env = {k: os.environ.get(k) for k in ("STUDIO_ROOT", "STUDIO_NARRATION", "STUDIO_PROFILE")}
        os.environ.update(STUDIO_ROOT=str(root), STUDIO_NARRATION=str(nar), STUDIO_PROFILE="off")
        import labels
        cls.labels, cls.old_labels = labels, labels.NARRATION
        labels.use(nar)
        (root / UZ).mkdir()
        (root / UZ / f"{UZ}.mp4").write_bytes(b"v")
        (root / UZ / "joined.txt").write_text("")
        (root / "shared" / "m0").mkdir(parents=True)
        (root / "shared" / "m0" / "notes.pdf").write_bytes(b"pdf")
        import serve_presenter as sp
        cls.sp = importlib.reload(sp)
        cls.sp.Studio.log_message = lambda *a: None
        static = root / "static"
        (static / "app" / "assets").mkdir(parents=True)
        (static / "app" / "index.html").write_text("<html>app</html>")
        (static / "app" / "assets" / "index-abc.js").write_text("export {}")
        cls.sp.STATIC = static
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(cls.sp.Studio, directory=str(root)))
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.port = cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.labels.use(cls.old_labels)
        for k, v in cls.env.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        cls.tmp.cleanup()

    def head(self, path, method="GET"):
        """(status, headers, body) with no redirect followed."""
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        c.request(method, path)
        r = c.getresponse()
        out = (r.status, {k.lower(): v for k, v in r.getheaders()}, r.read())
        c.close()
        return out

    def goes_to(self, path, **want):
        status, h, _ = self.head(path)
        self.assertEqual(status, 302, path)
        u = urlparse(h["location"])
        self.assertEqual(u.path, "/", path)
        got = {k: v[0] for k, v in parse_qs(u.query).items()}
        self.assertEqual(got, want, path)
        self.assertEqual(h["cache-control"], "no-store")
        return h["location"]

    def test_the_cloned_profile_is_known_and_the_default_for_new_recordings(self):
        self.assertIn("cloned", self.sp.CLEAN)
        self.assertEqual(list(self.sp.CLEAN)[-1], "cloned")
        src = (Path(self.sp.__file__)).read_text()
        self.assertIn('os.environ.get("STUDIO_PROFILE", "cloned")', src)              # the default; the tests set "off"
        self.assertIn('else "cloned"))', src)                                          # the export's default

    def test_the_front_page_is_the_app_and_is_never_cached_but_the_hashed_assets_are(self):
        for path in ("/", "/index.html"):
            status, h, body = self.head(path)
            self.assertEqual((status, body, h["cache-control"]), (200, b"<html>app</html>", "no-cache"), path)
        status, h, _ = self.head("/studio-static/app/assets/index-abc.js")
        self.assertEqual((status, h["cache-control"]), (200, "public, max-age=31536000, immutable"))

    def test_every_old_address_goes_to_the_same_thing_in_the_app(self):
        self.goes_to("/?m=0", lecture="lecture98")                                            # the module page: its first lecture
        self.assertEqual(self.head("/?m=3")[1]["location"], "/")                              # no lecture there: the app's front page
        self.assertEqual(self.head("/?m=9")[1]["location"], "/")
        self.goes_to(f"/lecture?build={UZ}", mode="export", lecture="lecture98", lang="uz", watch="lecture")
        self.goes_to(f"/edit?build={UZ}", mode="edit", lecture="lecture98", lang="uz")
        self.goes_to(f"/watch?build={UZ}&name=2026-10-21T14-24-06", mode="export", lecture="lecture98", lang="uz", watch="2026-10-21T14-24-06")
        self.goes_to(f"/watch?build={UZ}&name=../x", mode="export", lecture="lecture98", lang="uz")      # a bad name is not passed on
        self.goes_to("/narration?lecture=lecture98&lang=en", mode="script", lecture="lecture98", lang="en")
        self.goes_to(f"/{UZ}/presenter/presenter.html", mode="record", lecture="lecture98", lang="uz")
        # the fragment of an old address (presenter.html#line=41) stays with the browser, which appends it to the Location
        self.assertNotIn("#", self.head(f"/{UZ}/presenter/presenter.html")[1]["location"])

    def test_head_answers_like_get_without_the_body(self):
        status, h, body = self.head("/", "HEAD")
        self.assertEqual((status, body, h["cache-control"]), (200, b"", "no-cache"))
        status, h, body = self.head(f"/edit?build={UZ}", "HEAD")
        self.assertEqual((status, body), (302, b""))
        self.assertIn("mode=edit", h["location"])

    def test_addresses_that_are_not_a_lecture_are_not_redirected(self):
        for path in ("/lecture?build=nope", "/edit", "/narration?lecture=lecture98&lang=xx", "/narration?lecture=../x&lang=uz",
                     "/m7_lecture01_en/presenter/presenter.html"):
            self.assertEqual(self.head(path)[0], 404, path)

    def test_the_lecture_list_over_http(self):
        status, _, body = self.head("/api/lectures")
        self.assertEqual(status, 200)
        mods = json.loads(body)["modules"]
        self.assertEqual([m["k"] for m in mods], list(range(8)))
        zero = mods[0]
        self.assertEqual(zero["title"], "Statistics for Advanced AI")
        self.assertEqual([f["name"] for f in zero["files"]], ["notes.pdf"])
        lec = zero["lectures"][0]
        self.assertEqual((lec["stem"], lec["n"], [l["lang"] for l in lec["langs"]]), ("lecture98", 98, ["uz", "en"]))
        uz = lec["langs"][0]
        self.assertEqual((uz["build"], uz["lines"]["total"], uz["lines"]["draft"]), (UZ, 2, 2))
        self.assertEqual(mods[1]["lectures"], [])


if __name__ == "__main__":
    unittest.main()
