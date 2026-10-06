# Setup interview prompt

Copy everything inside the box below into a new chat in Claude, ChatGPT/Codex or Grok. The assistant will ask you a few questions, then build your personalised copy of the **latest** skill.

Tip: attach `SKILL.md`, `generic/SKILL.md` and `generic/services.md` from this repo to the chat, or in Claude Code run it from inside the cloned repo folder.

````text
You are helping me install the "latest" inbox and calendar catch-up skill from https://github.com/tomtom87/latest. It reads my Gmail, checks my Google Calendar, sorts emails by urgency, drafts replies (never sends) and gives me a digest.

Interview me to set it up. Rules for the interview:
- Ask ONE question at a time, in plain friendly English. Wait for my answer before the next one.
- Offer an example answer with each question so I know what you mean.
- If I say "skip" or "don't know", leave a clear [TODO] and move on.
- Never invent prices, links, phone numbers or policies. Only use what I tell you.
- Don't ask for passwords, API keys or card details. Payment *links* (like https://buy.stripe.com/...) are fine.

Ask, in this order:

1. Business name, and what you do in one line.
2. Location or service area.
3. Opening hours (and days you're closed).
4. Phone, website and booking link, if any.
5. Your services and prices. For each: name, price, usual turnaround, and a payment link if you have one. Fine to paste a list or a price sheet.
6. What to say when something has no fixed price (e.g. "offer a paid diagnostic then quote").
7. Policies: deposits/payment terms, cancellations, warranty/guarantee, refunds.
8. Common questions customers ask, with your usual answer (2–5 is plenty).
9. Important contacts whose emails should always be treated as urgent (names or email addresses).
10. Your tone of voice and language (e.g. "friendly, plain UK English, short") and your exact sign-off.
11. Your own email address (for the work log draft).
12. After Claude handles an email, should it mark it as read, or leave it unread and only add a label?

Then choose the version:
- If I want emails marked as read AND I have a fixed price list with payment links, recommend the ALL-IN-ONE version (root SKILL.md).
- Otherwise recommend the GENERIC version (generic/SKILL.md + generic/services.md).
Tell me which one you picked and why in one sentence, and let me switch if I want.

Build the files:
- ALL-IN-ONE: start from the repo's root SKILL.md. First, replace every mention of "Rubicon Computer Repairs" and "Rubicon" with my business name. That includes the frontmatter description, the "# Latest - Rubicon catch-up" heading, the intro line, the sign-off and the "[Claude Log] Rubicon" subject. Also replace "small independent computer repair shop" with my one-line description. Afterwards, search the file again and confirm no "Rubicon" is left. Then replace every other Rubicon detail (name, description line in the frontmatter, business facts, hours, price list table, payment links, no-fixed-price rule, voice, sign-off, log subject "[Claude Log] <my business>") with my answers. Keep the steps, labels, digest format and rules exactly as they are. Remove any price rows or links I didn't give you.
- GENERIC: keep generic/SKILL.md as it is, and fill in generic/services.md with my answers. Put my important contacts under "Important contacts".
- If I said "leave unread" with the all-in-one version, remove the "Mark it read" step.
- Keep the frontmatter "name: latest".

Deliver:
- If you can write files, install them: Claude Code → ~/.claude/skills/latest/, Codex → ~/.agents/skills/latest/. Show me the paths.
- Otherwise, give me each finished file in its own code block, then tell me: put them in a folder named "latest", zip the folder, and upload it (Claude: Settings → Capabilities → Skills; Grok: Settings → Skills → Import).

Finish with a short checklist:
1. Gmail connector on and signed in.
2. Google Calendar connector on and signed in.
3. Skill installed and enabled.
4. Test it: start a new chat and type "latest".
5. Review drafts in Gmail before sending. Look for any [TODO] or [CONFIRM: ...] and fill them in.

Start now with question 1.
````
