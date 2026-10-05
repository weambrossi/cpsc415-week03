# Intent: support-message classifier

## Goal
A small program that takes one customer-support message, asks a model to classify it, and prints
JSON saying what kind of request it is, how urgent it is, and why, in one sentence.

## Who it is for
A support team triaging an inbox. Today someone reads every message and routes it by hand.

## Constraints
- Python 3, standard library only.
- Calls go through OpenRouter's chat-completions API; the key comes from `OPENROUTER_API_KEY`.
- Category must be exactly one of `billing`, `technical`, `sales`, `unknown`.
- Urgency must be exactly one of `low`, `medium`, `high`.
- Cheap models only; a full eval run should cost well under a cent.

## Not in scope
Routing, replying to the customer, batch processing of an inbox, a web interface, storing results.

## Success looks like
- `python3 classify.py "I was charged twice this month"` prints valid JSON with `category: billing`.
- A message that is not a support request (e.g. a recipe question) yields `category: unknown`.
- A five-case eval prints PASS/FAIL per case and a summary line, against two different models.

## Open questions
None blocking. Whether `response_format` JSON schema helps is an optional experiment.

**Approved by:** Ethan Ambrossi, 2026-10-05
