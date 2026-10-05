"""Run the classifier over the cases in cases.json and print PASS/FAIL per case.

Usage:
    python3 eval.py [cases.json]

Uses the same environment variables as classify.py.
"""

import json
import os
import sys

from classify import ClassifyError, classify


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "cases.json"
    with open(path, encoding="utf-8") as f:
        cases = json.load(f)

    passed = 0
    tokens_in = tokens_out = 0
    for case in cases:
        try:
            result, usage = classify(case["message"])
        except ClassifyError as e:
            print(f"FAIL  case {case['id']}: {e}")
            continue
        tokens_in += usage.get("prompt_tokens") or 0
        tokens_out += usage.get("completion_tokens") or 0
        # A case passes when the category is one of the accepted answers.
        if result["category"] in case["expect_category"]:
            passed += 1
            print(f"PASS  case {case['id']}: {result['category']} / {result['urgency']}")
        else:
            print(f"FAIL  case {case['id']}: got {result['category']}, "
                  f"expected {' or '.join(case['expect_category'])} ({result['reason']})")

    print(f"\n{passed}/{len(cases)} passed | model: {os.environ.get('CHAT_MODEL')} | "
          f"tokens in: {tokens_in} | tokens out: {tokens_out}")


if __name__ == "__main__":
    main()
