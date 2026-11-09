# Markets that contradict each other (2026-11-09, `logichunt.py`)

Question: do linked markets ever price a sure thing below $1, after walking the real asks for 5 shares and paying fees?
Live scan on 2026-11-09 covered 25,268 open Polymarket yes/no markets and 18,615 open Kalshi events. Then the ~40 nearest misses were re-priced every 3 minutes for 2 hours (`lh_watch_120`).

| Kind | Checked | Real cost below $1 |
|---|---|---|
| Polymarket ladders inside one event (the `ladder` track's list) | 4,914 pairs | 0 |
| Polymarket ladders across two events (same question text) | 195 pairs | 0 (best within 0.3c on listed prices) |
| Champion, conference champion, makes playoffs (NFL, NBA, NHL) | 11 list pairs, 16 near misses | 0 teams priced backwards; the best costs $1.001 for $1 |
| Plain yes/no groups (not negRisk), all-NO or all-YES | 77 groups | The "cheap" ones are hidden ladders (win totals, yardage, "valuation hit"). Several can win at once, so they aren't safe. The best truly exclusive one gains ~1c on a $2.99 stake over 55 days (OpenAI Humanity's Last Exam buckets) |
| Kalshi exclusive sets, all-NO | 114 priced | 0 (best -0.4c) |
| Kalshi complete bucket sets, all-YES | 2 | 1 at +1.5c, but it runs 806 days (Trump executive orders) |
| Kalshi strike ladders (same subject, same close) | 101 priced | 0 (best -0.1c) |

Nothing new opened during the 2-hour watch. The gaps that stayed "open" were the unsafe hidden ladders above. Every safe pair stayed 0.1-1c over $1.

These traps are fixed in the code and are worth knowing:
- Kalshi labels "exactly N" buckets as strike_type `less`/`greater` with floor == cap. Treat a ladder strike as one-sided only.
- Kalshi events can mix many players or teams (spreads, receiving yards). Group ladders by subject, not by event.
- Polymarket groups that sum near $1 are often thresholds ("over 6.5 wins", "over 7.5 wins"), not exclusive outcomes.

Verdict: dead end. Everywhere a slow bot can see, the gaps between linked markets are already closed to within about a penny. No paper track was added.
