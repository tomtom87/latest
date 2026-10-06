---
name: latest
description: Inbox and calendar catch-up. Use when the user says "latest", "catch me up", "check my inbox", "what's new", "anything urgent", or asks what needs their attention. Reads new Gmail threads, checks Google Calendar for conflicts, sorts emails by urgency, drafts friendly replies using our services info, labels every thread it has handled so it is never processed twice, and finishes with a short digest.
---

# Latest — Inbox & Calendar Catch-up

Goal: the user runs this skill instead of opening their inbox. You read what's new, work out what matters, draft replies, tag what you've handled, and hand back a clear summary.

**Never send emails.** Only create drafts. The user reviews and sends.

## Tools

- Gmail MCP: `search_threads`, `get_thread`, `list_labels`, `create_label`, `label_thread`, `create_draft`, `list_drafts`, `get_draft`, `update_draft`
- Google Calendar MCP: `list_calendars`, `list_events`, `suggest_time`
- Services info: [services.md](services.md) (read it every run — it is the only source for prices, services and policies)

## Labels

Two Gmail labels track progress. Create them on first run if `list_labels` doesn't show them.

| Label | Meaning |
|---|---|
| `Claude/Digested` | Read and included in a digest. Applied to **every** thread processed. |
| `Claude/Replied` | A reply draft was created for this thread. |

These labels are how you avoid confusion between runs. A thread with `Claude/Digested` is done — skip it unless a new message has arrived since (see Step 2).

## Working log

One Gmail draft acts as your memory between runs. It is **never sent** and has no recipient.

- **Subject:** `[Claude] Latest — working log` (exact, so you can find it)
- **To:** leave empty

**Format** (plain text, replace the whole body each run):

```
LAST RUN: 2026-09-30 14:05

OPEN ITEMS (waiting on user or on a reply)
- [thread subject] — [sender] — [what's pending] — since 2026-09-29
- ...

RECENT RUNS (newest first, max 5)
- 2026-09-30 14:05 — 12 read, 4 drafted, 1 urgent
- 2026-09-29 09:12 — 8 read, 3 drafted, 0 urgent
```

**Keep it small:**
- Only three sections: last run, open items, recent runs.
- Recent runs: keep 5 lines max, drop the oldest.
- Open items: remove an item once the user has sent the reply, the sender has replied, or it is older than 14 days.
- No email bodies, no draft text, no FYI/noise items. One line per item.
- Whole log should stay under ~40 lines. If it's bigger, prune.

## Step 0 — Read the working log

1. `list_drafts` and find the one with subject `[Claude] Latest — working log`, then `get_draft`.
2. If it doesn't exist, this is the first run — create it at the end (Step 8).
3. Use `LAST RUN` to scope the search in Step 2 and to say "since [time]" in the digest.
4. Check each open item: has the user sent the draft? Has the sender replied? Use this to update the list in Step 8 and mention anything still pending in the digest.
5. If the log looks broken or unreadable, don't guess — rebuild it fresh at the end and mention it in the digest.

## Step 1 — Get the calendar picture

1. `list_events` from now to 14 days ahead on the primary calendar.
2. Note: today's events, tomorrow's events, and busy blocks. Keep this in mind for any email that mentions a meeting, appointment, visit, call or deadline.

## Step 2 — Find new email

1. `search_threads` with query: `in:inbox -label:Claude/Digested after:[LAST RUN date]` (first run: `newer_than:14d`). The label is the real safety net — anything already tagged is skipped even if dates overlap.
2. Also catch replies on old threads: `search_threads` with `in:inbox label:Claude/Digested is:unread`. If the newest message in the thread is after the last time we labelled it, treat it as new.
3. Don't draft a second reply on a thread that already has a Claude draft waiting — check `list_drafts` first. Mention it's still waiting instead.
4. If nothing is found, tell the user "Inbox clear — nothing new since [LAST RUN]", show today's calendar and any open items, update the log's `LAST RUN` and recent runs (Step 8), then stop.

## Step 3 — Read and sort

For each thread, `get_thread` and put it in one bucket:

| Bucket | What goes here |
|---|---|
| 🔴 **Urgent** | Needs action today: customer waiting on an answer, complaint, payment problem, deadline today/tomorrow, meeting request for the next 48 hours, anything from a known important contact. |
| 🟡 **Needs reply** | A real person wants an answer but it can wait a day or two: quotes, general enquiries, scheduling further out. |
| 🔵 **FYI** | Worth knowing, no reply needed: confirmations, receipts, updates, shipping notices. |
| ⚪ **Noise** | Newsletters, marketing, automated alerts, spam-ish. |

When unsure between two buckets, pick the more urgent one.

## Step 4 — Check the calendar before replying

For any email that asks for a time, date, meeting or appointment:

1. Check the requested time against the events from Step 1.
2. If free → confirm it in the draft.
3. If it clashes → say so in the draft and offer 2–3 free alternatives. Use `suggest_time` to find them, keeping to normal working hours.
4. Never create or accept calendar events. Just note in the digest that one may be needed.

## Step 5 — Draft replies

Draft a reply for every 🔴 and 🟡 email. Skip 🔵 and ⚪.

Use `create_draft` as a reply on the same thread, so it sits in the conversation.

**Tone:** friendly, warm, clear, business-like. Plain English. No jargon, no buzzwords, no long sentences. Write like a helpful person, not a company.

**Rules:**
- Answer what they actually asked, first.
- Use only facts from [services.md](services.md) for prices, services, turnaround times and policies. If the answer isn't in there, don't guess — write a placeholder like `[CONFIRM: price for X]` and flag it in the digest.
- Include a clear next step (book a time, reply with details, call us).
- Keep it short — usually 3–6 sentences.
- Sign off with the sign-off from services.md.

**Example:**

> Hi Sarah,
>
> Thanks for getting in touch. Yes, we can help with that — it's usually £60 and takes about two days.
>
> I'm free on Thursday at 10am or Friday at 2pm if you'd like to drop it in. Just let me know which works best.
>
> Kind regards,
> [Name]

## Step 6 — Tag what's been handled

After each thread is dealt with:

1. `label_thread` → add `Claude/Digested` to every thread you processed (all four buckets).
2. `label_thread` → also add `Claude/Replied` to every thread you drafted a reply for.

Do this per thread as you go, not all at the end, so a failed run doesn't lose track.

Do **not** archive, delete or mark as read. The user's inbox stays as it was, just labelled.

## Step 7 — Digest

Reply to the user with this format. Keep each line to one sentence.

```
## Latest — [day, date, time]

**Today:** [events today, or "Nothing booked"]
**Tomorrow:** [events tomorrow]

### 🔴 Urgent (n)
- **[Sender]** — [what they want]. Draft ready. [⚠️ any flag]

### 🟡 Needs reply (n)
- **[Sender]** — [what they want]. Draft ready.

### 🔵 FYI (n)
- **[Sender]** — [one-line summary]

### ⚪ Noise (n)
[n newsletters/marketing, not listed]

### ⚠️ Needs you
- [Placeholders to fill, calendar clashes, events to create, anything you couldn't answer]
```

Add a `### Still waiting` section from the log's open items (only ones still pending).

End with: "Drafts are in Gmail, ready to review and send."

## Step 8 — Update the working log

Do this last, every run, even if nothing new came in.

1. Set `LAST RUN` to now.
2. Add new 🔴/🟡 items to open items. Remove finished or stale ones (see "Keep it small").
3. Add one line to recent runs; trim to 5.
4. `update_draft` on the existing log (or `create_draft` with no recipient on first run).

## Guardrails

- Never send the working log. Never add a recipient to it.

- Never send, delete, archive or mark as read.
- Never make up prices, dates or promises.
- Never double-book — always check the calendar first.
- If an email looks like phishing or asks for passwords/payment details, put it in ⚠️ Needs you, don't draft a reply.
- If a tool call fails, say which one and carry on with the rest.
