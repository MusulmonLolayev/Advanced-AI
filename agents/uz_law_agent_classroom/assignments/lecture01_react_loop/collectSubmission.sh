#!/usr/bin/env bash
# Zip what you edited, plus the output of the self-checks. No network is used.
set -euo pipefail

FILES=(
    "uz_agent/agent.py"
    "lecture01_react_loop.ipynb"
)
CHECK_OUTPUT="self_check_output.txt"
ZIP="submission.zip"

for f in "${FILES[@]}"; do
    if [ ! -f "$f" ]; then
        echo "Required file $f not found, exiting." >&2
        exit 1
    fi
done

echo "### Running the self-checks ###"
# A failing check must not stop the zip: the output is part of the submission.
python3 -m uz_agent.self_checks 2>&1 | tee "$CHECK_OUTPUT" || true

echo "### Zipping ###"
rm -f "$ZIP"
zip -q "$ZIP" "${FILES[@]}" "$CHECK_OUTPUT"

echo "### Done. Submit $ZIP. ###"
