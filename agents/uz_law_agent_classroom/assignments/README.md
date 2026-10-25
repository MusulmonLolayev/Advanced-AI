# Assignments

The project is an open-source research agent over Uzbek law; the Labor Code is the starter corpus used in the course
videos. Optional assignments add another law or port the agent to the UK example corpus (see `STEPS.md`).

Every student works in their own folder, `assignments/<your-github-username>/`, and only there.

1. Fork the repository and clone your fork.
2. Copy the template: `cp -r assignments/_template assignments/<your-github-username>`
3. Do the work for each lecture step inside that folder (answers in `answers/`, notes and code beside them).
   The checks for each step are in [`STEPS.md`](../STEPS.md).
4. Submit by pull request. A pull request may change only files under `assignments/<your-github-username>/`;
   the `pr-scope` check fails otherwise (the folder name is compared without regard to case). Do not edit the
   agent, the tests, the template or another student's folder.
5. Make one small commit per change and tag nothing in the main repository; see [`CONTRIBUTING.md`](../CONTRIBUTING.md).

To run the check yourself before you push:

```bash
python scripts/check_pr_scope.py origin/main <your-github-username>
```
