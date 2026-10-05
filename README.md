# CPSC 415 Week 3: support-message classifier with a five-case eval

Classifies one customer-support message as `billing`, `technical`, `sales`, or `unknown`, with an
urgency and a one-sentence reason, and evaluates that against five known cases on two models.
Chain artifacts: [`intent/classifier.md`](intent/classifier.md) → [`spec.md`](spec.md).

## How to run

```bash
export OPENROUTER_API_KEY=...            # never commit this
export CHAT_BASE_URL=https://openrouter.ai/api/v1
export CHAT_MODEL=minimax/minimax-m3
python3 classify.py "I was charged twice this month"
python3 eval.py                          # runs cases.json
CHAT_MODEL=xiaomi/mimo-v2.6-flash python3 eval.py
```

Python 3 standard library only. If you get `CERTIFICATE_VERIFY_FAILED` with the python.org
installer, run its `Install Certificates.command` once, or `export SSL_CERT_FILE=/etc/ssl/cert.pem`.

## The five cases

| # | Expect | What it is there to catch |
|---|---|---|
| 1 | billing | Double charge. Baseline: a model that fails this cannot do the task. |
| 2 | technical | App crash after update. A plain bug report, no money involved. |
| 3 | sales | Enterprise pricing for 40 seats. Mentions price, so it catches "price ⇒ billing" confusion. |
| 4 | billing or technical | Checkout error *and* a charge. Genuinely ambiguous; either answer passes. |
| 5 | unknown | Banana-bread recipe. Not a support request; catches a model forcing everything into a category. |

## Comparison

| Model | Passed | Tokens in / out |
|---|---|---|
| minimax/minimax-m3 | 5/5 | 1552 / 772 |
| xiaomi/mimo-v2.6-flash | 5/5 | 809 / 510 |

Both models passed every case, but they split on the ambiguous case 4 (minimax said technical,
mimo said billing) and on the urgency of case 1. mimo-v2.6-flash reached the same results with
roughly half the tokens. Details in [`CHECKS.md`](CHECKS.md).

## A correction I made to the spec

The first draft only validated `category`. I added that `urgency` must also be in
{low, medium, high} and `reason` must be non-empty, because otherwise a reply like
`{"category": "billing"}` would pass the eval while missing two-thirds of what the intent asks for.

## One line I can explain

In `classify.py`, `extract_json`:

```python
match = re.search(r"\{.*\}", reply, re.DOTALL)
```

If the reply is not pure JSON (models often wrap it in ```` ```json ```` fences or add a sentence),
this grabs the span from the first `{` to the last `}` across newlines and parses that. If nothing
parses, it raises `ClassifyError`, which the eval records as FAIL instead of crashing.
