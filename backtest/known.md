# Bets still cheap after the answer is known (24 Nov 2026)

Tool: `known.py` (probes `kn_sfetch_<n>`, `kn_live`; offline `crypto`, `stocks`, `tennis`, `report`). Data: `bt_cache/kn/` in the
shared price store (3,976 Polymarket game markets, every trade from kickoff to payout in 1-minute steps, plus Gamma event fields),
reused `bt_cache/opt` (crypto), `bt_cache/stk` (stocks) and the `tennis-store` release. Paper only. Tables: `backtest/known_tables.md`.

**Verdict: dropped, no track.** Once the real answer is public, the winning side sits at 99c or more almost every time, on both
sites. When it still trades under 97c, that is a warning sign, not a bargain: our outside source was wrong (a close call, a late
game, a data mix-up) and those bets mostly lose. Buying the winner at 99c+ makes a few cents a bet, about $0.65 a day at $25 bets.

## Ceiling (rough guess)

- Most in an average day: under $1 (all three families together, at $25 a bet).
- Money needed: about $25-100 (each bet is paid within about 15 minutes to 2 hours).
- Where it stops growing: the profit is about 4c on a $25 bet; a bigger bet just meets the same thin line of 99.5c+ sellers.
- Bad day: one wrong call costs the whole bet (-$25), which eats about 600 wins.

## What was tested

| Family | Markets | When the answer is known | Winner still traded at 97c or less afterwards |
|---|---|---|---|
| Polymarket Bitcoin / Ethereum price bets (Feb-Nov 2026) | 14,076 | the Binance 1-minute price at the reference minute, or the first touch for "reach / dip" | 21 markets (1 in 670) |
| Polymarket stock close bets (Nov 2025-Nov 2026) | 13,934 | Nasdaq's official close, 2 minutes after 4 PM New York | 54 markets (1 in 260) |
| Polymarket league soccer games (Mar-Nov 2026) | 1,261 | kickoff + 2h15m (league games have no extra time) | 38 markets (1 in 33) |
| Kalshi tennis matches (Jun 2025-Nov 2026) | 21,886 | 365scores' match end (start + minutes of each set) | Kalshi closes the market a middle of 1 minute after the end, so there is almost no window |
| Polymarket right now (snapshot 24 Nov 13:21 UTC) | 5,377 open markets past their end date | - | the cheap ones are live games (the end date is the kickoff) and slow politics (see below) |

## The bot that buys a "known" winner still under 97c

Wait 5 minutes after the answer is fixed, buy the side our source says won if its last trade is 97c or less, pay the worst trade
of the next hour + 1c + fee: **44 bets, 29 lost, -$27.30 per $100** (exam "Behind, but could be bad luck"). Crypto: 4 of 5 lost,
all coins within 0.06% of the line (ETH on 22 Oct: the market knew better than our Binance minute). Soccer: 14 of 21 lost (games
that started late or were stopped, a few chess and cricket markets filed as soccer). Stocks: 11 of 18 lost (Netflix's share split,
range edges). The cheap price was the market telling us our source was wrong.

## The 99c grind

Buy the known winner at whatever it costs (last trade 90c+), worst trade of the next hour + fee, $25 a bet:

| Family | Bets | Lost | Average price | Per $100 | Paid within |
|---|---|---|---|---|---|
| League soccer after the whistle | 830 | 1 | 99.73c | +$0.06 | about 1.8 hours |
| Crypto price bets | 3,458 | 1 | 99.88c | +$0.07 | about 15 minutes |
| Stock close bets | 2,538 | 0 | 99.81c | +$0.27 | about 1.5 hours |

Crypto + stocks: 5,996 bets, +$0.16 per $100, exam "Promising, needs more bets", but it is $234 at $25 a bet over a year
(about $0.65 a day), shrinking each month (Polymarket pays these out faster now, so fewer trades after the answer), and the
one loss (ETH 22 Oct) cost as much as about 600 wins. Soccer: +$0.06 per $100, "Ahead, but could be luck". Not worth a track.

## Slow politics (from the live snapshot)

The real "decided but still cheap" money sits in politics: "Will Chuck Schumer be the next Senate Majority Leader?" at 93c 20 days
after the midterms, New Zealand's next prime minister at 81c 16 days after the vote, Serbia and Israel prime minister markets at
87-96c, about $340,000 for sale under 97c. These are not known answers: they wait for a vote in parliament, coalition talks or a
certification weeks away, and some do flip. This is the endgame "past the deadline" bet that already lost $167 on 709 bets
(backtest/report.md), and the live `endgame` track holds several of these at 86-93c today. Not redone. A fair version would need
an outside source (AP race calls, coalition news), which we don't have for free.

## Dispute risk

In this dig's window none of the 5,996 grind bets flipped on a dispute; the losses were all our own source being wrong. The UMA
statuses in the sports sample were all a plain "proposed" with automatic sports payouts. The only live markets at 99c+ with a
dispute (4 in the snapshot) are already skipped by the endgame track.

## Backward look

Starting from the losses: every loss was a market where the winner traded cheap after our "known" time. So the one rule that
helps is "skip it when the price disagrees with your source", which turns the idea into the 99c grind above. Nothing else shared.

## Traps

- Polymarket's Gamma events for finished games keep no end-of-game time (no `finishedTimestamp`, no score), only `closedTime`.
- "The winner reached 99c" is not "the game is over": 305 of 3,976 games fell back under 97c after touching 99c (late goals).
- Soccer end dates on Polymarket are the kickoff, so "past the end date" lists every live game.
- In a 5-minute step a single crumb trade can show 0.1c or 59c next to $30,000 traded at 99.9c: price buys at the worst trade of the next hour.
