# Checks

Eval results, one row per run. Same five cases (`cases.json`) and same prompt for every model.
Run on 2026-10-05 through OpenRouter.

| Run | Model | Passed | Failed case(s) and how | Judgment call or real? | Tokens in / out |
|---|---|---|---|---|---|
| 1 | minimax/minimax-m3 | 5/5 | none | n/a | 1552 / 772 |
| 2 | xiaomi/mimo-v2.6-flash | 5/5 | none | n/a | 809 / 510 |

Per-case answers (category / urgency):

| Case | Expect | minimax-m3 | mimo-v2.6-flash |
|---|---|---|---|
| 1 double charge | billing | billing / high | billing / medium |
| 2 app crash | technical | technical / high | technical / high |
| 3 enterprise pricing | sales | sales / medium | sales / medium |
| 4 checkout error + charge | billing or technical | technical / high | billing / high |
| 5 banana bread | unknown | unknown / low | unknown / low |

## What differed
Both models passed every case, and both returned `unknown` for the non-support message. They
split on the ambiguous case 4 (minimax chose technical, mimo chose billing), which is why that
case accepts either; they also differed on urgency for case 1 (high vs. medium), which the eval
does not judge because urgency is a judgment call. mimo-v2.6-flash used about half the input
tokens and two-thirds of the output tokens for the same results.
