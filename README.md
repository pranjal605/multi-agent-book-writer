# Multi-Agent Book Writer

A small multi-agent system that researches and writes a three-chapter book, with real, checked
citations, from a brief.

**Book:** *Pay Me on UPI: How Digital Payments Changed Small Business in India*
**Audience:** first-time small-business owners in India  |  **Length:** 3 chapters, 600-900 words each

![Architecture](docs/architecture.png)

## How to run

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then put ONE API key in .env (a FREE Gemini key works)
python main.py                                         # takes roughly 10-25 minutes
```

Options: `--provider gemini|groq|openrouter|ollama|anthropic|openai`, `--model <name>`,
`--rounds 3`, `--out output`.

**No paid API needed.** A free Google AI Studio key (https://aistudio.google.com/apikey) is enough:
put `GEMINI_API_KEY=...` in `.env` and run `python main.py`. Groq, OpenRouter (`:free` models) and
Ollama (runs locally) also work. Free tiers have rate limits, so the code waits between calls and
retries on 429 errors (raise `LLM_MIN_INTERVAL` in `.env` if you still see them).
Any LLM works through `bookwriter/llm.py` (adding another provider is a few lines). Web search uses DuckDuckGo through the `ddgs` package, so no search
key is needed.

Output (in `output/`):

| File | What it is |
|---|---|
| `book.md`, `book.html` | the finished book (each chapter ends with Takeaway, then references) |
| `plan.json` | the Planner's outline |
| `evidence.json` | every verified fact, quote and link the Researcher kept |
| `chapterN_draftR.txt` | each draft of each chapter, per revision round |
| `run_log.json` | what every agent did |

Run the tests (no API key needed, they use a fake LLM and fake web): `pytest -q`

## The agents

| Agent | Job | How it avoids mistakes |
|---|---|---|
| **Planner** | Turns the brief into 3 chapters, each with key questions and search queries | Asks for questions that official figures can answer |
| **Researcher** | Searches, reads pages, extracts facts | Official sources (NPCI, RBI, PIB, `.gov.in`) rank first, then reputable news; Wikipedia, blogs, Quora, etc. are blocked. Each fact must come with an **exact quote**; code checks the quote really is on the page and the page loads, otherwise the fact is thrown away |
| **Writer** | Writes/revises one chapter | May use **only** the evidence cards and cites them by id (`[E4]`); sees the previous chapter's ending so the voice stays the same |
| **Editor** | Grammar, spelling, tone, jargon explained, readability, voice consistency | Does not touch facts; returns issues, marked major or minor |
| **Fact-checker** | Confirms each citation is real and supports its claim | Re-checks every cited link live, then judges every cited sentence against the real page text around the quote |

A rule-based **lint** step (no LLM) also enforces the hard rules: 600-900 words, no bullets, a
single last-line `Takeaway:` with no numbers, no unknown citation ids, and no number/date/figure
sentence without a citation.

## How they work together

1. Planner -> Researcher fills a shared **evidence store** before any writing starts.
2. For each chapter: Writer drafts -> Lint + Editor + Fact-checker review the same draft in
   parallel -> if any **major** issue exists, all issues go back to the Writer for a revision.
3. **Stop rule:** a chapter is approved when no major issue is left, or after 3 rounds
   (`--rounds`). If it stops on the round limit, any sentence still unsupported or uncited is
   **deleted**, so unverified content is never published.
4. The **Assembler** renumbers `[E4]` to `[1]`, `[2]`... per chapter and builds each reference
   list (source name, title, link) only from the sources actually cited. Because the reference
   list is generated from the evidence store, a reference can never point to something other
   than the page the fact came from.

Chapters are written one after another so that each can copy the voice of the one before.

## Design choices and limits

- **Anti-hallucination by construction:** the Writer cannot cite a source that was not fetched
  and quote-verified; the fact-checker is a separate agent with a separate prompt, not the Writer
  marking its own homework.
- **Simple on purpose:** plain Python, no agent framework, under 900 lines.
- **Limits:** some sites block scrapers (those pages are simply skipped); statistics change, so
  the book states figures "as of" the date in the source; the LLM fact-check is strong but not
  perfect, so a human should still skim the references before publishing.
