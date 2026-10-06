# /// script
# requires-python = ">=3.10"
# dependencies = ["typellm==0.6.0", "typesafe-sdk==0.7.2"]
# ///
"""Sort emails into urgent / needs_reply / fyi / noise / phishing.

Modes:
  full     Jev takes a fast first pass and closes the clear fyi, noise and
           phishing emails itself. Everything else goes to TypeLLM.
  typellm  TypeLLM reads every email.
  jev      Jev sorts every email on its own. Fastest, but it can't pull out
           requested_time or amount, so those are always null.

TypeLLM also pulls out the requested time and money amount.

Usage:  uv run triage.py emails.json [--mode full|typellm|jev]   (default: full)
Input:  [{"id": "...", "from": "...", "subject": "...", "body": "..."}, ...]
Output: JSON list, same order, one result per email.
Needs TYPELLM_API_KEY (full, typellm) and TYPESAFE_API_KEY (full, jev).
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor

from typellm import TypeLLMClient
from typesafe_sdk import TypeSafeClient

MODES = ("full", "typellm", "jev")

JEV_CAN_CLOSE = {"fyi", "noise", "phishing"}
MIN_CONFIDENCE = 0.9  # ponytail: one global threshold, tune per bucket if misroutes show up

FIRST_PASS = {
    "bucket": {
        "type": "choice",
        "instructions": "Triage this email for a small computer repair shop.",
        "criteria": {
            "needs_attention": "A real person wants something from the shop, or something "
                               "has gone wrong: a customer, supplier, review or deadline.",
            "fyi": "Nothing to do: receipts, payouts, confirmations, auto-replies, "
                   "thank-yous, notices that need no action.",
            "noise": "Marketing, newsletters, promotions, webinars.",
            "phishing": "Pretends to be a known service to get a click, login or attachment opened.",
        },
    },
}

# Jev on its own has to pick all five buckets.
JEV_ONLY = {
    "bucket": {
        "type": "choice",
        "instructions": "Triage this email for a small computer repair shop. Judge by what "
                        "is at stake, not by words like 'URGENT' or 'no rush'.",
        "criteria": {
            "urgent": "The shop should act today: something is down, data or money is at "
                      "risk, a deadline is close, a customer is unhappy or a bad review is "
                      "public, or a supplier has blocked the account.",
            "needs_reply": "A real person wants an answer, but it can wait a few days.",
            "fyi": FIRST_PASS["bucket"]["criteria"]["fyi"],
            "noise": FIRST_PASS["bucket"]["criteria"]["noise"],
            "phishing": FIRST_PASS["bucket"]["criteria"]["phishing"],
        },
    },
}

QUESTIONS = {
    "bucket": {
        "type": "string",
        "enum": ["urgent", "needs_reply", "fyi", "noise", "phishing"],
        "instructions": (
            "Triage this email for a small computer repair shop. Judge by what is "
            "actually at stake, not by words like 'URGENT' or 'no rush'.\n"
            "urgent: the shop should act today: something is down, data or money is "
            "at risk, a deadline is close, a customer is unhappy or a bad review is "
            "public, a supplier has blocked the account, or someone needs a time "
            "confirmed soon.\n"
            "needs_reply: a real person wants an answer, but it can wait a few days.\n"
            "fyi: nothing to do: receipts, payouts, confirmations, auto-replies, "
            "thank-yous, notices that need no action.\n"
            "noise: marketing, newsletters, promotions, webinars.\n"
            "phishing: pretends to be a known service to get a click, login or "
            "attachment opened."
        ),
    },
    "needs_reply": {
        "type": "boolean",
        "instructions": "Does a person at the shop need to write back?",
    },
    "requested_time": {
        "type": ["string", "null"],
        "instructions": "The date or time the sender asks for or is working to, "
                        "copied verbatim from the email, or null.",
    },
    "amount": {
        "type": ["number", "null"],
        "instructions": "The main money amount in the email, or null.",
    },
    "reason": {
        "type": "string",
        "instructions": "One short sentence explaining the bucket.",
        "depends_on": ["bucket"],
    },
}

def jev_result(answer):
    return {"bucket": answer.choice, "needs_reply": answer.choice in ("urgent", "needs_reply"),
            "requested_time": None, "amount": None,
            "reason": f"Jev: {answer.choice} ({answer.confidence:.0%} sure)"}


def triage(email, mode, jev, llm):
    text = f"From: {email['from']}\nSubject: {email['subject']}\n\n{email['body']}"
    if mode == "jev":
        result, route = jev_result(jev.system_one(state=text, questions=JEV_ONLY).answers["bucket"]), "jev"
    else:
        first = jev.system_one(state=text, questions=FIRST_PASS).answers["bucket"] if mode == "full" else None
        if first and first.choice in JEV_CAN_CLOSE and first.confidence >= MIN_CONFIDENCE:
            result, route = jev_result(first), "jev"
        else:
            result = llm.generate(context=text, questions=QUESTIONS, temperature=0, seed=42).result
            route = "typellm"
    return {"id": email["id"], **result, "route": route}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("emails")
    parser.add_argument("--mode", choices=MODES, default="full")
    args = parser.parse_args()
    emails = json.load(open(args.emails))
    jev = TypeSafeClient() if args.mode != "typellm" else None
    llm = TypeLLMClient() if args.mode != "jev" else None
    # TypeLLM's hosted API allows 4 requests in flight per key.
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = pool.map(lambda e: triage(e, args.mode, jev, llm), emails)
        print(json.dumps(list(results), indent=2, ensure_ascii=False))
