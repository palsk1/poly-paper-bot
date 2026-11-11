# Can a simple fix save the `claude` track?

Generated 2026-11-11T19:06:49Z by `claudefix.py`. Paper only. 126,352 finished Polymarket markets that ended before 2026-11-10 (bt_cache). Each version replayed with the real picking code, 2 picks a day, no cash limit. Decision number = the pessimistic one (PROTOCOL.md): bought 1 hour late at the chart price +2c plus fee, a take-profit sold at the target. Money is per $100 bet.

| Version | Bets (won/lost) | Per $100, +1c | Per $100, +2c 1h late | 1st / 2nd half | Random bets, same band and exits | Exam verdict | Worst case per $100 |
|---|---|---|---|---|---|---|---|
| Live rules, no volume filter | 364 (267/97) | -$5.49 | -$7.35 | -$6.68 / -$8.01 | -$6.93 | Losing | -$10.45 |
| Hold to the end, no volume filter | 361 (308/53) | -$6.73 | -$6.79 | -$3.46 / -$10.10 | -$2.89 | Losing | -$11.77 |
| Hold to the end, 30-60 days, no volume filter | 360 (301/59) | -$6.60 | -$8.57 | -$6.31 / -$10.83 | -$2.33 | Losing | -$15.40 |
| Live rules, random pick | 364 (250/114) | -$4.38 | -$6.60 | -$6.73 / -$6.47 | -$6.51 | Losing | -$7.76 |
| Hold to the end, random pick | 359 (307/52) | -$5.34 | -$6.44 | -$7.76 / -$5.15 | -$4.82 | Losing | -$18.36 |
| Hold to the end, 30-60 days, random pick | 358 (312/46) | -$3.51 | -$4.86 | -$2.58 / -$7.11 | -$2.95 | Losing | -$14.09 |
| Hold to the end, 30-60 days, 90-97c, random pick | 359 (329/30) | -$1.77 | -$3.99 | -$1.16 / -$6.76 | -$1.98 | Losing | -$11.55 |

How to read it: 'Random bets' = for each bet, a random other market open at the same time with the same days left and price band, same exits and costs. If the version doesn't beat that, the picking adds nothing.

## Exam cards

### Live rules, no volume filter

```

=== EXAM: claude track fix: Live rules, no volume filter ===
Verdict: Losing
Bets: 364 bets on 308 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$5.02 per $100 bet (total -$83.36 on $1661.90). Luck range -$7.54 to -$2.50.
Halves: first -$3.26, second -$6.76 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 85 tries. The luckiest of 85 worthless ideas would show about +$4.90 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$10.45. Below $0: not proven.
```

### Hold to the end, no volume filter

```

=== EXAM: claude track fix: Hold to the end, no volume filter ===
Verdict: Losing
Bets: 361 bets on 340 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$3.27 per $100 bet (total -$54.02 on $1654.02). Luck range -$7.49 to +$0.95.
Halves: first +$2.04, second -$8.65 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 86 tries. The luckiest of 86 worthless ideas would show about +$7.95 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$11.77. Below $0: not proven.
```

### Hold to the end, 30-60 days, no volume filter

```

=== EXAM: claude track fix: Hold to the end, 30-60 days, no volume filter ===
Verdict: Losing
Bets: 360 bets on 356 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$6.18 per $100 bet (total -$101.80 on $1646.80). Luck range -$10.81 to -$1.56.
Halves: first +$2.29, second -$14.81 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 87 tries. The luckiest of 87 worthless ideas would show about +$8.68 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$15.40. Below $0: not proven.
```

### Live rules, random pick

```

=== EXAM: claude track fix: Live rules, random pick ===
Verdict: Losing
Bets: 364 bets on 324 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$3.09 per $100 bet (total -$51.54 on $1668.91). Luck range -$5.15 to -$1.02.
Halves: first -$2.28, second -$3.90 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 88 tries. The luckiest of 88 worthless ideas would show about +$4.14 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$7.76. Below $0: not proven.
```

### Hold to the end, random pick

```

=== EXAM: claude track fix: Hold to the end, random pick ===
Verdict: Losing
Bets: 359 bets on 351 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$8.60 per $100 bet (total -$141.08 on $1641.08). Luck range -$13.52 to -$3.67.
Halves: first -$12.17, second -$4.93 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 89 tries. The luckiest of 89 worthless ideas would show about +$9.23 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$18.36. Below $0: not proven.
```

### Hold to the end, 30-60 days, random pick

```

=== EXAM: claude track fix: Hold to the end, 30-60 days, random pick ===
Verdict: Losing
Bets: 358 bets on 353 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$5.06 per $100 bet (total -$82.86 on $1637.86). Luck range -$9.56 to -$0.56.
Halves: first -$1.56, second -$8.68 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 90 tries. The luckiest of 90 worthless ideas would show about +$8.49 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$14.09. Below $0: not proven.
```

### Hold to the end, 30-60 days, 90-97c, random pick

```

=== EXAM: claude track fix: Hold to the end, 30-60 days, 90-97c, random pick ===
Verdict: Losing
Bets: 359 bets on 353 events over 182 days. Counted as 182 separate bets (losses came in bunches on the same days, so one day counts once).
Result: -$4.21 per $100 bet (total -$72.34 on $1717.34). Luck range -$7.77 to -$0.65.
Halves: first -$3.38, second -$5.07 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 91 tries. The luckiest of 91 worthless ideas would show about +$6.80 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$11.55. Below $0: not proven.
```

Run time 66s.
