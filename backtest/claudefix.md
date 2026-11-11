# Can a simple fix save the `claude` track?

Generated 2026-11-11T18:43:06Z by `claudefix.py`. Paper only. 126,352 finished Polymarket markets that ended before 2026-11-10 (bt_cache). Each version replayed with the real picking code, 2 picks a day, no cash limit. Decision number = the pessimistic one (PROTOCOL.md): bought 1 hour late at the chart price +2c plus fee, a take-profit sold at the target. Money is per $100 bet.

| Version | Bets (won/lost) | Per $100, +1c | Per $100, +2c 1h late | 1st / 2nd half | Random bets, same band and exits | Exam verdict | Worst case per $100 |
|---|---|---|---|---|---|---|---|
| Live rules: sell at 97c, sell at 70c | 364 (245/119) | -$6.56 | -$8.30 | -$7.68 / -$8.92 | -$6.35 | Losing | -$11.67 |
| Sell at 97c, never sell at a loss | 363 (295/68) | -$6.62 | -$9.69 | -$9.14 / -$10.22 | -$6.46 | Losing | -$27.50 |
| Sell at 70c, otherwise hold to the end | 353 (229/124) | -$7.56 | -$8.84 | -$6.60 / -$11.06 | -$6.52 | Losing | -$6.12 |
| Hold every bet to the end | 340 (285/55) | -$7.92 | -$8.32 | -$5.78 / -$10.85 | -$3.67 | Losing | -$16.42 |
| Hold to the end, only 30-60 days left | 273 (226/47) | -$8.15 | -$9.39 | -$7.49 / -$11.25 | -$0.71 | Losing | -$14.82 |

How to read it: 'Random bets' = for each bet, a random other market open at the same time with the same days left and price band, same exits and costs. If the version doesn't beat that, the picking adds nothing.

## Exam cards

### Live rules: sell at 97c, sell at 70c

```

=== EXAM: claude track fix: Live rules: sell at 97c, sell at 70c ===
Verdict: Losing
Bets: 364 bets on 293 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$6.24 per $100 bet (total -$103.84 on $1664.63). Luck range -$8.80 to -$3.68.
Halves: first -$2.60, second -$9.87 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 74 tries. The luckiest of 74 worthless ideas would show about +$4.90 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$11.67. Below $0: not proven.
```

### Sell at 97c, never sell at a loss

```

=== EXAM: claude track fix: Sell at 97c, never sell at a loss ===
Verdict: Losing
Bets: 363 bets on 305 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$17.50 per $100 bet (total -$289.84 on $1656.19). Luck range -$22.70 to -$12.30.
Halves: first -$13.85, second -$21.16 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 74 tries. The luckiest of 74 worthless ideas would show about +$9.53 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$27.50. Below $0: not proven.
```

### Sell at 70c, otherwise hold to the end

```

=== EXAM: claude track fix: Sell at 70c, otherwise hold to the end ===
Verdict: Losing
Bets: 353 bets on 308 events over 180 days. Counted as 180 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$0.50 per $100 bet (total -$8.05 on $1614.80). Luck range -$3.11 to +$2.11.
Halves: first +$2.85, second -$3.97 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 75 tries. The luckiest of 75 worthless ideas would show about +$5.05 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$6.12. Below $0: not proven.
```

### Hold every bet to the end

```

=== EXAM: claude track fix: Hold every bet to the end ===
Verdict: Losing
Bets: 340 bets on 320 events over 176 days. Counted as 176 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$6.85 per $100 bet (total -$106.29 on $1551.29). Luck range -$11.72 to -$1.99.
Halves: first -$5.21, second -$8.60 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 76 tries. The luckiest of 76 worthless ideas would show about +$9.00 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$16.42. Below $0: not proven.
```

### Hold to the end, only 30-60 days left

```

=== EXAM: claude track fix: Hold to the end, only 30-60 days left ===
Verdict: Losing
Bets: 273 bets on 264 events over 154 days. Counted as 154 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$4.93 per $100 bet (total -$61.43 on $1246.43). Luck range -$9.83 to -$0.02.
Halves: first -$5.08, second -$4.75 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 77 tries. The luckiest of 77 worthless ideas would show about +$9.17 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$14.82. Below $0: not proven.
```

Run time 47s.
