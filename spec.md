# Spec

## Intent
Implements [`intent/classifier.md`](intent/classifier.md).

## Components

### classifier (`classify.py`) with eval runner (`eval.py`)
- **What it does:** Sends one support message plus a system prompt to a chat model, extracts a JSON
  object from the reply, validates the three fields, and prints the JSON. `eval.py` runs the
  classifier over the cases in `cases.json` and prints PASS/FAIL per case plus a summary line.
- **Language:** Python 3. **Why:** the `json`, `urllib`, and `re` modules cover everything with no
  dependencies, and last week's `chat.py` is reusable. Java was the alternative; it has no JSON
  parser in the standard library, so it would need a hand-written parser or a Jackson/Gson jar.
- **Model:** `minimax/minimax-m3` (class default). **Why:** compared against
  `xiaomi/mimo-v2.6-flash` on the same five cases; results in `CHECKS.md`. Both are cheap; the
  comparison checks whether a smaller flash model is good enough for a three-field classification.
- **Interfaces:** input is one command-line argument (the message). Output on stdout is one JSON
  object `{"category", "urgency", "reason"}`; a usage line goes to stderr. Exit code 0 on valid
  output, 1 on any failure. `eval.py` reads `cases.json`: a list of
  `{"id", "message", "expect_category": [..], "purpose"}`.
- **Dependencies:** none beyond the Python standard library and network access to OpenRouter.

## Behavior
1. A clear billing message (double charge) yields `category: billing`.
2. A clear technical message (app crashes / cannot log in) yields `category: technical`.
3. A clear sales message (pricing for more seats) yields `category: sales`.
4. An ambiguous message (a bug that caused a wrong charge) yields `billing` or `technical`; either passes.
5. A message that is not a support request yields `category: unknown`.

Every passing reply also has `urgency` in {low, medium, high} and a non-empty `reason` string.

## Failure handling
- **Reply is not JSON:** the classifier looks for the first `{...}` block (handles code fences and
  text around the JSON). If none parses, it prints an error with the raw reply and exits 1. The eval
  counts that case as FAIL ("not JSON") and continues; it never crashes.
- **Field out of the allowed set:** `category` or `urgency` outside the allowed values is an error,
  exit 1; the eval records FAIL with the bad value.
- **Empty reply:** reported as an error, including `finish_reason` so a `length` cutoff from hidden
  reasoning is visible; exit 1. `max_tokens` is set high (4000) to reduce this.
- **Missing key / env var:** error naming the variable, exit 1.
- **HTTP error or timeout (60 s):** error with status and body, exit 1.
- The model is told to use `unknown` rather than guess; hallucinated categories fail validation.

## Cost estimate
About 250 input and 60 output tokens per call (Week 2's usage line was in this range), so one eval
run is ~1,500 tokens. At well under $1 per million tokens for both models, a run costs a small
fraction of a cent; even 1,000 runs over the semester is under $1.

## Out of scope
Routing, replying, batch processing, a web UI, persistence. `response_format` is optional and the
eval does not depend on it.
