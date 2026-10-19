"""Unit tests for studio/timeline.py: takes, tracks, cuts, nudges, the edit list, subtitles, the script check.

    uv run python -m unittest discover -s studio -p 'test_timeline.py'        (from video/)
"""
import random
import unittest

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
        e = T.edited(self.take, self.ev, {"trim_in": 0.5, "trim_out": 1.0, "cuts": [(12.0, 12.5)], "nudge": 0.2})
        self.assertAlmostEqual(T.length(e["voice"]), 14 - 0.5 - 1.0 - 0.5 + 0.2)
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
                    "trim_in": 0.001, "nudge": rnd.choice([0, 0.4, -0.7])}
            ed = T.edited(take, ev, edit)
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
