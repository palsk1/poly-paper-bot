# fade_sure re-test on whole events (btcheck.py fade, 2026-11-10)

## What it means

- **fade_sure's backtest was the data hole.** On the old cache (only markets whose final volume passed $20k) the
  rule makes +$53 to +$90 per $100, the same picture as `fade.md`. The old cache drops most of the weather buckets
  that lost, and the cheap side of those is exactly what fade_sure buys.
- **On whole events it loses.** 13,063 bets on 3,126 complete weather events: the cheap side won 845 times where
  the price said about 738. So the long shots are a little cheap, but not by enough to pay for a 1-2c worse price
  on a 6c bet. At the decision setting (+2c, bought 1 hour later) it's **-$18.67 per $100**, band -$22.63 to
  -$14.71, both halves negative. Even the kindest case (+1c, same hour) is -$4.45.
- Verdict: dead. Not stopped here (research only); live track rules are Claude's to change, reported to Jan.

Live rule: weather (temperature/rain/snow) markets ending within 24h, first hour one side is 90-98c and the other
2-10c, buy the cheap side, hold. In-sample only (ending before 2026-11-10). History price + slip + fee. Bands are by
event (bets in one event are not independent). Run: probe `btcheckfade`.

| Data | Entry | Slip | Bets | Events | Cheap side won (price said) | Per $100 | 90% band (by event) | 1st / 2nd half |
|---|---|---|---|---|---|---|---|---|
| old cache ($20k final volume) | same hour | +1c | 4391 | 2242 | 596 (257) | +$90.22 | +$78.50 to +$101.94 | +$90.81 / +$89.59 |
| old cache ($20k final volume) | same hour | +2c | 4391 | 2242 | 596 (257) | +$66.04 | +$55.82 to +$76.27 | +$66.36 / +$65.70 |
| old cache ($20k final volume) | same hour | +3c | 4391 | 2242 | 596 (257) | +$47.33 | +$38.26 to +$56.41 | +$47.48 / +$47.18 |
| old cache ($20k final volume) | 1h later | +1c | 4391 | 2242 | 596 (287) | +$73.71 | +$63.38 to +$84.04 | +$74.01 / +$73.39 |
| old cache ($20k final volume) | 1h later | +2c | 4391 | 2242 | 596 (287) | +$53.38 | +$44.34 to +$62.42 | +$53.47 / +$53.29 |
| old cache ($20k final volume) | 1h later | +3c | 4391 | 2242 | 596 (287) | +$37.33 | +$29.28 to +$45.39 | +$37.29 / +$37.38 |
| whole events (complete only) | same hour | +1c | 13063 | 3126 | 845 (717) | -$4.45 | -$9.32 to +$0.42 | -$4.89 / -$4.04 |
| whole events (complete only) | same hour | +2c | 13063 | 3126 | 845 (717) | -$17.18 | -$21.40 to -$12.95 | -$17.62 / -$16.75 |
| whole events (complete only) | same hour | +3c | 13063 | 3126 | 845 (717) | -$26.90 | -$30.63 to -$23.17 | -$27.34 / -$26.48 |
| whole events (complete only) | 1h later | +1c | 13063 | 3126 | 845 (738) | -$6.45 | -$11.00 to -$1.91 | -$7.90 / -$5.03 |
| whole events (complete only) | 1h later | +2c | 13063 | 3126 | 845 (738) | -$18.67 | -$22.63 to -$14.71 | -$19.88 / -$17.48 |
| whole events (complete only) | 1h later | +3c | 13063 | 3126 | 845 (738) | -$28.05 | -$31.56 to -$24.54 | -$29.09 / -$27.03 |
