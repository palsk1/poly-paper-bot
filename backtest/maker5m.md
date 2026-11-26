# Being the seller on Bitcoin 5-minute bets (26 Nov 2026)

Jan asked: "If they have this sellers advantage, doesn't it make more sense to be one, or does it involve a lot
of money?" Tool: `maker5m.py` (research only, reads logs, never trades). All numbers: `backtest/maker5m_raw.txt`.

## Verdict: at our speed, sellers lose. Dropped, no bot.

The money doesn't decide it: the setup fits a $100-300 bank. Speed does. The seller's edge only exists if you can
pull your offer **the instant** Bitcoin moves. At the speed our box really has (0.1-0.25 s from hearing a move to
the pull landing), every version loses, and the seller reward doesn't cover it.

## What we tested
- **Data:** the speed check box's logs, 17-25 Nov, 2,363 Bitcoin 5-minute windows (9 days). The log has the top of
  Polymarket's book to the millisecond, every real trade, Binance's price and each window's result.
- **The seller:** keep a 5-share waiting offer on both sides (sell Up at the best ask, buy Up at the best bid),
  follow the best price as it moves, never more than 20 shares one way in a window, stop 20 s before the end.
  Every fill is held to the result. No fee for the seller.
- **Fills counted from real trades:** our order joins the back of the line at the best price. It only fills when
  real trades have eaten the shares in front of it (or a buyer sweeps through our price). Nothing is guessed.
- **Speed:** every move or pull lands 0, 0.1, 0.25 or 0.5 s after the box hears the reason. Polymarket holds
  buyers 0.15 s on these windows and lets sellers pull at once, so a pull that lands before the match saves us.
  Our real orders took 0.27-1 s round trip; a pull is quicker, so 0.1-0.25 s is the honest range.
- **Rules tried (32 versions):** plain (just follow the best price); pull an offer for 2 s when Binance moves the
  fair price 1c, 2c or 3c against it; only keep offers that sit 0-4c on the safe side of Binance's fair price.
- **Seller reward:** counted apart, as 20 cents of every $1 of fee the buyer paid us (the old flat rebate). That is
  about +$0.65 per $100. Polymarket is moving it to volume tiers, so a small seller would get less. Treat it as the
  most we could get.

## Results, per $100 locked in bets (before the reward)

| Rule | Instant (0 s) | 0.1 s | 0.25 s | 0.5 s |
|---|---|---|---|---|
| Plain | -$0.42 | -$2.21 | -$2.71 | -$3.27 |
| Pull on a 1c Binance move | **+$0.25** | -$1.41 | -$2.02 | -$2.58 |
| Pull on a 2c move | +$0.17 | -$1.47 | -$1.99 | -$2.68 |
| Pull on a 3c move | +$0.04 | -$1.43 | -$2.14 | -$2.73 |
| Only 2c+ on the safe side of fair | +$1.73 | -$1.06 | -$2.54 | -$4.41 |
| Only 4c+ on the safe side of fair | +$1.97 | -$0.67 | -$3.09 | -$4.75 |

The reward adds at most about +$0.65 per $100 everywhere. So only the instant column is ahead, and nobody is
instant: Binance's price reaches Stockholm about 0.13 s after it happens, and the pros sit next to the exchanges.

- **Every day lost** at 0.1 s and 0.25 s (9 of 9 days). Exam on the best real-speed version (pull on a 2c move,
  0.25 s): **"Losing"**, -$1.99 per $100, luck range -$2.17 to -$1.81, both halves behind.
- **Where it loses** (pull 2c, 0.25 s): fills right after Bitcoin moved against us -$4.43 per $100 (19,319 fills);
  fills after a move our way +$0.66; fills with Bitcoin quiet -$1.68. Even quiet fills lose: standing at the back of
  the line, we get filled when the line is eaten, which is just before the price moves through us.
- **By price:** loses in every 10c band from 20c to 100c. Nothing to cut out.

## For a $100-300 bank
Smallest setup: 5-share offers, at most 5 shares one way and 10 a side per window, pull on a 2c move.

| | At 0.1 s | At 0.25 s |
|---|---|---|
| Bought in a day | about $3,200 | about $3,300 |
| Result a day (no reward) | **-$45** | **-$61** |
| Seller reward a day, at most | +$22 | +$23 |
| Result a day with the reward | about -$22 | about -$39 |
| Worst day | -$118 | -$120 |
| Money tied up at once | about $20 in a window (about $40 with the last window still settling) | same |

So it doesn't need a lot of money: $50 would run it. It just loses that money, roughly $20-60 a day.

**Ceiling (rough guess):** an instant bot, which we can't be, might make about +$0.90 per $100 with the reward,
about $30 a day on this setup. That is the pros' money, and it is why their quotes move within 0.1-0.2 s.

## How this fits what we knew
- GoodFallen (`backtest/wallet5m.md`): his waiting orders made money because he trades in the first seconds after
  Bitcoin moves; his plain waiting orders made about +$0.63 per $100 before the reward. Ours, at our speed, lose.
- The 5 Polymarket maker tracks (12 Nov) lost $416 and earned $7 in rewards. Same lesson: slow sellers get picked off.
- The speed check's buy side is the mirror image: a buyer who is quick after a jump wins exactly the money a slow
  seller loses. That is the side our live speed bot already tests.

## Limits
- Our order isn't in the real log. A buyer who filled us would not have filled someone else, so the line in front
  of us may be a bit shorter in real life. With 5 shares that is small, and it would help the instant column most.
- The book log writes the line's size only when it changes by 20 in 100 or more, so the shares in front of us are
  rounded.
- 17 Nov is a part day (from 14:55 UTC), counted as a day in the per-day numbers.
- Found by looking: the rules were not fixed before. That doesn't matter much here, since everything lost.

Don't redo this unless we get a box next to the exchange or Polymarket changes the buyer wait.
