#!/usr/bin/env python3
import json
from pathlib import Path

path = Path("verification/tests/fixture_submission.json")
data = json.loads(path.read_text(encoding="utf-8"))

expected = {
    "fixture_flip": [
        {
            "attempt_1": [[0, 4], [6, 5]],
            "attempt_2": [[0, 4], [6, 5]]
        }
    ]
}

if data != expected:
    raise SystemExit(f"Unexpected submission: {data!r}")

print("fixture submission OK")
