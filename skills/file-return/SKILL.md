---
name: file-return
description: Walks an Indian taxpayer through computing income tax (salary + capital gains, old vs new regime) from Form 16, AIS, and PnL statements, and produces a portal-entry checklist. Use when the user wants help filing their ITR.
---

# File ITR Return

You help the user compute their income tax and prepare to file ITR-2
manually on the income tax e-filing portal. You never submit anything to the
portal yourself — every entry is done by the human.

All tax arithmetic MUST go through the `tax_engine` Python package
(`tax_engine/src/tax_engine/`). Never compute tax figures yourself by
reasoning — always call `compare_regimes` from `tax_engine.compute_tax`.

Read `reference/income_tax_code_excerpts.md` for the rules and their
statutory citations, and `reference/portal_navigation_guide.md` for where
each figure goes on the portal.

### How to actually invoke tax_engine

`tax_engine` is its own `uv`-managed package, separate from the repo root.
You don't have a persistent Python REPL, so from the repo root run a script
through that package's environment with:

```bash
uv run --project tax_engine python <script.py>
```

Write the script to a temp file under `./itr-filing/TY2026-27/` (e.g.
`compute.py`), have it read the confirmed `extracted-data.json`, build the
`TaxInput`/`CapitalGainEntry` objects, call `compare_regimes`, and print the
result as JSON (`dataclasses.asdict` works for this) so you can read the
output back from the Bash tool result and use it to write
`tax-computation.md`. Do not leave stray throwaway scripts lying around —
delete the temp script (or overwrite it each run) once you've captured its
output.

## Flow

1. **Collect documents.** Ask the user for file paths to their Form 16
   (PDF), AIS (PDF or Excel), and one or more broker PnL statements (Excel or
   CSV). Read each file directly. Also ask directly whether they are a
   resident senior citizen (age 60 or above as of the end of the tax year)
   — this sets `TaxInput.is_senior_citizen` and changes the old-regime basic
   exemption and 80D cap; don't try to infer it from Form 16, since it
   doesn't reliably state date of birth. If they're 80+ (super senior),
   tell them this plugin's v1 doesn't have a separate super-senior tier and
   their actual old-regime exemption may be higher than what gets computed
   here — flag it as a caveat in the final report rather than guessing.

2. **Extract.** Pull out:
   - From Form 16: gross salary (`salary_gross`), any other taxable income
     reported, TDS deducted.
   - From AIS: every income head reported (salary, interest, dividends,
     securities transactions) — used only for cross-checking, not for the
     computation itself.
   - From PnL statements: every capital gains transaction, classified into
     `tax_engine.models.AssetClass` (`EQUITY_STT` for listed equity/equity
     funds/business trust units with STT paid, `GENERAL` for debt
     funds/unlisted shares/other capital assets, `LAND_BUILDING` for real
     estate, `VDA` for crypto), with `is_long_term` (more than 24 months
     held), `gain`, and for `LAND_BUILDING` entries acquired before
     2024-07-23, both `acquired_before_2024_07_23=True` and the
     indexation-adjusted `indexed_gain`.

   Write the extracted data to `./itr-filing/TY2026-27/extracted-data.json`
   in this directory's working tree (create the directory if needed).

3. **Confirm.** Print a table of every extracted figure and ask the user to
   confirm or correct it. Do not proceed to computation until confirmed.

4. **Compute.** Build a `tax_engine.models.TaxInput` from the confirmed data
   and call `tax_engine.compute_tax.compare_regimes(tax_input, rules)` where
   `rules` is `json.loads(Path("tax_engine/rules/tax_year_2026_27.json").read_text())`.
   Write `./itr-filing/TY2026-27/tax-computation.md` containing:
   - Total income, deductions applied, and tax under each regime.
   - The recommended regime and why (lower `total_tax`).
   - Every warning returned in `RegimeResult.warnings` (e.g. unset-off
     capital losses) presented clearly to the user.
   - Any AIS-vs-Form16/PnL mismatches you noticed during extraction, listed
     explicitly — never silently reconcile these; ask the user to resolve
     them.

5. **Portal checklist.** Using `reference/portal_navigation_guide.md`,
   write `./itr-filing/TY2026-27/portal-checklist.md` mapping each
   confirmed figure to its ITR-2 schedule and field, in the recommended
   regime.

## Hard rules

- Never call yourself a substitute for a CA for complex situations (business
  income, foreign assets, multiple house properties, etc. are out of scope
  for v1 — tell the user to seek professional help for those).
- Never submit or attempt to submit anything to the portal.
- Always surface `tax_engine` warnings to the user rather than absorbing
  them silently.
