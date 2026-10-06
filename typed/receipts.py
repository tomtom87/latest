# /// script
# requires-python = ">=3.10"
# dependencies = ["typellm==0.6.0", "pypdfium2", "pillow"]
# ///
"""Read receipts and invoices (PDF, JPG, PNG) into typed fields with TypeLLM.

Usage:  uv run receipts.py [files or folders...]   (default: this folder)
Prints a table, and checks against expected.json when it sits next to the files.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pypdfium2
from typellm import TypeLLMClient

GREEN, RED, DIM, BOLD, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"
TYPES = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
FIELDS = ["vendor", "number", "date", "subtotal", "tax", "total"]

QUESTIONS = {
    "doc_type": {"type": "string", "enum": ["receipt", "invoice", "quote", "other"]},
    "vendor": {"type": "string", "instructions": "Who issued it: the business name only."},
    "number": {"type": ["string", "null"],
               "instructions": "The receipt or invoice number exactly as printed, without a leading #."},
    "date": {"type": ["string", "null"], "instructions": "Issue or payment date as YYYY-MM-DD."},
    "currency": {"type": "string", "enum": ["USD", "GBP", "EUR", "other"]},
    "subtotal": {"type": ["number", "null"]},
    "tax": {"type": ["number", "null"]},
    "total": {"type": "number", "instructions": "The final amount paid or due."},
    "line_items": {
        "type": "array",
        "instructions": "Every purchased line.",
        "items": {"type": "object", "properties": {
            "description": {"type": "string"},
            "quantity": {"type": "integer"},
            "amount": {"type": "number", "instructions": "Line total."},
        }},
    },
}

client = TypeLLMClient()


def pages(path):
    """A PDF becomes one image per page; an image is passed as is."""
    if path.suffix.lower() != ".pdf":
        return [str(path)]
    # ponytail: every page is sent, cap it if long PDFs show up
    return [page.render(scale=2).to_pil() for page in pypdfium2.PdfDocument(path)]


def read(path):
    return client.generate(context=f"Attached: {path.name}. Read this document.",
                           images=pages(path), questions=QUESTIONS,
                           temperature=0, seed=42).result


def matches(field, got, want):
    if isinstance(want, float):
        return got is not None and abs(got - want) < 0.005
    return str(want).lower() in str(got or "").lower()


if __name__ == "__main__":
    args = [Path(a) for a in sys.argv[1:]] or [Path(__file__).parent]
    files = sorted(f for a in args for f in ([a] if a.is_file() else a.iterdir())
                   if f.suffix.lower() in TYPES)
    if not files:
        sys.exit("No PDF, JPG or PNG files found.")
    expected_path = files[0].parent / "expected.json"
    expected = json.load(open(expected_path)) if expected_path.exists() else {}

    print(f"{DIM}Reading {len(files)} documents with TypeLLM…{RESET}\n")
    t = time.perf_counter()
    # TypeLLM's hosted API allows 4 requests in flight per key.
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(read, files))
    elapsed = time.perf_counter() - t

    right = checked = 0
    for f, r in zip(files, results):
        want = expected.get(f.name, {})
        print(f"{BOLD}{f.name}{RESET}  {DIM}{r['doc_type']}, {r['currency']}{RESET}")
        for field in FIELDS:
            mark = " "
            if field in want:
                ok = matches(field, r[field], want[field])
                right, checked = right + ok, checked + 1
                mark = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET} {DIM}(expected {want[field]}){RESET}"
            print(f"  {field:9} {str(r[field]):32} {mark}")
        for item in r["line_items"]:
            print(f"  {DIM}• {item['quantity']} × {item['description'][:34]:34} {item['amount']:>9.2f}{RESET}")
        print()

    summary = f"{right}/{checked} fields correct, " if checked else ""
    print(f"{BOLD}{summary}{len(files)} documents in {elapsed:.1f}s{RESET}")
