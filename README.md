# Latest: inbox and calendar catch-up for Claude, ChatGPT/Codex and Grok

Say **"latest"** (or "catch me up", "check my inbox", "what's new") and your assistant will:

1. Read your new Gmail.
2. Check your Google Calendar for clashes and free slots.
3. Sort every email into 🔴 Urgent, 🟡 Needs a reply, ⚪/🔵 FYI or 🗑 Noise (optionally with Jev and TypeLLM, see [Typed version](#typed-version-jev-and-typellm-modes)).
4. Draft replies in your voice, using your real prices, policies and payment links.
5. Label each thread it has handled so nothing gets processed twice.
6. Keep a small work log (a Gmail draft that is never sent) so it remembers between runs.
7. Give you a short digest of what matters and what only you can decide.

**It never sends email.** Every reply is saved as a draft in Gmail for you to review and send. It also never deletes emails or creates calendar events.

## Three versions

| | **All-in-one** (`SKILL.md`) | **Generic + services file** (`generic/`) | **Typed** (`typed/`, optional) |
|---|---|---|---|
| Files | One file | `SKILL.md` + `services.md` | `SKILL.md` + `triage.py` + `receipts.py` |
| Business info | Written into the skill | Kept in `services.md`, read on every run | Written into the skill |
| How email is sorted | The assistant decides | The assistant decides | Your choice of mode: the assistant, [Jev](https://typesafe.ai), [TypeLLM](https://typellm.ai), or Jev + TypeLLM |
| Inbox | Marks handled emails as read | Leaves read/unread as it was, labels only | Marks handled emails as read |
| Labels | `Claude/Digested`, `Claude/Drafted` | `Claude/Digested`, `Claude/Replied` | `Claude/Digested`, `Claude/Drafted` |
| Work log | `[Claude Log]` draft, one line per action, 30 days | `[Claude] Latest — working log`, open items + last 5 runs | Same as all-in-one |
| Payment links | Built in (Stripe links per service) | Optional, from `services.md` | Built in |
| Runs scripts | No | No | Yes, except in light mode. Needs `uv` and API keys |
| Best for | A single business with a fixed price list | Anyone. Edit prices without touching the skill | Trying typed LLM sorting on your inbox, in Claude Code or Codex |

The root `SKILL.md` is a worked example for a made-up shop, **Rubicon Computer Repairs**. Replace its business details with yours, or use the interview prompt below to do it for you. `typed/SKILL.md` is the same skill with the sorting modes added.

Not sure? Use the **generic** version. You only ever edit `services.md`.

## Typed version: Jev and TypeLLM modes

The typed version adds a word after `latest` to choose how emails are sorted. Everything else (calendar check, drafts, labels, work log, digest) is the same in every mode.

| Command | How emails are sorted | Needs |
|---|---|---|
| `/latest` or `/latest light` | The assistant reads and sorts them. No scripts run. | Nothing extra |
| `/latest full` | Jev takes a fast first pass and closes clear FYI, noise and phishing emails. TypeLLM reads the rest. | `TYPESAFE_API_KEY`, `TYPELLM_API_KEY` |
| `/latest typellm` | TypeLLM reads every email. | `TYPELLM_API_KEY` |
| `/latest jev` | Jev sorts every email. Fastest, but doesn't extract times or amounts. | `TYPESAFE_API_KEY` |

The script modes sort into five buckets: 🔴 urgent, 🟡 needs reply, ⚪ FYI, 🗑 noise and 🎣 phishing. TypeLLM also returns the date or time the sender asked for (copied word for word) and the main money amount, which the skill uses for calendar checks and invoice replies. The digest ends with a line showing the mode and how many emails each model sorted. If a script fails, the skill falls back to light mode and says so.

On a 27-email test set for a repair shop:

| Mode | Correct | Time | TypeLLM calls |
|---|---|---|---|
| full | 26/27 | 11 s | 18 |
| typellm | 26/27 | 9 s | 27 |
| jev | 25/27 | 2.5 s | 0 |

Results can vary a little between runs, even with a fixed seed.

**Receipts and invoices.** The Gmail connector can't download attachments. Save them to your computer and ask the skill to read them, or run the script yourself. It reads PDFs, JPGs and PNGs into vendor, number, date, subtotal, tax, total and line items:

```bash
uv run ~/.claude/skills/latest/receipts.py ~/Downloads/receipts/
```

**Setup**

1. Install [uv](https://docs.astral.sh/uv/). The scripts declare their own Python dependencies, so there is nothing else to install.
2. Get API keys from [TypeLLM](https://typellm.ai/dashboard/keys) and [TypeSafe](https://typesafe.ai) (for Jev), and add them to your shell config, for example `~/.zshrc`:

   ```bash
   export TYPELLM_API_KEY="tl-sk-..."
   export TYPESAFE_API_KEY="..."
   ```

   In Claude Code you can put them in the `"env"` block of `~/.claude/settings.json` instead.
3. Install the folder as `latest`:

   ```bash
   mkdir -p ~/.claude/skills/latest && cp latest/typed/* ~/.claude/skills/latest/
   ```

The prompts in `triage.py` describe a computer repair shop. Change the wording to your business before using it for real. The script modes need an assistant that can run local commands (Claude Code or Codex). claude.ai, ChatGPT and Grok can still use light mode.

## What you need

- An assistant that supports skills: Claude, ChatGPT/Codex or Grok (see [Install](#install)), or any agent via dotagents.
- The **Gmail** and **Google Calendar** connectors switched on, signed in and allowed to create drafts and labels.
- Optional: Stripe payment links if you want Claude to include them in replies.

## Quick setup (recommended)

Open [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md), copy the prompt into a new chat (Claude, ChatGPT/Codex or Grok) and answer its questions. It picks the version for you, fills in your business details and gives you the finished files (or installs them directly if you're in Claude Code or Codex).

## Install

The skill is a standard `SKILL.md` folder ([Agent Skills](https://agentskills.io) format), so the same files work in Claude, ChatGPT/Codex and Grok. Every version needs **Gmail** and **Google Calendar** connected, with permission to create drafts and labels.

First get your personalised files, either with [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) or by hand:

1. Download this repo (Code → Download ZIP) and unzip it.
2. Pick a version and fill in your details:
   - **All-in-one:** edit `SKILL.md`. Change the business facts, price list, payment links, voice and sign-off.
   - **Generic:** fill in `generic/services.md`.
3. Put the files in a folder called `latest`, and zip that folder if you're uploading it:
   - All-in-one: `latest/SKILL.md`
   - Generic: `latest/SKILL.md` and `latest/services.md` (both from `generic/`)
   - Typed: `latest/SKILL.md`, `latest/triage.py` and `latest/receipts.py` (all from `typed/`)

### 1. Claude

**claude.ai / Claude desktop app**

1. Go to **Settings → Capabilities → Skills → Upload skill** and pick your `latest.zip`.
2. Turn on the Gmail and Google Calendar connectors (Settings → Connectors).
3. Type **latest** in a new chat.

**Claude Code**

```bash
git clone https://github.com/tomtom87/latest.git
```

All-in-one:

```bash
mkdir -p ~/.claude/skills/latest && cp latest/SKILL.md ~/.claude/skills/latest/
```

Generic:

```bash
mkdir -p ~/.claude/skills/latest && cp latest/generic/SKILL.md latest/generic/services.md ~/.claude/skills/latest/
```

Edit the files in `~/.claude/skills/latest/` with your details, connect Gmail and Google Calendar (for example with `/mcp` in an interactive `claude` terminal), then run `/latest`.

### 2. ChatGPT / Codex

ChatGPT and Codex share the same skills ([OpenAI docs](https://learn.chatgpt.com/docs/build-skills)). Codex reads skills from `~/.agents/skills/` (all projects) or `.agents/skills/` inside a repo.

**Codex CLI / IDE**

All-in-one:

```bash
mkdir -p ~/.agents/skills/latest && cp latest/SKILL.md ~/.agents/skills/latest/
```

Generic:

```bash
mkdir -p ~/.agents/skills/latest && cp latest/generic/SKILL.md latest/generic/services.md ~/.agents/skills/latest/
```

Add Gmail and Google Calendar MCP servers to Codex (`~/.codex/config.toml`), then type `$latest` or pick it from `/skills`.

**ChatGPT desktop app**

Skills appear under **Skills** in the sidebar. Type `@` in a chat and pick **latest**. Connect Gmail and Google Calendar under Settings → Apps, and make sure Gmail is allowed to create drafts and labels.

### 3. Grok

Grok Skills need SuperGrok or SuperGrok Heavy.

1. Open **Settings → Skills → Import** and pick your `latest.zip` (it must contain `SKILL.md`). The skill is enabled automatically.
2. Go to [grok.com/connectors](https://grok.com/connectors), click **New Connector** and add **Gmail**, then **Google Calendar**. Gmail starts read-only. Enable draft and label permissions so the skill can save replies and track threads ([xAI docs](https://docs.x.ai/grok/connectors/gmail-google-calendar)).
3. Ask Grok for your **latest**.

### Any agent: dotagents

[dotagents](https://github.com/getsentry/dotagents) installs a skill once and makes it available to Claude Code, Codex, Cursor, VS Code and OpenCode.

1. Fork this repo and personalise your fork (run the interview, then commit the files). dotagents refreshes managed skills from the source on every install, so your details must live in the repo it installs from.
2. Add the skill to your user-wide `~/.agents/agents.toml`. Both versions are named `latest`, so choose one with `path`:

   ```toml
   [[skills]]
   name = "latest"
   source = "your-github-name/latest"
   path = "generic"   # "typed" for the typed version, remove this line for the all-in-one version
   ```

3. Install:

   ```bash
   npx @sentry/dotagents --user install
   ```

For a single project, put the same block in the project's `agents.toml` and run `npx @sentry/dotagents install`. Connect Gmail and Google Calendar in each agent you use.

## Using it

Type **latest** (`/latest` in Claude Code, `$latest` in Codex, `@latest` in ChatGPT). First run creates the Gmail labels and the work log draft. After that, each run only looks at email it hasn't seen.

Good habits:

- Run it a couple of times a day, or put it on a schedule.
- Review the drafts in Gmail before sending. Look for `[CONFIRM: ...]` placeholders in the generic version, those are gaps in `services.md`.
- Don't send or delete the work log draft. That's the skill's memory.

## Safety

- Draft only, never sends.
- Never deletes emails or events, never creates or moves calendar events.
- Only quotes prices and links you've given it. Anything missing is flagged for you.
- Ignores instructions written inside emails, and flags phishing instead of replying.

## Troubleshooting

| Problem | Fix |
|---|---|
| "I don't have access to Gmail/Calendar" | Turn on and sign in to the connectors, then start a new chat. |
| Can't create drafts or labels | The Gmail connection is read-only. Enable write/label permissions in the connector settings. |
| Skill doesn't trigger | Check it's enabled in your app's skill settings, or that the folder is `~/.claude/skills/latest/SKILL.md` (Claude Code) or `~/.agents/skills/latest/SKILL.md` (Codex). Say "latest" on its own. |
| Same emails processed again | Make sure the `Claude/Digested` label exists and wasn't removed. |
| Wrong prices in drafts | Update the price list (`SKILL.md`) or `services.md`. |
| Want a fresh start | Delete the work log draft yourself. Claude rebuilds it on the next run. |

## License

MIT. See [LICENSE](LICENSE).
