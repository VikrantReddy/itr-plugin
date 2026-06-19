# ITR Filing Assistant for Indian Income Tax (Claude Code Plugin)

> **Disclaimer:** This is not a financial product and not professional tax
> advice. It is a reference tool only — the computations may be wrong.
> Always consult a Chartered Accountant before filing or relying on any
> figure produced here.

A Claude Code plugin that helps Indian taxpayers compute their income tax
and prepare an ITR-2 filing — from raw documents to a portal-entry
checklist. It never submits anything to the income tax portal; every entry
is made by the human, this just does the math and tells you where it goes.

## What it does

- **Reads your source documents directly**: Form 16 (PDF), AIS (PDF/Excel),
  and broker capital-gains P&L statements (Excel/CSV) — no manual
  data entry of the basics.
- **Computes tax under both the old and new regimes** and recommends
  whichever is cheaper, via a deterministic Python tax engine (not LLM
  arithmetic) for every figure.
- **Capital gains, classified correctly by asset type**: listed equity/equity
  funds (STT-paid), debt funds & other general assets, land/building, and
  virtual digital assets (crypto) — each with the right holding-period
  threshold for long-term vs short-term (these differ by asset class under
  the Income-tax Act, e.g. 12 months for listed equity vs 24 months for
  most other assets).
- **Land/building indexation**: picks the cheaper of indexed vs non-indexed
  capital-gains tax for pre-23-July-2024 acquisitions, per the grandfathering
  rule.
- **House property income/loss**: up to two self-occupied properties plus
  any number of let-out properties, with the correct home-loan interest cap
  (₹2,00,000 vs ₹30,000) based on when the loan was taken and possession
  completed.
- **NPS deductions**: both the self-contribution (old regime only, capped at
  ₹50,000) and employer contribution (both regimes, with different caps for
  government vs private employers).
- **Section 87A rebate**, applied correctly per regime — a hard cliff above
  the threshold under the old regime vs marginal relief under the new regime.
- **Surcharge computation**, including marginal-relief checks near the
  ₹50L/₹1Cr/₹2Cr/₹5Cr thresholds.
- **4% health & education cess** applied on the final tax (after rebate and
  surcharge) under both regimes.
- **Cross-checks AIS against Form 16/PnL** and surfaces mismatches instead of
  silently reconciling them.
- **Flags out-of-scope cases explicitly** rather than guessing — e.g. a 3rd+
  self-occupied property, super-senior citizens (80+), or Agniveer Corpus
  Fund contributions are called out as not modelled in v1.
- **Produces two output documents** per filing: a `tax-computation.md`
  (regime comparison, recommended regime, tax due/refund, surcharge,
  warnings) and a `portal-checklist.md` mapping every confirmed figure to
  its exact ITR-2 schedule and field on the e-filing portal.

## Installation

This repo is itself a Claude Code plugin marketplace. In Claude Code, run:

```
/plugin marketplace add gravity-codes/itr-plugin
/plugin install itr-filing@itr-plugin
```

Then start a conversation and ask to file your ITR — Claude will use the
`file-return` skill automatically.

### Claude Desktop / claude.ai

This skill is self-contained under `skills/file-return/` — `tax_engine` and
the reference docs it needs live inside that folder, with no dependency on
anything elsewhere in this repo.

1. Clone or download this repo.
2. Zip the `skills/file-return/` folder (the zip's root should be the
   `file-return` folder itself, containing `SKILL.md`, `tax_engine/`, and
   `reference/`).
3. Upload it as a custom skill via Claude Desktop/claude.ai's skill
   settings.

> **Note:** the exact custom-skill upload UI and any plan-tier
> restrictions (e.g. Pro/Max/Team/Enterprise) weren't independently
> verified while building this — if step 3 doesn't match what you see in
> your client, check Anthropic's current Agent Skills documentation.

## How it works

- `skills/file-return/SKILL.md` — the Claude Code skill that drives the
  end-to-end flow: collect documents → extract figures → confirm with the
  user → compute → write the portal checklist.
- `skills/file-return/tax_engine/` — a standalone, dependency-free Python
  package that does all tax arithmetic deterministically: slabs, surcharge,
  capital gains, house property, and regime comparison. The skill calls
  into it (via plain `python3`, no package manager needed) rather than
  reasoning about tax math itself.
- `skills/file-return/reference/income_tax_code_excerpts.md` — the
  statutory rules and citations (Income-tax Act, 2025) backing every
  computation.
- `skills/file-return/reference/portal_navigation_guide.md` — maps each
  computed figure to its field on the incometax.gov.in ITR-2 form.

Everything the skill needs lives inside `skills/file-return/`, so that
folder alone is a complete, portable unit — usable as a Claude Code plugin
skill or zipped up for Claude Desktop/claude.ai.

## Status

Covers salary income, capital gains (all major asset classes), house
property, NPS, and the old-vs-new regime comparison for AY 2026-27 (Tax Year
2026-27). Business income, foreign assets, and a few other edge cases are
explicitly out of scope for v1 — the skill tells you to consult a CA for
those rather than guessing.
