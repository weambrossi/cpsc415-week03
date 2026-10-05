# Project conventions

<!-- The agent reads this at the start of every session. Keep it short and current.
     Graded: does it reflect how the team actually works? -->

## What this repository is
A command-line classifier that sends one customer-support message to a chat model and prints
JSON with `category`, `urgency`, and `reason`, plus a five-case eval run against two models.
See [`spec.md`](spec.md).

## Commands
```
# run       python3 classify.py "message text"
# eval      python3 eval.py            (reads cases.json)
# env       CHAT_BASE_URL, CHAT_MODEL, OPENROUTER_API_KEY
```

## Conventions
- Language: Python 3, standard library only.
- Default model: minimax/minimax-m3 (class model); comparison model: xiaomi/mimo-v2.6-flash.
- File naming: lowercase snake_case for code and data (`classify.py`, `cases.json`); UPPERCASE for chain docs.

## Working rules

For an introductory lab, follow its explicitly assigned stages; the full chain below applies to major projects. Week 1 uses its own minimal repository.

- Write or update `intent/` and `spec.md` before code. Get `plan.md` approved before implementing.
- One feature per branch and pull request. Never push to `main` directly.
- Never commit `.env` or `.claude/settings.local.json`.
- This is the Week 3 introductory lab. Stages assigned: intent and spec.
  No plan.md, no branches or pull requests. Commit to main.
- Standard library only, except that Java may add one JSON library jar.

## Common mistakes
Things the agent got wrong before and must not repeat. Add to this list as they happen.
