"""Agent course — the opening: who it is for, the road map, the shape of a section, the API, the testbed."""
from agents_course_kit import *

T2 = D["tau2"]


class S00Opening(LectureScene):
    def construct(self):
        title = txt(label("ac_course_title"), size=60, weight=BOLD, color=LBLUE)
        sub = txt(label("ac_course_sub"), size=32, color=GREY_B)
        head = VGroup(title, sub).arrange(DOWN, buff=0.4)
        with self.say("0.1") as (tr, t):
            self.play(FadeIn(title, shift=UP * 0.3), run_time=0.8)
            self.play(FadeIn(sub), run_time=0.6)
        self.play(FadeOut(head), run_time=0.4)

        # the eight sections as a stack: the loop at the bottom, evaluation on top
        names = [HEADS[n][LANG].split(" · ", 1)[1] for n in range(1, 9)]
        rows = stack(names, width=6.2, height=0.56, size=22,
                     colors=[RLBLUE] * 4 + [RLGREEN] * 3 + [RLRED])
        rows.move_to(ORIGIN)
        with self.say("0.2") as (tr, t):
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in rows], lag_ratio=0.25), run_time=2.4)
            self.cue(tr, t, {"en": "evaluation and safety"})
            self.play(Indicate(rows[-1], color=HILITE, scale_factor=1.05), run_time=0.8)

        # every section: problem → idea → code → failure; sections 1-2 run, the rest are shown
        tiles, arrows = flow_row([label("ac_problem"), label("ac_idea"), label("ac_code"), label("ac_failure")],
                                 color=GREY_B, size=24, width=2.3, height=0.85, buff=0.45)
        shape = VGroup(tiles, arrows).to_edge(UP, buff=SAFE + 0.35)
        pills = VGroup(*[(run_pill(16) if i < 2 else shown_pill(16)) for i in range(8)])
        with self.say("0.3") as (tr, t):
            self.play(rows.animate.scale(0.82).to_edge(DOWN, buff=SAFE + 0.5).shift(LEFT * 1.4), run_time=0.6)
            for p, r in zip(pills, rows):
                p.next_to(r, RIGHT, buff=0.3)
            self.play(LaggedStart(*[FadeIn(x) for x in tiles], lag_ratio=0.3), Create(arrows), run_time=1.6)
            self.cue(tr, t, {"en": "The first two sections"})
            self.play(FadeIn(pills[:2]), run_time=0.5)
            self.cue(tr, t, {"en": "later ones show"})
            self.play(LaggedStart(*[FadeIn(p) for p in pills[2:]], lag_ratio=0.15), run_time=1.0)
        self.clear_all()


class S00Testbed(LectureScene):
    def construct(self):
        # the client is three lines of real code; only base_url names the provider
        panel = code_panel("common.py", "def client", "api_key=os.environ", size=22, tag="run")
        panel.move_to(UP * 0.4)
        url = highlight(panel, code_lines("common.py", "base_url=")[0])
        with self.say("0.4") as (tr, t):
            self.play(FadeIn(panel), run_time=0.8)
            self.cue(tr, t, {"en": "We use DeepSeek"})
            self.play(Create(url), run_time=0.6)
        self.clear_all()

        # τ²-bench retail: a policy, 16 tools, 500 customers and 1,000 orders, and a simulated customer
        bench = txt(label("ac_tau2_retail"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        policy_rows = [r for r in (RAWDIR / "tau2_retail_policy.md").read_text().splitlines() if r.strip()][:9]
        page_txt = VGroup(*[txt(textwrap.shorten(r.replace("**", "").lstrip("#- "), 40, placeholder="…"), size=16, color=GREY_A)
                            for r in policy_rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        page = VGroup(RoundedRectangle(corner_radius=0.1, width=page_txt.width + 0.4, height=page_txt.height + 0.4,
                                       stroke_color=GREY_B, stroke_width=2), page_txt)
        page_txt.move_to(page[0])
        page_cap = txt(label("ac_policy"), size=24, color=GREY_B).next_to(page, UP, buff=0.15)
        tools = raw("tau2_retail_tools.json")["tools"]
        grid = VGroup(*[mono(x["name"], size=15, color=HILITE if x["type"] == "WRITE" else LBLUE) for x in tools])
        grid.arrange_in_grid(rows=8, cols=2, buff=(0.3, 0.14), col_alignments="ll")
        grid_cap = tagged(len(tools), label("ac_tools"), size=24, color=GREY_B).next_to(grid, UP, buff=0.15)
        db = VGroup(tagged(f"{T2['retail_users']:,}", label("ac_customers"), size=28),
                    tagged(f"{T2['retail_orders']:,}", label("ac_orders"), size=28)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        first_user = next(m["content"] for m in raw("tau2_retail_trajectory.json")["messages"] if m["role"] == "user")
        customer = bubble("user", first_user, max_chars=30, max_rows=4, size=18)
        cust_cap = txt(label("ac_simulated_customer"), size=22, color=GREY_B).next_to(customer, UP, buff=0.12)
        left = VGroup(page_cap, page)
        mid = VGroup(grid_cap, grid)
        right = VGroup(db, VGroup(cust_cap, customer)).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        layout = VGroup(left, mid, right).arrange(RIGHT, buff=0.6, aligned_edge=UP).next_to(bench, DOWN, buff=0.5)
        layout.scale_to_fit_width(12.6)
        layout.move_to(DOWN * 0.45)
        with self.say("0.5") as (tr, t):
            self.play(FadeIn(bench), run_time=0.5)
            self.cue(tr, t, {"en": "a written policy"})
            self.play(FadeIn(left), run_time=0.6)
            self.cue(tr, t, {"en": "sixteen tools"})
            self.play(FadeIn(grid_cap), LaggedStart(*[FadeIn(g) for g in grid], lag_ratio=0.05), run_time=1.0)
            self.cue(tr, t, {"en": "five hundred customers"})
            self.play(FadeIn(db), run_time=0.6)
            self.cue(tr, t, {"en": "An AI plays the customer"})
            self.play(FadeIn(cust_cap), FadeIn(customer, shift=RIGHT * 0.2), run_time=0.6)
        self.clear_all()


SCENES = ["S00Opening", "S00Testbed"]
