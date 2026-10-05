"""Classify one customer-support message and print JSON with category, urgency, and reason.

Usage:
    python3 classify.py "message text"

Environment:
    CHAT_BASE_URL       API address, e.g. https://openrouter.ai/api/v1
    CHAT_MODEL          model ID, e.g. minimax/minimax-m3
    OPENROUTER_API_KEY  your OpenRouter key (never put it in this file)
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

CATEGORIES = {"billing", "technical", "sales", "unknown"}
URGENCIES = {"low", "medium", "high"}
MAX_TOKENS = 4000

SYSTEM_PROMPT = """You classify customer-support messages.
Reply with ONLY a JSON object, no other text, in exactly this form:
{"category": "...", "urgency": "...", "reason": "..."}
category: one of billing, technical, sales, unknown.
  billing = charges, refunds, invoices, payments on an existing account.
  technical = bugs, errors, crashes, login or access problems.
  sales = pricing questions, plans, upgrades, buying more.
  unknown = anything that is not a support request, or that you cannot place. Do not guess.
urgency: one of low, medium, high.
reason: one sentence explaining the category."""


class ClassifyError(Exception):
    """Raised when the model's reply cannot be turned into a valid classification."""


def call_model(message):
    """Send the message to the model. Returns (reply_text, usage, finish_reason)."""
    base_url = os.environ.get("CHAT_BASE_URL")
    model = os.environ.get("CHAT_MODEL")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    for name, value in [("CHAT_BASE_URL", base_url), ("CHAT_MODEL", model),
                        ("OPENROUTER_API_KEY", api_key)]:
        if not value:
            raise ClassifyError(f"{name} is not set")

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "max_tokens": MAX_TOKENS,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
    except urllib.error.HTTPError as e:
        raise ClassifyError(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise ClassifyError(f"could not reach {base_url}: {e}")

    if "error" in data:
        raise ClassifyError(str(data["error"].get("message", data["error"])))
    choice = data["choices"][0]
    reply = (choice["message"].get("content") or "").strip()
    return reply, data.get("usage", {}), choice.get("finish_reason")


def extract_json(reply):
    """Find the JSON object in the reply, even if wrapped in code fences or prose."""
    try:
        return json.loads(reply)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost {...} span: tolerates ```json fences and text around the object.
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise ClassifyError(f"reply is not JSON: {reply!r}")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        raise ClassifyError(f"reply is not JSON: {reply!r}")


def validate(result):
    """Check the three fields against the allowed values. Returns the cleaned result."""
    if not isinstance(result, dict):
        raise ClassifyError(f"expected a JSON object, got {result!r}")
    category = str(result.get("category", "")).strip().lower()
    urgency = str(result.get("urgency", "")).strip().lower()
    reason = str(result.get("reason", "")).strip()
    if category not in CATEGORIES:
        raise ClassifyError(f"category out of allowed set: {result.get('category')!r}")
    if urgency not in URGENCIES:
        raise ClassifyError(f"urgency out of allowed set: {result.get('urgency')!r}")
    if not reason:
        raise ClassifyError("reason is empty")
    return {"category": category, "urgency": urgency, "reason": reason}


def classify(message):
    """Classify one message. Returns (result_dict, usage). Raises ClassifyError on failure."""
    reply, usage, finish_reason = call_model(message)
    if not reply:
        raise ClassifyError(f"empty reply (finish_reason={finish_reason})")
    return validate(extract_json(reply)), usage


def main():
    if len(sys.argv) != 2:
        print('usage: python3 classify.py "message text"', file=sys.stderr)
        sys.exit(1)
    try:
        result, usage = classify(sys.argv[1])
    except ClassifyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2))
    print(f"model: {os.environ.get('CHAT_MODEL')} | input tokens: {usage.get('prompt_tokens')} | "
          f"output tokens: {usage.get('completion_tokens')}", file=sys.stderr)


if __name__ == "__main__":
    main()
