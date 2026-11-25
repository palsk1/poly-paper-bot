# Player props vs sportsbooks (2026-11-24, `props.py`)

Research only, no track. Jan asked for 5 deep digs in different areas; this one is player props and other niche
sports bets (NBA / NFL / NHL / MLB player points, yards, touchdowns, first scorer, award futures).

## The ceiling first (rough guess)

- **Most in an average day:** about $0. Nothing we found beats the price after the fee.
- **Money needed:** $25 a bet would fit easily. NFL and NBA props trade millions of contracts each.
- **Bet size where it stops growing:** not reached. Pinnacle's own limit on props is $250 a bet.
- **Bad day:** about -$75 (three lost $25 bets in one game, since bets on one game win and lose together).

## What exists

- **Kalshi is where props live.** 734 prop / award series. Biggest by contracts traded (settled markets, Oct 2025 -
  Nov 2026): NFL touchdowns (KXNFLTD, 638 million), MLB home runs (389 million), NBA player points (KXNBAPTS,
  297 million), NFL first touchdown (282 million), NFL receiving yards (206 million), MLB strikeouts, NFL rushing /
  passing yards, NBA rebounds / threes / assists, NHL goals and points, soccer goal scorers. Each prop is a ladder of
  "Player: 20+", "25+", ... markets, listed a day or two before the game.
- **Polymarket** has 16,000 prop markets, but they barely trade (median gap 89c in the 10 Nov census). Its award
  futures are big (NBA MVP 2025-26: $95 million; Ballon d'Or 2026: $104 million), but every award is one event a
  year, so there is no history to test on.
- **Pinnacle** (the sharp bookie, free public site feed) lists about 350 player props at a time (NFL, NBA, NHL), $250
  limit. It keeps no history, so a bookie-vs-Kalshi test can only be live.

## Test 1: Kalshi vs Pinnacle, live (24 Nov, 13:23-17:44 UTC, 14 looks, 20 minutes apart)

Every Pinnacle prop with a half-point line (24.5 points = Kalshi "25+") matched to Kalshi's ladder by player name:
97 to 187 matches per look (NFL receptions / yards / rush attempts / passing TDs / interceptions, NBA points /
rebounds / assists / threes, NHL goals / assists / points). Pinnacle's cut taken out two ways; we use the less
favourable one.

- Kalshi's middle price sat **within half a cent** of Pinnacle's fair price (median -0.2c to -0.3c; 8 in 10 within
  2c). Kalshi's buy/sell gap is 2c; Pinnacle charges about 7c of margin per pair.
- Kalshi side cheaper than Pinnacle fair by 3c+ after the fee: **0** in all 14 looks. 1c+: 0 to 3 per look.
- Same as game winners (`backtest/sharp.md`): Kalshi's prop sellers copy the sharp bookie. No edge to buy.
- Saved in `bt_cache/pp/live.json.gz`; `props.py livescore` can settle them, but with 0 bets at 3c there is nothing
  to score.

## Test 2: Kalshi prop history at the real sell price

14 prop kinds, 1,000 random settled markets each (13,788 with quotes and a known start time), hourly real bid / ask
and every trade, start time from Kalshi's own schedule (`/milestones`). Buy at the real sell offer + Kalshi's fee,
$25 a bet, 24h / 6h / 2h / 30 min before the game, spread 10c at most.

| bet | bets | per $100 | exam |
|---|---|---|---|
| always Yes (the "over"), 2h before | 2,588 groups (9,036 bets) | **-$13.07** | Losing |
| always No (the "under"), 2h before | 2,537 groups (8,610 bets) | **-$4.74** | Losing |
| NFL first touchdown, Yes | 569 | -$34.30 | |
| NFL receiving yards, Yes | 785 | -$26.39 | |
| NBA player points, Yes / No | 756 / 754 | -$13.42 / -$10.23 | |
| NHL goal, Yes / No | 395 / 355 | -$5.03 / -$6.60 | |

People overpay for overs (Yes) the most, like long shots everywhere. The under only loses the fee and the gap.

**The player's own record** (how often he cleared the same line in his last 15 Kalshi markets, 5+ needed) forecasts
worse than the price (error 0.179 vs 0.162 on 6,119 markets). Buying where the record is 10-25c away from the price
loses $4-14 per $100 on both sides.

**Backward look** (246 cuts: family x side x time x price band): one lead, NFL player props, buy No where Yes is
bid 50-75c, 24h before kickoff: +$11.21 per $100 on 454 bets in 227 games, "Promising, needs more bets" (found by
looking).

**Fresh check, rule written before the data** (1,000 new random markets per NFL series): +$7.88 per $100 on 484
bets, +$5.18 at 1c more a share, so it passed its written bar (ahead at +1c), but first half -$5.34, second +$19.08,
"Ahead, but could be luck". **A third sample** (the first download, markets not in the other two) lost $13.60 per
$100 on 681 bets. **All three together: -$0.22 per $100 on 1,619 bets in 308 games** ("Behind, but could be bad
luck"). So it was luck. Bets in one NFL game move together, and there are only ~300 games in the data, so samples
swing by $20 per $100. Dropped.

## Traps (for the next dig)

- **Final volume is not a clean filter (again).** The first download kept only markets with 300+ contracts traded
  in the end. A long shot that comes in gets traded heavily after the goal, so the filter keeps winners: NHL goal
  long shots looked like **+$166 per $100**, the player's own record like +$7,000. The fair sample (no filter) shows
  NHL Yes at -$5. Use `PP_MINV=0` / `ufetch`. Same trap as `kmentions.md`.
- **Kalshi candles 100 times too small** on about half the prop markets (`props.fix_quotes`, same as
  `kmentions.load`): any quote strictly between 0 and 1c means the whole market came scaled down.
- Bets on one game are linked: count games, not bets (the exam does).

## Not dug

- Award futures (MVP, Rookie of the Year, Ballon d'Or): one event a year on each site, too few to test. A live
  Pinnacle-futures vs Polymarket check would be the only way.
- Soccer goal scorer props (EPL / UCL / La Liga): Kalshi's candles have almost no two-sided quotes before kickoff.

## Commands

    probe pp_scan                 # which prop / award series exist on Kalshi, Polymarket, Pinnacle
    probe pp_live_<min>_<every>   # Pinnacle vs Kalshi prop snapshots (pp_live = one look)
    probe pp_ufetch_<i>_<n>       # fair sample: 1,000 random settled markets per prop kind -> bt_cache/pp/
    probe pp_ffetch_<i>_<n>       # fresh NFL sample for the pre-written check
    python3 props.py ureport      # price bands, own record, backward look, exam
    python3 props.py freport      # the fresh check
