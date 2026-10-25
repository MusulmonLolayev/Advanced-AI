"""Unit tests for make_student.py.

    python -m unittest agents/uz_law_agent_classroom/tools/test_make_student.py      (from the repository root)
    python -m unittest test_make_student                                             (from tools/)
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import make_student as ms  # noqa: E402

BANNER = '''    ##########################################################################
    # TODO: add one.                                                         #
    ##########################################################################
'''
SOLUTION = f'''import os


def add_one(x):
    """Doc."""
{BANNER}    {ms.START}
    y = x + 1
    return y
    {ms.END}


class K:
    def method(self):
        if True:
            {ms.START}
            z = 1
            {ms.END}
        return 2
'''


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


class Blank(unittest.TestCase):
    def test_a_block_is_blanked_and_the_banner_and_markers_stay(self):
        out = ms.blank_blocks(SOLUTION)
        self.assertNotIn("y = x + 1", out)
        self.assertNotIn("return y", out)
        self.assertIn("# TODO: add one.", out)
        self.assertEqual(out.count(ms.START), 2)
        self.assertEqual(out.count(ms.END), 2)
        self.assertIn('raise NotImplementedError("TODO: add_one")', out)

    def test_text_outside_the_blocks_is_untouched(self):
        out = ms.blank_blocks(SOLUTION)
        for line in ("import os", "def add_one(x):", '    """Doc."""', "class K:", "        return 2"):
            self.assertIn(line, out.split("\n"))

    def test_indentation_is_that_of_the_marker_and_the_method_name_is_used(self):
        out = ms.blank_blocks(SOLUTION).split("\n")
        self.assertIn('    raise NotImplementedError("TODO: add_one")', out)
        self.assertIn('            raise NotImplementedError("TODO: method")', out)

    def test_the_result_is_valid_python_that_raises(self):
        ns = {}
        exec(compile(ms.blank_blocks(SOLUTION), "s", "exec"), ns)
        with self.assertRaises(NotImplementedError) as cm:
            ns["add_one"](1)
        self.assertEqual(str(cm.exception), "TODO: add_one")

    def test_running_it_on_its_own_output_changes_nothing(self):
        once = ms.blank_blocks(SOLUTION)
        self.assertEqual(ms.blank_blocks(once), once)

    def test_unbalanced_markers_are_rejected(self):
        with self.assertRaisesRegex(ms.MarkerError, "never closed"):
            ms.blank_blocks(f"def f():\n    {ms.START}\n    x = 1\n")
        with self.assertRaisesRegex(ms.MarkerError, "END without a START"):
            ms.blank_blocks(f"def f():\n    x = 1\n    {ms.END}\n")

    def test_nested_markers_are_rejected(self):
        with self.assertRaisesRegex(ms.MarkerError, "nested"):
            ms.blank_blocks(f"def f():\n    {ms.START}\n    {ms.START}\n    {ms.END}\n    {ms.END}\n")

    def test_the_solution_lines_are_listed_for_the_leak_check(self):
        self.assertEqual(ms.solution_lines(SOLUTION)[:2], [("add_one", "    y = x + 1"), ("add_one", "    return y")])


class Copy(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sol, self.stu = self.tmp / "sol", self.tmp / "stu"
        (self.sol / "pkg").mkdir(parents=True)
        (self.sol / "pkg" / "a.py").write_text(SOLUTION)
        (self.sol / "README.md").write_text(f"Quote: `{ms.START}` in prose stays.\n")
        (self.sol / "__pycache__").mkdir()
        (self.sol / "__pycache__" / "x.pyc").write_bytes(b"x")
        (self.sol / ".env").write_text("LLM_API_KEY=secret\n")
        (self.sol / "secret_notes.txt").write_text("solution only\n")
        (self.sol / ".studentignore").write_text("# comment\nsecret_*.txt\n")

    def test_copy_skips_what_it_should_and_blanks_python_only(self):
        n = ms.make_student(self.sol, self.stu)
        self.assertEqual(n, 2)
        self.assertEqual(sorted(tree(self.stu)), ["README.md", "pkg/a.py"])
        self.assertIn(ms.START, (self.stu / "README.md").read_text())
        self.assertNotIn("y = x + 1", (self.stu / "pkg" / "a.py").read_text())

    def test_twice_gives_identical_output(self):
        ms.make_student(self.sol, self.stu)
        first = tree(self.stu)
        ms.make_student(self.sol, self.stu, replace=True)
        self.assertEqual(tree(self.stu), first)

    def test_an_existing_folder_is_not_overwritten_without_replace(self):
        ms.make_student(self.sol, self.stu)
        with self.assertRaises(SystemExit):
            ms.make_student(self.sol, self.stu)

    def test_the_student_folder_cannot_sit_inside_the_solution(self):
        with self.assertRaises(SystemExit):
            ms.make_student(self.sol, self.sol / "pkg" / "out", replace=True)


if __name__ == "__main__":
    unittest.main()
