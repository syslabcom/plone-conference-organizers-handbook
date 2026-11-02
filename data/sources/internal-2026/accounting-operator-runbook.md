<!-- Internal source copy (INT-08 in internal-sources-2026.md): aftermath/ploneconf-accounting/docs/operator-runbook.md; D7-screened 2026-11-02. -->

# Operator runbook — ploneconf-accounting

Design and rationale: `~/org/roam/agentic/devops/ploneconf-accounting.org`.
This runbook covers the mechanical actions only.

## Regular import cycle

Once or twice a week, refresh figures from ti.to and Stripe.

1. **Pull** latest git so both workstations start from the same state:

   ```
   git pull
   ```

2. **Download** fresh exports and drop them into `source-data/debitors/`.

   - **ti.to:** Dashboard → Reports → Income and expenditure → Export → CSV.
     Save as `source-data/debitors/income_and_expenditure_by_payments-*.csv`
     (keep whatever filename ti.to emits; the rules file globs on the prefix).
   - **Stripe:** Dashboard → Transactions → Payouts → Export → Date range: all.
     Save as `source-data/debitors/payouts.csv` (overwrite; re-downloads may
     land as `payouts (1).csv`, which the glob also matches).

   Both exports are *cumulative full trails* — every export contains every row
   since the campaign started. `hledger import` deduplicates via the
   `.latest.<rulesname>` sidecars in `rules/` (committed to git for sync).

3. **Import**:

   ```
   hledger import -f imported.journal \
       rules/tito-orders.csv.rules \
       rules/stripe-payouts.csv.rules
   ```

   Reports either `imported N new transactions` or `no new transactions found`.
   Idempotent — safe to re-run.

4. **ABN/AMRO**

    - Download transactions:
        Zelf regelen  → Bij- en afschrijvingen downloaden  →
        Excel TXT  → vanaf laatste download  → Ondernemingsrekening
      Save into source-data/bank
    - Cleanup transactions: remove all non-Ploneconf lines
    - Claude: "book the new bank transactions"

5. **Verify** balances still make sense:

   ```
   bash tests/run-tests.sh                   # figures still match design worked example
   hledger -f main.journal balance --budget -p 2026   # convergence view
   ```

6. **Commit** and **push**:

   ```
   git add source-data/debitors imported.journal rules/.latest.*
   git commit -m "Import: ti.to + Stripe through YYYY-MM-DD"
   git push
   ```

## Manual entries

`manual.journal` holds transactions not driven by the two CSVs:

- Invoiced sponsors and regular-channel tickets (invoice issue + payment; see
  design § Invoiced income patterns).
- Domestic supplier costs (see § Received supplier invoice — single rate / mixed rate).
- Costs the parent paid directly (see § Cost funded directly by the parent).
- Grant receipts (see § Grants sit outside the regime axis).
- VAT clearance at Q3 close (see § VAT clearance to the parent).
- Ticket refunds — CSV rules skip any row with a non-zero `Refund` column;
  book those manually per § Ticket refund.
- Contract signings for venue/party obligations (see § Commitment recognition).
  Book net (excl. BTW) as Dr `equity:conference-current` / Cr
  `equity:reserved:contracted`. Prepayments split gross into
  `assets:prepaid:venue` (net) + `assets:prepaid:vat` (VAT portion) and unwind
  the reserve for the net portion cash-committed.

Templates are all in the design doc's § Entry patterns.

## Reports

Four canned reports under `bin/`:

```
bin/pnl-budget     # P&L convergence view incl. committed spend (see overlay note)
bin/pnl            # P&L incl. committed spend (see overlay note)
bin/balance        # whole-journal balance for the period
bin/vat            # BTW rubriek summary for the accountant
```

All accept passthrough hledger args (e.g. `bin/vat -p 2026Q3`, `bin/balance --tree`).

**Committed-spend overlay** (`bin/pnl`, `bin/pnl-budget`): the books keep
contracted/prepaid costs on the balance sheet until fiscal invoices arrive,
which makes a strict P&L look far healthier than reality. These two reports
therefore apply a *report-only* relabeling (hledger `--alias`) that counts
`assets:prepaid:venue`, `assets:prepaid:accommodation`, and the contracted
commitment debit in `equity:conference-current` as `expenses:committed:*` —
so **total expenses and the bottom line include committed spend**. The
journals are untouched; `bin/vat`, `bin/balance`, and raw hledger stay
strict. In `bin/pnl-budget` the committed rows carry no budget goal but are
listed by default (`-E` is baked in); revenue sorts before expenses via the
top-level account declarations in `accounts.journal`. The overlay is valid
only while `equity:conference-current` exactly mirrors the contracted
reserve — a parent-funded cost, the Q3 VAT clearance, or close-time P/L
absorption all break that, and a smoke test trips when it happens (expect
this at the Q3 VAT clearance). When it fires, retire or rework the aliases
in `bin/pnl` and `bin/pnl-budget`.

For ad-hoc reconciliation:

```
hledger -f main.journal register assets:bank:conference   # reconcile vs real bank
hledger -f main.journal register assets:bank:stripe       # reconcile vs Stripe balance
hledger -f main.journal balance assets:receivable         # outstanding invoiced-but-unpaid
hledger -f main.journal balance equity:reserved:contracted  # remaining contracted P&L drag not yet cash-committed or invoiced
```

Phase pivot (once actuals carry `phase:` tags):

```
hledger -f main.journal balance expenses --pivot phase
```

## Audit trail back to source

Every generated entry carries the source-row identifier as its `code`:

```
hledger -f main.journal register code:PC2026-0007       # ti.to invoice number
hledger -f main.journal register code:po_1TnT5XH0Q...   # Stripe payout id
```

## Troubleshooting

- **`hledger import` says "no new transactions"** but you know there are new
  rows: delete the corresponding `rules/.latest.<rulesname>` sidecar and
  re-run. It re-imports everything; stable `code`s prevent duplication if you
  merge carefully, otherwise reset `imported.journal` and re-import fully.
- **Amounts off by ~100×:** the Stripe CSV uses `,` as decimal mark and is
  normalised by `rules/bin/stripe-payouts-preprocess.awk`. If that script
  fails, amounts will land wrong. Test with:
  ```
  hledger -f rules/stripe-payouts.csv.rules print
  ```
- **`assets:bank:stripe` non-zero after all payouts should have cleared:** a
  payout is missing from the Stripe CSV, or a ticket sale row is missing from
  the ti.to CSV. Re-export both and re-import.
