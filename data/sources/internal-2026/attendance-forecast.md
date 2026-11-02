<!-- Internal source copy (INT-11 in internal-sources-2026.md): planning/sales-data/forecast.py; D7-screened 2026-11-02. -->

```python
#!/usr/bin/env python3
"""Attendance forecast for Plone Conference 2026 — rerun each time the data moves.

Model: `planning/sales-actions.md` (P50 formula, P10/P90 scenario parameters,
venue-guarantee rule). First snapshot and worked example:
`planning/sales-data/20260830-forecast.md`.

Usage:

    python3 planning/sales-data/forecast.py \
        --tickets  planning/sales-data/20260830-tito-tickets.csv \
        --speakers planning/sales-data/20260830-speakers.md \
        --previous planning/sales-data/20260821-tito-tickets.csv

`--previous` is the last Tito export; it gives the measured sales velocity.
Without it, pass `--velocity TICKETS_PER_DAY` by hand.

What the script derives from the files: total tickets, daytime tickets
(party-only excluded), velocity, unique speakers, speakers without a ticket,
zero-claim sponsor columns, unnamed seats on multi-ticket rows.

What you must review BY HAND each run — the judgment inputs in CONFIG below.
The script prints the raw material for them above the forecast, so reviewing
means: read the printed lists, adjust the numbers, rerun. Then save a dated
snapshot markdown next to this script (see the 20260830 example).
"""

import argparse
import csv
import math
import re
import unicodedata
from datetime import date

# ---------------------------------------------------------------------------
# CONFIG — judgment inputs. Review against the printed raw material each run.
# Values below are the 30 August 2026 run; do not bump them mechanically.
# ---------------------------------------------------------------------------

FREEZE = date(2026, 9, 7)        # numbers freeze = T-14 (conference 2026-09-21)

C_CONFIRMED_NON_TICKET = 9       # organisers/keynotes/staff attending with no
                                 # ticket at all (Guido, Alex, Angela, Ciro,
                                 # Alessandro, Kirschner, ...). Was 8 on 21 Aug;
                                 # +1 for the Kirschner keynote.

SPEAKERS_NO_SEAT = 24            # speakers with NO ticket and NO paid seat who
                                 # are expected to buy/register. Derive from the
                                 # printed "speakers without a ticket" list:
                                 # subtract organiser/keynote exceptions,
                                 # speakers covered by unnamed paid seats
                                 # (sponsor speaker tickets, multi-ticket rows),
                                 # and speakers expected on sponsor allocations.
                                 # 30 Aug: 43 ticketless - 7 exceptions - 6 paid
                                 # seats - 5 iMio - 1 match miss = 24.

SPONSOR_PIPELINE = {             # unclaimed sponsor allocations -> (seats, P50
                                 # probability they get named). From the printed
                                 # zero-claim columns + the entitlement model in
                                 # FINANCE/sponsoring/ploneconf-2026.md
                                 # (Gold 4, Silver 2, Bronze 1).
    "iMio (Gold 4 + bulk 8)": (12, 0.85),   # committed sponsor, roster chased
    "Affinitic (Bronze 1 + 3 purchased)": (4, 0.60),
    "Enfold (Silver 2)": (2, 0.30),         # sponsorship not closed yet
}

# Scenario parameters from sales-actions.md — do not tune per run.
SCENARIOS = {
    # label: (q14, velocity multiplier, no-show, speaker weight, sponsor mult)
    "P10": (0.78, 0.75, 0.05, 0.50, 0.5),
    "P50": (0.71, 1.00, 0.03, 0.75, 1.0),
    "P90": (0.65, 1.30, 0.01, 0.90, 1.2),
}

PARTY_ONLY_COLUMN = "Party Quantity"   # excluded from daytime attendance

# ---------------------------------------------------------------------------


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())


def file_date(path: str) -> date:
    m = re.search(r"(\d{4})(\d{2})(\d{2})", path)
    if not m:
        raise SystemExit(f"cannot read date from filename: {path}")
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def load_tickets(path: str):
    """Read a Tito export. Two formats occur:
    - per-registration (one row per order, '* Quantity' columns, 'Name')
    - per-ticket (one row per ticket, 'Ticket Full Name', 'Ticket' type,
      'Void Status') — richer: per-day attendance columns, use it when
      available, especially for the day-level freeze run.
    Returns (rows, total, daytime, unnamed, names, zero_claim_sponsor_cols).
    """
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    if "Ticket Full Name" in rows[0]:  # per-ticket format
        live = [r for r in rows if not r["Void Status"].strip()]
        total = len(live)
        daytime = sum(1 for r in live if r["Ticket"].strip() != "Party")
        unnamed = sum(1 for r in live if not r["Ticket Full Name"].strip())
        names = {norm(r["Ticket Full Name"]) for r in live
                 if r["Ticket Full Name"].strip()}
        return rows, total, daytime, unnamed, names, []
    qty_cols = [c for c in rows[0] if c.endswith("Quantity")]
    per_col = {c: sum(int(r[c]) for r in rows if r[c].strip()) for c in qty_cols}
    total = sum(per_col.values())
    daytime = total - per_col.get(PARTY_ONLY_COLUMN, 0)
    unnamed = 0
    names = set()
    for r in rows:
        n = sum(int(r[c]) for c in qty_cols if r[c].strip())
        if n > 1:
            unnamed += n - 1
        names.add(norm(r["Name"]))
    zero_claim = sorted(c for c in qty_cols if per_col[c] == 0
                        and any(k in c for k in ("ponsor", "Silver", "Gold",
                                                 "Bronze", "bulk", "purchased")))
    return rows, total, daytime, unnamed, names, zero_claim


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tickets", required=True)
    ap.add_argument("--speakers", required=True)
    ap.add_argument("--previous")
    ap.add_argument("--velocity", type=float)
    ap.add_argument("--as-of", default=date.today().isoformat(),
                    help="run date, YYYY-MM-DD (default: today)")
    a = ap.parse_args()
    as_of = date.fromisoformat(a.as_of)

    rows, total, daytime, unnamed, tito_names, zero_claim = load_tickets(a.tickets)
    days_to_freeze = (FREEZE - as_of).days

    if a.previous:
        _, prev_total, prev_daytime, *_ = load_tickets(a.previous)
        span = (file_date(a.tickets) - file_date(a.previous)).days
        velocity = (daytime - prev_daytime) / span
        v_note = f"measured {prev_daytime} -> {daytime} over {span} days"
    elif a.velocity is not None:
        velocity = a.velocity
        v_note = "given by hand"
    else:
        raise SystemExit("need --previous or --velocity")

    speakers = sorted({norm(l) for l in open(a.speakers, encoding="utf-8")
                       if l.strip()})
    matched = {s for s in speakers if s in tito_names
               or any(s.split()[-1] == n.split()[-1]
                      and (s.split()[0] in n or n.split()[0] in s)
                      for n in tito_names)}
    ticketless = [s for s in speakers if s not in matched]

    print("RAW MATERIAL (review CONFIG against this)")
    print(f"  tickets: {total} total, {daytime} daytime "
          f"(party-only excluded), {len(rows)} registrations")
    print(f"  unnamed seats on multi-ticket rows: {unnamed}")
    print(f"  velocity: {velocity:.2f}/day ({v_note})")
    print(f"  days to freeze ({FREEZE}): {days_to_freeze}")
    print(f"  speakers: {len(speakers)} unique, {len(matched)} hold a ticket, "
          f"{len(ticketless)} without")
    print("  ticketless speakers — categorise into exceptions / paid seats / "
          "sponsor seats / expected-to-buy:")
    for s in ticketless:
        print(f"    - {s}")
    print(f"  zero-claim sponsor columns — candidates for SPONSOR_PIPELINE:")
    for c in zero_claim:
        print(f"    - {c}")
    print()

    def run(q14, vmult, noshow, sp_w, spn_mult):
        T = daytime + days_to_freeze * velocity * vmult
        pace = 0.6 * (T / q14) + 0.4 * (T + 14 * velocity * vmult)
        named = (T + SPEAKERS_NO_SEAT * sp_w
                 + sum(n * w * spn_mult for n, w in SPONSOR_PIPELINE.values()))
        m = max(pace, named)
        return T, pace, named, C_CONFIRMED_NON_TICKET + (1 - noshow) * m

    print("FORECAST — principal conference days")
    results = {}
    for label, params in SCENARIOS.items():
        T, pace, named, physical = run(*params)
        results[label] = physical
        print(f"  {label}: tickets@freeze={T:.0f}  pace={pace:.0f}  "
              f"named={named:.0f}  -> physical={physical:.0f}")

    T, pace, named, strict = run(*SCENARIOS["P50"][:3], SCENARIOS["P50"][3], 0.0)
    print(f"  P50 strict (sponsors excluded until named): "
          f"pace={pace:.0f} named={named:.0f} -> physical={strict:.0f}")

    p50, p90, p10 = results["P50"], results["P90"], results["P10"]
    g = math.ceil(max(p50, p90 / 1.10))
    lo, hi = math.floor(g * 0.9), math.ceil(g * 1.1)
    print(f"\nGUARANTEE = ceil(max(P50 {p50:.0f}, P90 {p90:.0f}/1.10)) = {g} "
          f"-> band {lo}-{hi}")
    if p10 >= lo:
        print(f"P10 ({p10:.0f}) inside lower band? yes")
    else:
        print(f"P10 ({p10:.0f}) inside lower band? NO — spread wider than "
              f"the +/-10% band; narrow it or talk to Van der Valk")


if __name__ == "__main__":
    main()

```
