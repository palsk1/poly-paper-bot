# Sharp fair price backtest: Polymarket soccer vs Betfair Exchange closing odds

Run 2026-11-09T11:40Z (`python3 sharp.py bt`, probe input `sharp_bt`). Leagues: E0, SP1, D1, I1, F1 (top 5 Europe); seasons 2025-26 and 2026-27 so far. 1,230 games matched, 3,678 outcomes (home/draw/away) priced. (Gamma stops at 2,000 events per series, so the EPL and Serie A lists are cut short; the sample is still large.)

Polymarket price = price history 15 min before kickoff. Fair = Betfair closing odds with the margin removed, the less favorable of two methods. Fee = the market's taker fee. Result = Polymarket's settlement.
Betfair's closing price is 15 minutes newer than the price we buy at, so this flatters the strategy.

## How close the two prices are

- Polymarket minus Betfair fair: median -0.0c, middle half between -0.4c and +0.4c
- Prediction error (Brier, lower is better): Polymarket 0.1966, Betfair fair 0.1969 (a tie)

## Rule results (buy 1 share each time the edge clears the bar)

| slippage | bar | bets | won | cost | paid out | profit | per $100 |
|---|---|---|---|---|---|---|---|
| 0c | 1c | 169 | 88 | $82.62 | $88.00 | $+5.38 | $+6.51 |
| 0c | 2c | 24 | 12 | $11.12 | $12.00 | $+0.88 | $+7.90 |
| 0c | 3c | 16 | 7 | $6.85 | $7.00 | $+0.15 | $+2.16 |
| 0c | 5c | 14 | 6 | $5.90 | $6.00 | $+0.10 | $+1.71 |
| 1c | 1c | 24 | 12 | $11.36 | $12.00 | $+0.64 | $+5.63 |
| 1c | 2c | 16 | 7 | $7.01 | $7.00 | $-0.01 | $-0.17 |
| 1c | 3c | 14 | 6 | $6.04 | $6.00 | $-0.04 | $-0.65 |
| 1c | 5c | 14 | 6 | $6.04 | $6.00 | $-0.04 | $-0.65 |
| 2c | 1c | 16 | 7 | $7.17 | $7.00 | $-0.17 | $-2.40 |
| 2c | 2c | 14 | 6 | $6.18 | $6.00 | $-0.18 | $-2.91 |
| 2c | 3c | 14 | 6 | $6.18 | $6.00 | $-0.18 | $-2.91 |
| 2c | 5c | 14 | 6 | $6.18 | $6.00 | $-0.18 | $-2.91 |

## Verdict

Polymarket soccer prices just before kickoff are the sharp price (to within half a cent, and just as accurate). Gaps big enough to pay the fee are rare (14-24 in 1,230 games) and come out about even once you pay even 1c of spread. The 0c-slippage line is not reachable in practice (you can't buy at the middle price). No edge for a slow bot. The live track `sharp_pinnacle` stays on as a cheap check of earlier hours (up to 24h before kickoff) and other sports.
