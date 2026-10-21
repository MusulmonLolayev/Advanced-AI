"""Unit tests for studio/timeline.py: takes, tracks, cuts, nudges, the edit list, subtitles, the script check.

    uv run python -m unittest discover -s studio -p 'test_timeline.py'        (from video/)
"""
import json
import random
import unittest
from pathlib import Path

from studio import timeline as T

R = 1 / 1.1                                       # the presenter's speed
STARTS = [0.0, 10.0, 20.0]                        # three narration lines in a 30 s video


def session():
    """Line 0 played and talked over, then a retake of line 1 (X), line 1 again, then line 2 and stop."""
    return [
        [0.0, "hold", 0.0, R],
        [1.0, "line", 0.0, R, 0], [1.05, "play", 0.0, R],
        [12.05, "hold", 10.0, R],                 # 11 s at 1/1.1 shows 10 s of video; the picture stops at line 1
        [15.0, "line", 10.0, R, 1], [15.05, "play", 10.0, R],
        [17.0, "retake", 11.77, R, 1], [17.0, "hold", 11.77, R],
        [18.0, "line", 10.0, R, 1], [18.05, "play", 10.0, R],
        [29.05, "hold", 20.0, R],
        [31.0, "line", 20.0, R, 2], [31.05, "play", 20.0, R],
        [42.05, "hold", 30.0, R],
        [43.0, "stop", 30.0, R],
    ]


class Takes(unittest.TestCase):
    def test_one_take_per_line_start_and_the_retake_is_rejected(self):
        tk = T.takes("s1", session(), STARTS)
        self.assertEqual([(t["line"], t["rejected"]) for t in tk], [(0, False), (1, True), (1, False), (2, False)])
        self.assertEqual([(t["t_in"], t["t_out"]) for t in tk], [(1.0, 15.0), (15.0, 17.0), (18.0, 31.0), (31.0, 43.0)])
        self.assertEqual(tk[0]["id"], "s1@1.00")

    def test_a_crashed_session_ends_where_the_audio_ends(self):
        ev = [e for e in session() if e[0] < 35]                   # no stop: the tab closed at 35 s
        tk = T.takes("s1", ev, STARTS, end=36.5)
        self.assertEqual((tk[-1]["line"], tk[-1]["t_out"]), (2, 36.5))

    def test_old_recordings_get_line_starts_from_play_positions(self):
        old = [e for e in session() if e[1] not in T.MARKERS]
        self.assertEqual([t["line"] for t in T.takes("s0", old, STARTS)], [0, 1, 1, 2])

    def test_markers_do_not_change_the_picture(self):
        self.assertEqual(T.segments(session()), T.segments([e for e in session() if e[1] not in T.MARKERS]))


class Tracks(unittest.TestCase):
    def setUp(self):
        self.ev = session()
        self.take = T.takes("s1", self.ev, STARTS)[0]              # line 0: 1.0 .. 15.0

    def test_voice_and_picture_have_the_take_length(self):
        tr = T.take_tracks(self.take, self.ev)
        self.assertAlmostEqual(T.length(tr["voice"]), 14.0)
        self.assertAlmostEqual(T.length(tr["picture"]), 14.0)
        self.assertEqual(tr["voice"], [(14.0, "s1", 1.0)])
        kinds = [p[1] for p in tr["picture"]]
        self.assertEqual(kinds, ["hold", "play", "hold"])           # 0.05 s before playing, the line, then held
        play = tr["picture"][1]
        self.assertAlmostEqual(play[2], 0.0)
        self.assertAlmostEqual(play[3], 10.0)

    def test_a_cut_removes_the_same_span_from_both_tracks(self):
        tr = T.take_tracks(self.take, self.ev)
        v, p = T.cut(tr["voice"], [(12.0, 13.5)], True), T.cut(tr["picture"], [(12.0, 13.5)], False)
        self.assertAlmostEqual(T.length(v), 12.5)
        self.assertAlmostEqual(T.length(p), 12.5)
        self.assertEqual([(round(d, 3), s, round(a, 3)) for d, s, a in v], [(12.0, "s1", 1.0), (0.5, "s1", 14.5)])

    def test_a_cut_inside_a_play_skips_that_much_picture(self):
        tr = T.take_tracks(self.take, self.ev)
        p = T.cut(tr["picture"], [(2.05, 3.15)], False)              # 1.1 s at 1/1.1 = 1 s of video
        plays = [x for x in p if x[1] == "play"]
        self.assertAlmostEqual(plays[0][3], 2.0 * R, places=6)
        self.assertAlmostEqual(plays[1][2], 3.1 * R, places=6)

    def test_nudge_moves_voice_against_picture_and_keeps_one_length(self):
        tr = T.take_tracks(self.take, self.ev)
        later = T.nudge(tr, 0.4)
        self.assertEqual(later["picture"][0][:3], (0.4, "hold", tr["picture"][0][2]))
        self.assertEqual(later["voice"][-1], (0.4, None, None))
        sooner = T.nudge(tr, -0.3)
        self.assertEqual(sooner["voice"][0], (0.3, None, None))
        for x in (later, sooner):
            self.assertAlmostEqual(T.length(x["voice"]), T.length(x["picture"]))

    def test_edited_applies_trim_cuts_and_nudge(self):
        # the take: 0.05 s held, 11 s of animation (to local 11.05), then held. trim_in 0.5 reaches 0.45 s into the
        # animation (squeezed to 0.15 s, its voice silent); trim_out 1.0 and the cut are over the held picture.
        e = T.edited(self.take, self.ev, {"trim_in": 0.5, "trim_out": 1.0, "cuts": [(12.0, 12.5)], "nudge": 0.2})
        self.assertAlmostEqual(T.length(e["voice"]), 14 - 0.05 - 0.45 + 0.15 - 1.0 - 0.5 + 0.2)
        self.assertAlmostEqual(T.length(e["picture"]), T.length(e["voice"]))


class Conserved(unittest.TestCase):
    """Spans of a few milliseconds (events a click apart) must not be dropped: the picture would run short of the voice."""
    def test_the_recorded_take_that_broke_the_editor(self):
        ev = [[0.0, "hold", 0, R], [1.3869, "line", 0, R, 0], [1.3947, "hold", 0, R], [1.3992, "play", 0.021396, R],
              [2.5771, "hold", 1.091909, R], [2.7381, "play", 1.092119, R], [16.1276, "hold", 13.26, R],
              [16.1545, "hold", 13.26, R], [17.4024, "line", 13.3, R, 1], [17.4114, "hold", 13.3, R]]
        take = {"id": "s@1.39", "session": "s", "line": 0, "t_in": 1.3869, "t_out": 17.4024, "rejected": False}
        tr = T.take_tracks(take, ev)
        self.assertAlmostEqual(T.length(tr["voice"]), 16.0155, places=9)
        self.assertAlmostEqual(T.length(tr["picture"]), T.length(tr["voice"]), places=9)

    def test_segments_add_up_to_the_events_span(self):
        ev = [[1.0, "hold", 0, R], [1.004, "play", 0.0, R], [1.009, "hold", 0.01, R], [3.0, "stop", 0.01, R]]
        self.assertAlmostEqual(sum(s[3] for s in T.segments(ev)), 2.0, places=9)

    def test_random_events_keep_both_tracks_one_length(self):
        rnd = random.Random(7)
        for _ in range(200):
            t, pos, ev = 0.0, 0.0, []
            for _ in range(rnd.randint(3, 25)):
                t += rnd.choice([0.0005, 0.004, 0.0075, 0.02, 0.3, 2.0])
                pos += rnd.choice([0.0, 0.0, 0.5, 3.0])
                ev.append([t, rnd.choice(["play", "hold", "line", "retake"]), pos, R, 0])
            ev[0][1] = "line"
            ev.append([t + 0.01, "stop", pos, R])
            take = {"id": "s@0", "session": "s", "line": 0, "t_in": ev[0][0], "t_out": t + 0.01, "rejected": False}
            tr = T.take_tracks(take, ev)
            self.assertAlmostEqual(T.length(tr["picture"]), T.length(tr["voice"]), places=9)
            total = T.length(tr["voice"])
            edit = {"cuts": [(total * 0.2, total * 0.2 + 0.003), (total * 0.5, total * 0.7)],
                    "trim_in": rnd.choice([0, 0.001, total * 0.3]), "trim_out": rnd.choice([0, 0.002, total * 0.25, total * 0.9]),
                    "nudge": rnd.choice([0, 0.4, -0.7])}
            ed = T.edited(take, ev, edit)
            self.assertAlmostEqual(T.length(ed["picture"]), T.length(ed["voice"]), places=9)
            for _ in range(3):                                     # squeezes too, overlapping cuts and each other
                sq = [[a, a + rnd.choice([0.0004, 0.5, 4.0]), rnd.choice([0.001, 0.15, 1.0])]
                      for a in (rnd.uniform(0, total) for _ in range(rnd.randint(1, 4)))]
                ed = T.edited(take, ev, dict(edit, squeeze=sq, auto_cuts=[(total * 0.1, total * 0.3)]))
                self.assertAlmostEqual(T.length(ed["picture"]), T.length(ed["voice"]), places=9)

    def test_edit_list_pads_a_mismatch_instead_of_failing(self):
        tr = {"voice": [(5.0, "s", 0.0)], "picture": [(4.9, "play", 0.0, 4.0, R)]}
        el = T.edit_list([0.0], 5.0, {0: tr})
        self.assertAlmostEqual(T.length(el["voice"]), T.length(el["picture"]))
        tr = {"voice": [(4.9, "s", 0.0)], "picture": [(5.0, "hold", 1.0, None, 1)]}
        el = T.edit_list([0.0], 5.0, {0: tr})
        self.assertAlmostEqual(T.length(el["voice"]), T.length(el["picture"]))


class Silences(unittest.TestCase):
    def test_only_silence_over_a_still_picture_is_shortened(self):
        picture = [(2.0, "play", 0, 2, 1), (4.0, "hold", 2, None, 1), (2.0, "play", 2, 4, 1)]
        cuts = T.shrink_silences([(0.5, 1.8), (2.5, 5.5)], picture, total=8.0)
        self.assertEqual(cuts, [(2.75, 5.25)])                     # the first silence is animation time: kept

    def test_the_tail_keeps_a_short_breath(self):
        picture = [(3.0, "play", 0, 3, 1), (3.0, "hold", 3, None, 1)]
        self.assertEqual(T.shrink_silences([(3.6, 6.0)], picture, total=6.0), [(3.85, 6.0)])

    def test_short_pauses_stay(self):
        self.assertEqual(T.shrink_silences([(1.0, 1.6)], [(4.0, "hold", 0, None, 1)], total=4.0), [])


class Squeeze(unittest.TestCase):
    PIC = [(2.0, "hold", 0, None, 1), (4.0, "play", 0, 4, 1), (2.0, "hold", 4, None, 1), (2.0, "play", 4, 6, 0.5)]
    VOICE = [(10.0, "s", 100.0)]

    def both(self, cuts, sq):
        return T.squeeze(self.VOICE, cuts, sq, True), T.squeeze(self.PIC, cuts, sq, False)

    def test_both_tracks_get_the_new_length(self):
        v, p = self.both([], [[1.0, 7.0, 1.5]])
        self.assertAlmostEqual(T.length(v), 10 - 6 + 1.5, places=9)
        self.assertAlmostEqual(T.length(p), T.length(v), places=9)

    def test_play_speeds_are_multiplied_and_holds_shortened(self):
        _, p = self.both([], [[1.0, 7.0, 1.5]])                    # f = 4 over: 1 s of hold, 4 s of play, 1 s of hold
        self.assertEqual(p, [(1.0, "hold", 0, None, 1), (0.25, "hold", 0, None, 1), (1.0, "play", 0, 4, 4.0),
                             (0.25, "hold", 4, None, 1), (1.0, "hold", 4, None, 1), (2.0, "play", 4, 6, 0.5)])
        _, p = self.both([], [[6.0, 10.0, 1.0]])                   # a slow play: 0.5 x 4 = 2
        self.assertEqual(p[-1], (0.5, "play", 4, 6, 2.0))

    def test_a_squeeze_starting_inside_a_play_covers_the_same_picture(self):
        _, p = self.both([], [[3.0, 5.0, 0.5]])                    # video seconds 1 .. 3 at 4 x
        self.assertEqual([x for x in p if x[1] == "play"][:3],
                         [(1.0, "play", 0, 1.0, 1), (0.5, "play", 1.0, 3.0, 4.0), (1.0, "play", 3.0, 4, 1)])

    def test_the_voice_of_a_squeezed_span_is_silent(self):
        v, _ = self.both([], [[2.0, 8.0, 1.5]])
        self.assertEqual(v, [(2.0, "s", 100.0), (1.5, None, None), (2.0, "s", 108.0)])

    def test_a_cut_wins_over_a_squeeze(self):
        v, p = self.both([(3.0, 5.0)], [[2.0, 8.0, 1.5]])           # f = 4; the 2 s cut is gone, the other 4 s become 1
        self.assertEqual(v, [(2.0, "s", 100.0), (0.25, None, None), (0.75, None, None), (2.0, "s", 108.0)])
        self.assertAlmostEqual(T.length(p), 5.0, places=9)
        self.assertEqual(p[1:3], [(0.25, "play", 0, 1.0, 4.0), (0.25, "play", 3.0, 4, 4.0)])
        self.assertEqual(self.both([(0.0, 10.0)], [[2.0, 8.0, 1.5]]), ([], []))     # all cut: nothing squeezed is left

    def test_edited_applies_auto_cuts_with_the_manual_ones(self):
        ev = session()
        take = T.takes("s1", ev, STARTS)[0]
        a = T.edited(take, ev, {"cuts": [(12.0, 12.5)], "auto_cuts": [(13.0, 13.5)]})
        b = T.edited(take, ev, {"cuts": [(12.0, 12.5), (13.0, 13.5)]})
        self.assertEqual(a, b)
        old = T.edited(take, ev, {"cuts": [(12.0, 12.5)]})          # an edit made before auto_cuts existed
        self.assertAlmostEqual(T.length(old["voice"]), 13.5)


class Trim(unittest.TestCase):
    """trim_in / trim_out remove the take's ends like tightening does: cut where the picture is still, fast-forwarded
    (up to 4 x, the voice silent) where it plays, so an animation is never cut."""
    def events(self):
        return [[0.0, "line", 0, 1, 0], [0.0, "play", 0, 1], [10.0, "hold", 10, 1], [12.0, "stop", 10, 1]]

    def take(self):
        return {"id": "s@0.00", "session": "s", "line": 0, "t_in": 0.0, "t_out": 12.0, "rejected": False}

    def both(self, edit):
        e = T.edited(self.take(), self.events(), edit)
        self.assertAlmostEqual(T.length(e["voice"]), T.length(e["picture"]), places=9)
        return e

    def test_a_trim_over_a_still_picture_is_a_cut(self):
        e = self.both({"trim_out": 1.5})                             # the picture holds from 10 s on
        self.assertEqual(T.plan(T.take_tracks(self.take(), self.events())["picture"], 12.0, {"trim_out": 1.5}),
                         ([(10.5, 12.0)], []))
        self.assertAlmostEqual(T.length(e["voice"]), 10.5)
        self.assertEqual(e["voice"], [(10.5, "s", 0.0)])
        self.assertEqual([p[1] for p in e["picture"]], ["play", "hold"])
        self.assertAlmostEqual(e["picture"][-1][0], 0.5)

    def test_a_trim_over_a_playing_picture_is_a_squeeze_with_a_silent_voice(self):
        e = self.both({"trim_out": 4.0})                             # 2 s of animation (8..10) and 2 s held
        self.assertAlmostEqual(T.length(e["voice"]), 8.5)            # the animation in 0.5 s, the hold cut
        self.assertEqual(e["voice"], [(8.0, "s", 0.0), (0.5, None, None)])
        last = e["picture"][-1]
        self.assertEqual(last[:4], (0.5, "play", 8.0, 10.0))
        self.assertAlmostEqual(last[4], 4.0)                         # 4 x at the presenter's speed of 1
        self.assertEqual(e["picture"][-1][3], 10.0)                  # it still ends where the animation ends

    def test_the_start_is_squeezed_too_and_the_voice_there_is_silent(self):
        e = self.both({"trim_in": 2.0})
        self.assertEqual(e["voice"], [(0.5, None, None), (10.0, "s", 2.0)])
        self.assertEqual(e["picture"][0][:4], (0.5, "play", 0.0, 2.0))

    def test_a_short_animation_is_squeezed_to_at_least_0_15_s_and_a_tiny_one_is_left(self):
        pic = T.take_tracks(self.take(), self.events())["picture"]
        self.assertEqual(T.plan(pic, 12.0, {"trim_in": 0.4})[1], [(0.0, 0.4, 0.15)])
        self.assertEqual(T.plan(pic, 12.0, {"trim_in": 0.1})[1], [])          # 0.15 s would be longer than 0.1 s

    def test_a_trim_over_mixed_picture_does_both(self):
        pic = [(3.0, "hold", 0, None, 1), (3.0, "play", 0, 3, 1), (2.0, "hold", 3, None, 1), (4.0, "play", 3, 7, 1),
               (1.0, "hold", 7, None, 1)]
        cuts, sq = T.plan(pic, 13.0, {"trim_out": 9.0})                # 4..13: animation 4..6, hold, animation 8..12, hold
        self.assertEqual(cuts, [(6.0, 8.0), (12.0, 13.0)])
        self.assertEqual(sq, [(4.0, 6.0, 0.5), (8.0, 12.0, 1.0)])
        voice = [(13.0, "s", 0.0)]
        v, p = T.squeeze(voice, cuts, sq, True), T.squeeze(pic, cuts, sq, False)
        self.assertAlmostEqual(T.length(v), 13 - 9 + 0.5 + 1.0)
        self.assertAlmostEqual(T.length(p), T.length(v))
        self.assertEqual(v, [(4.0, "s", 0.0), (0.5, None, None), (1.0, None, None)])
        self.assertTrue(all(x[4] <= 4.0 + 1e-9 for x in p if x[1] == "play"))
        self.assertEqual([x[3] for x in p if x[1] == "play"], [1.0, 3, 7])      # each animation ends where it should

    def test_squeezes_of_the_tools_have_a_silent_voice_too(self):
        e = T.edited(self.take(), self.events(), {"squeeze": [[2.0, 6.0, 1.0]]})
        self.assertEqual(e["voice"], [(2.0, "s", 0.0), (1.0, None, None), (6.0, "s", 6.0)])


class Fit(unittest.TestCase):
    def test_lead_and_tail_are_the_silences_touching_the_ends(self):
        self.assertEqual(T.lead_tail([(0.0, 1.5), (4.0, 5.0), (8.0, 10.0)], 10.0), (1.5, 2.0))
        lead, tail = T.lead_tail([(0.02, 1.5), (9.97, 10.0)], 10.0)                    # within the 0.05 s tolerance
        self.assertEqual((lead, round(tail, 6)), (1.5, 0.03))
        self.assertEqual(T.lead_tail([(4.0, 5.0)], 10.0), (0.0, 0.0))                    # a pause inside is not an end
        self.assertEqual(T.lead_tail([(0.0, 10.0)], 10.0), (0.0, 0.0))                   # a take of nothing but silence

    def test_fit_keeps_the_margin_around_the_voice(self):
        sil = [(0.0, 1.5), (4.0, 5.0), (8.0, 10.0)]
        a, b = T.fit(sil, 10.0, 0.3)
        self.assertAlmostEqual(a, 1.2)
        self.assertAlmostEqual(b, 1.7)
        a, b = T.fit(sil, 10.0, 0.5)
        self.assertAlmostEqual(a, 1.0)
        self.assertAlmostEqual(b, 1.5)
        self.assertEqual(T.fit(sil, 10.0, 3.0), (0.0, 0.0))                              # the margin is longer than both

    def test_fit_does_nothing_for_a_gain_under_0_05_s(self):
        self.assertEqual(T.fit([(0.0, 0.34), (9.66, 10.0)], 10.0, 0.3), (0.0, 0.0))     # 0.04 s each: left alone
        a, b = T.fit([(0.0, 0.36), (9.0, 10.0)], 10.0, 0.3)
        self.assertAlmostEqual(a, 0.06)
        self.assertAlmostEqual(b, 0.7)

    def test_fit_then_trim_leaves_the_margin_in_the_edited_take(self):
        pic = [(10.0, "hold", 0, None, 1)]
        sil = [(0.0, 1.5), (8.0, 10.0)]
        tin, tout = T.fit(sil, 10.0, 0.3)
        cuts, sq = T.plan(pic, 10.0, {"trim_in": tin, "trim_out": tout})
        self.assertEqual((cuts, sq), ([(0.0, 1.2), (8.3, 10.0)], []))
        self.assertAlmostEqual(T.length(T.squeeze([(10.0, "s", 0.0)], cuts, sq, True)), 10 - 1.2 - 1.7)


class Pauses(unittest.TestCase):
    def test_interior_pauses_are_not_ends(self):
        sil = [(0.0, 3.0), (5.0, 8.0), (15.0, 20.0)]
        self.assertEqual(T.interior(sil, 20.0), [(5.0, 8.0)])
        picture = [(20.0, "hold", 0, None, 1)]
        inner = T.shrink_silences(T.interior(sil, 20.0), picture, 20.0)
        self.assertEqual(inner, [(5.25, 7.75)])
        tin, tout = T.fit(sil, 20.0, 0.3)
        cuts, _ = T.plan(picture, 20.0, {"trim_in": tin, "trim_out": tout})
        for a, b in cuts:                                          # the ends and the pauses inside never overlap
            self.assertTrue(all(b <= x or y <= a for x, y in inner))


class RealSession(unittest.TestCase):
    """The instructor's real recording of Lecture 1 (read only), when it is there."""
    R = Path(__file__).resolve().parents[1] / "out" / "lecture01_uz_navoiy" / "presenter"
    S = "2026-10-19T14-11-13"

    @unittest.skipUnless((R / "recordings" / f"{S}.json").exists() and (R / "recordings" / f"{S}.silence.json").exists()
                         and (R / "lines.json").exists(), "no such recording")
    def test_fit_both_on_every_take_keeps_the_tracks_in_step_and_stops_at_the_margin(self):
        ev = json.loads((self.R / "recordings" / f"{self.S}.json").read_text())
        sil = json.loads((self.R / "recordings" / f"{self.S}.silence.json").read_text())
        starts = [l[0] for l in json.loads((self.R / "lines.json").read_text())]
        margin, saved, trimmed = 0.3, 0.0, 0
        for t in T.takes(self.S, ev, starts):
            raw = T.take_tracks(t, ev)
            total = T.length(raw["voice"])
            local = [(max(a, t["t_in"]) - t["t_in"], min(b, t["t_out"]) - t["t_in"]) for a, b in sil
                     if b > t["t_in"] and a < t["t_out"]]
            tin, tout = T.fit(local, total, margin)
            lead, tail = T.lead_tail(local, total)
            cuts = T.shrink_silences(T.interior(local, total), raw["picture"], total)
            e = T.edited(t, ev, {"trim_in": tin, "trim_out": tout, "auto_cuts": cuts})
            self.assertAlmostEqual(T.length(e["voice"]), T.length(e["picture"]), places=9)
            # the trims stay inside the end silences, and leave `margin` seconds of them (or all of it, when shorter)
            self.assertLessEqual(tin, max(lead - margin, 0.0) + 1e-9, t["id"])
            self.assertLessEqual(tout, max(tail - margin, 0.0) + 1e-9, t["id"])
            self.assertTrue(tin == 0 or any(a <= 0.05 and tin <= b - margin + 1e-9 for a, b in local), t["id"])
            self.assertTrue(tout == 0 or any(b >= total - 0.05 and total - tout >= a + margin - 1e-9 for a, b in local), t["id"])
            saved += total - T.length(e["voice"])
            trimmed += (tin > 0) + (tout > 0)
        self.assertGreater(trimmed, 10)
        self.assertGreater(saved, 20)


class EditList(unittest.TestCase):
    def test_lines_without_a_take_show_their_own_picture(self):
        ev = session()
        tk = [t for t in T.takes("s1", ev, STARTS) if not t["rejected"]]
        chosen = {t["line"]: dict(T.take_tracks(t, ev), id=t["id"]) for t in tk if t["line"] != 1}
        el = T.edit_list(STARTS, 30.0, chosen)
        self.assertEqual([(k, tid) for k, _, _, tid in el["lines"]], [(0, "s1@1.00"), (1, None), (2, "s1@31.00")])
        k, a, b, _ = el["lines"][1]
        self.assertAlmostEqual(b - a, 10 / R)                       # line 1's picture at the presenter's speed
        self.assertAlmostEqual(T.length(el["voice"]), T.length(el["picture"]))
        self.assertAlmostEqual(el["lines"][-1][2], T.length(el["voice"]))

    def test_unrecorded_lines_can_keep_the_original_voice(self):
        ev = session()
        t0 = T.takes("s1", ev, STARTS)[0]
        el = T.edit_list(STARTS, 30.0, {0: dict(T.take_tracks(t0, ev), id=t0["id"])}, fallback="original")
        k, a, b, tid = el["lines"][1]
        self.assertEqual((tid, b - a), (None, 10.0))                 # at full speed, as built
        voice = [p for p in el["voice"] if p[1] == T.ORIGINAL]
        self.assertEqual([(d, pos) for d, _, pos in voice], [(10.0, 10.0), (10.0, 20.0)])
        self.assertIn((10.0, "play", 10.0, 20.0, 1.0), el["picture"])
        self.assertAlmostEqual(T.length(el["voice"]), T.length(el["picture"]))

    def test_frame_counts_never_drift(self):
        track = [(1 / 3, "hold", 0, None, 1)] * 300                 # 100 s in pieces of a third of a second
        n = T.frame_counts(track, fps=60)
        self.assertEqual(sum(n), 6000)
        self.assertTrue(all(c in (20,) for c in n))
        odd = [(0.0123 * (i % 7 + 1), "hold", 0, None, 1) for i in range(500)]
        self.assertEqual(sum(T.frame_counts(odd)), round(T.length(odd) * 60))

    def test_merge_picture_joins_continuing_pieces(self):
        p = [(1, "play", 0, 1, 1), (1, "play", 1, 2, 1), (1, "hold", 2, None, 1), (0.5, "hold", 2, None, 1),
             (1, "play", 2, 3, 0.5)]
        self.assertEqual(T.merge_picture(p), [(2, "play", 0, 2, 1), (1.5, "hold", 2, None, 1), (1, "play", 2, 3, 0.5)])


class Remap(unittest.TestCase):
    def test_positions_keep_their_offset_in_their_line(self):
        ev = [[1.0, "line", 10.0, R, 1], [1.05, "play", 10.0, R], [5.0, "hold", 13.6, R], [9.0, "play", 25.0, R]]
        new = T.remap_events(ev, [0, 10, 20], 30, [0, 12, 21], 31)  # line 0 grew by 2 s, line 1 shrank by 1 s
        self.assertEqual([e[2] for e in new], [12.0, 12.0, 15.6, 26.0])
        self.assertEqual([e[0] for e in new], [1.0, 1.05, 5.0, 9.0])  # the clock is untouched
        self.assertEqual(new[0][4], 1)

    def test_a_position_past_a_shorter_line_stops_at_its_end(self):
        new = T.remap_events([[0, "hold", 19.9, R]], [0, 10, 20], 30, [0, 10, 15], 30)
        self.assertAlmostEqual(new[0][2], 14.96)

    def test_a_different_line_count_is_refused(self):
        with self.assertRaises(ValueError):
            T.remap_events([], [0, 10], 20, [0, 5, 10], 20)


class Exports(unittest.TestCase):
    def test_srt_cards_cover_each_line_and_stay_two_rows(self):
        text = ("Now we give the same model the same question, but with no tools. No loop, no search: we ask once, "
                "like an ordinary chatbot.")
        s = T.srt([(0, 0.0, 9.0, "x"), (1, 9.0, 12.5, "y")], [text, "Short."])
        cards = [c for c in s.split("\n\n") if c.strip()]
        self.assertTrue(cards[0].startswith("1\n00:00:00,000 --> "))
        self.assertIn("00:00:12,500", cards[-1])
        for c in cards:
            self.assertLessEqual(len(c.splitlines()) - 2, 2)
        self.assertEqual(T.stamp(3725.5), "01:02:05,500")

    def test_chapters_start_at_zero(self):
        spans = [(0, 0.0, 5, None), (1, 5, 70, None), (2, 70, 130.4, None)]
        self.assertEqual(T.chapters(spans, {0: "Opening", 2: "Section 1 · Why"}), "0:00 Opening\n1:10 Section 1 · Why")

    def test_script_check_finds_missed_and_extra_words(self):
        heard = [("Let's", 0, .3, ), ("um", .3, .5), ("start", .5, .8), ("with", .8, 1), ("question", 1, 1.4)]
        missing, extra, changed = T.script_check("Let's start with one question.", heard)
        self.assertEqual(missing, [(3, "one")])
        self.assertEqual([w for _, w, _, _ in extra], ["um"])
        self.assertEqual(changed, [])

    def test_a_misheard_word_is_changed_not_extra(self):
        heard = [("Demak", 0, .8), ("ayrim", .8, 1), ("berilganlar", 1, 1.5), ("sonimiz", 1.5, 2.1), ("va", 2.1, 2.4),
                 ("toifa", 2.4, 2.8)]
        missing, extra, changed = T.script_check("Demak, ayrim berilganlar son emas, balki toifa", heard)
        self.assertEqual((missing, extra), ([], []))                  # nothing offered for cutting
        self.assertEqual(changed, [("son emas balki", "sonimiz va", 1.5, 2.4)])

    def test_script_check_ignores_apostrophe_styles(self):
        self.assertEqual(T.script_check("oʻn sakkiz", [("o'n", 0, 1), ("sakkiz", 1, 2)]), ([], [], []))


if __name__ == "__main__":
    unittest.main()
