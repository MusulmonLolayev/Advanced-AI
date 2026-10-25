"""The pull-request scope rule: a student changes only assignments/<their username>/."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from check_pr_scope import outside_scope, read_maintainers  # noqa: E402


class Scope(unittest.TestCase):
    def test_inside_the_own_folder_is_fine(self):
        self.assertEqual(outside_scope(["assignments/alice/answers/l1.md", "assignments/alice/notes.md"], "alice"), [])

    def test_outside_the_folder_fails(self):
        self.assertEqual(outside_scope(["agent.py", "assignments/alice/a.md"], "alice"), ["agent.py"])
        self.assertEqual(outside_scope(["assignments/README.md"], "alice"), ["assignments/README.md"])
        self.assertEqual(outside_scope(["assignments/_template/README.md"], "alice"), ["assignments/_template/README.md"])

    def test_another_students_folder_fails(self):
        self.assertEqual(outside_scope(["assignments/bob/a.md"], "alice"), ["assignments/bob/a.md"])
        self.assertEqual(outside_scope(["assignments/alicia/a.md"], "alice"), ["assignments/alicia/a.md"])

    def test_the_folder_name_is_case_insensitive(self):
        self.assertEqual(outside_scope(["assignments/Alice/a.md"], "alice"), [])
        self.assertEqual(outside_scope(["assignments/alice/a.md"], "ALICE"), [])

    def test_maintainers_may_change_anything(self):
        self.assertEqual(outside_scope(["agent.py", "assignments/bob/a.md"], "Boss", {"boss"}), [])
        self.assertEqual(read_maintainers("# owners\nBoss  # the instructor\n\n  carol\n"), {"boss", "carol"})
        self.assertEqual(outside_scope(["agent.py"], "alice", read_maintainers("# nobody\n")), ["agent.py"])

    def test_path_traversal_fails(self):
        self.assertEqual(outside_scope(["assignments/alice/../bob/x"], "alice"), ["assignments/alice/../bob/x"])
        self.assertEqual(outside_scope(["assignments/alice/../../agent.py"], "alice"), ["assignments/alice/../../agent.py"])
        self.assertEqual(outside_scope(["assignments/alice/./a.md"], "alice"), [])

    def test_a_bare_file_named_like_the_folder_fails(self):
        self.assertEqual(outside_scope(["assignments/alice"], "alice"), ["assignments/alice"])

    def test_an_absolute_path_fails(self):
        self.assertEqual(outside_scope(["/assignments/alice/a.md"], "alice"), ["/assignments/alice/a.md"])


if __name__ == "__main__":
    unittest.main()
