# Bets still cheap after the answer is known

Generated 2026-11-24 13:26 UTC by `known.py report`. Paper only, research only.

**Question (Jan, 24 Nov):** are there markets where the real answer is already public (game over, price fixed, market closed) but the winning side can still be bought under 97-99c? How often, how much, how long is the money stuck, and how often does the payout go the other way?

## 1. How often the known winner is still cheap

Every real trade, in 1- or 5-minute steps. 'Known' = the moment the outside source fixes the answer. A step counts as cheap when someone traded the known winner at that price or less (the kind count: one crumb trade is enough).

| Family | Markets | Traded after the answer was known | Winner traded at 97c or less | at 99c or less | Our source disagreed with the payout |
|---|---|---|---|---|---|
| Bitcoin / Ethereum price bets (answer = Binance's 1-minute price) | 14,076 | 3,477 | 21 ($587,044 traded) | 67 ($733,770) | 7 |
| Stock close bets (answer = Nasdaq's official close) | 13,934 | 2,605 | 54 ($154,610 traded) | 204 ($209,064) | 19 |
| League soccer, after the final whistle (kickoff + 2h15m) | 1,261 | 867 | 38 ($213,766 traded) | 50 ($225,818) | 19 |

## 2. A bot that buys the known winner when it is still under 97c

Wait 5 minutes after the answer is fixed (soccer: kickoff + 2h15m), buy the side the source says won if its last trade is 97c or less, pay the WORST trade of the next hour + 1c + fee, $25 a bet, paid by the real result.

| Family | Bets | Lost | Profit per $100 |
|---|---|---|---|
| Bitcoin / Ethereum price bets (answer = Binance's 1-minute price) | 5 | 4 | -$77.93 |
| Stock close bets (answer = Nasdaq's official close) | 18 | 11 | +$28.84 |
| League soccer, after the final whistle (kickoff + 2h15m) | 21 | 14 | -$62.40 |

## 3. The 99c grind: buy the known winner at whatever it costs

| Family | Bets | Lost | Average price | Profit per $100 (worst trade of the hour) | Hours until paid | $ traded in that hour |
|---|---|---|---|---|---|---|
| League soccer after the whistle | 830 | 1 | 99.73c | +$0.06 | 1.8 | $881,837 |
| Crypto price bets | 3458 | 1 | 99.88c | +$0.07 | under 1 (pays fast) | $4,394,052 |
| Stock close bets | 2538 | 0 | 99.81c | +$0.27 | under 1 (pays fast) | $1,680,214 |

## 4. Exam

- **Known answer, winner still under 97c: buy it (crypto, stocks, soccer):** 44 bets, -$27.30 per $100, verdict **Behind, but could be bad luck**.
- **Soccer after the final whistle: buy the leader at 99c+ (the grind):** 830 bets, +$0.06 per $100, verdict **Ahead, but could be luck**.
- **Crypto / stock bets after the answer is fixed: buy the winner at 99c+:** 5996 bets, +$0.16 per $100, verdict **Promising, needs more bets**.
