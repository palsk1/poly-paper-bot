# Test before results: how a backtest lead becomes "worth real money"

Written 2026-11-09, before any holdout data was looked at. Change it only with Jan's OK, and never after seeing
the result it would change.

## 1. Every engine change passes the sanity checks first

`python3 btcheck.py selftest` (offline, ~15 s) and the `btcheck` probe on real data (`backtest/checks.md`):

- **Fair-coin world.** On fake markets where every price is exactly right, every strategy must lose its costs and
  no more. A planted bug (stop-loss booked at the stop price after a gap) must be caught.
- **Second simulator.** A separate, small simulator re-walks every trade from the raw price history. Entry, exit and
  profit must match the engine to a tenth of a cent.
- **Random entries** on the same real data, held to the end, should lose about the costs.

If one fails, no backtest number counts until it's fixed.

## 2. The decision number is the pessimistic one

- Fill = history price **+2c** (one tick worse than the old +1c main case) plus the taker fee.
- Entry **1 hour after** the signal. The "next recorded price" column is shown as a stress test.
- A take-profit seen above its target is booked **at the target** (history is 12-hourly; the live bot would have
  sold near the target, not at the higher price seen later).
- Thin markets (tiny volume, mention markets) are also shown at +5c.

## 3. A lead has to beat random entries with the same exits

Same hour, same days-to-end window, same price band, same take-profit and stop rules, same costs. If the
strategy doesn't beat those twins, the "edge" is in the band or the exits, not the signal.

## 4. Order of tests (never skip, never go back)

1. **Sweep** the parameters on the whole in-sample period (ends before 2026-11-10). Allowed: looking.
2. **Walk-forward on two halves** (split at the middle trade): pick the best setting on one half, score it on the other, and
   the other way round. Something that wins one half and loses the other is a regime bet, not an edge.
3. **Holdout, once.** Markets ending **2026-11-10 or later** are kept out of every check (btcheck drops them). From
   **2026-12-21** the `btholdout` probe scores the pre-registered tests below, once (it refreshes the
   cache first). Its log is committed as `backtest/holdout.md`; once that file exists, `btholdout` refuses to run again. No rule changes between now and then for these tests, and don't rerun `calib.py` or `backtest.py` slices about
   mention markets or panic fades on data past 2026-11-10 before then (those tools don't hold the holdout back).

## 5. Pre-registered holdout tests (fixed now)

| Test | Rule | Pass bar |
|---|---|---|
| `mention_no` | NO at 25-90c, first time a "will X say Y" market is within 7 days of its end, one bet per event, +2c + fee, held | ahead, and band low end above -$5 per $100 |
| `panic_fade_10c` | engine, 2c + 1 hour later, take-profit at the target | ahead, and band low end above -$5 per $100 |
| `soccer_draw` (added 2026-11-10, `census.py`) | YES on a soccer full-time draw priced 15-50c 24h before kickoff, filled at the first real buy of it before kickoff +1c + fee, held. Not in `btholdout` yet: score with the census sports fetch on games from 2026-11-10 on | ahead, and band low end above -$5 per $100 |
| `boring_no` (added 2026-11-10, Jan's OK, `winners.py`) | Topic "other" (`calib.topic`), the first time No's last traded price is at 90-97c with more than 30 days to the end date: wait 5 minutes, take the next real $100+ buy of No within 6 hours, +1c + fee, $25 a bet, one bet per market, no bet if that buy is more than 2c outside the band. Exactly `winners.rule_bets` with `PRESETS[2]`. Not in `btholdout` yet: fetch trade lists (`informed.py`) for markets ending 2026-11-10 or later, then `winners.py drill` | ahead, and band low end above -$5 per $100 |
| `crypto_no` (added 2026-11-10, Jan's OK, `winners.py`) | Topic "crypto price", the first time No is at 70-90c with 3-7 days to the end date, same fill rule. Exactly `winners.rule_bets` with `PRESETS[0]`. Scored the same way | ahead, and band low end above -$5 per $100 |
| `soccer_draw_mid` (secondary, added 2026-11-10, `digs.py draws`) | Same as `soccer_draw` but only draws priced 22-32c and only outside the big leagues (slugs epl, lal, sea, bun, fl1, ucl, uel). Found by slicing in-sample data, so it only counts if `soccer_draw` also passes | ahead at +1c |
| `combo_moving` (added 2026-11-10, Jan's OK, `combo.py`) | The everything-together model, "moving prices only, no clock" version, frozen: same 14 inputs and settings as `combo.fit` (random_state 1), learned on every usable market that ended before 2026-11-10, only on market-days where the price moved 0.2c or more since the day before. Judged on noons from 2026-11-10 on, markets ending 2026-11-10 or later, events it never learned from, moving prices only. Bets when its chance is 12c or more above the cost (chart + `yesno.POLY_EXTRA` + fee, cost 5-95c), one bet per market at the first such noon, $25. Counted at the first real buy within 3 hours +1c + fee (`exam.fills`); bets nobody could buy don't count. Exactly `combo.holdout()` (probe `btcomboholdout`, after a fresh fetch of markets ending 2026-11-10 or later) | ahead, and band low end above -$5 per $100 |
| `cs2_fav_day` (added 2026-11-11, `cs2.py`) | Polymarket CS2 match winner (slug `cs2-`, market type moneyline): the team whose chart price is 70-97c 24 hours before the listed start, filled at the first real buy of that team within 3 hours and before the start, +1c + fee, $25, held to the result. Exactly `cs2.py` rule `fav24`: `CS2_HOLDOUT=1 python3 cs2.py exam fav24` after fresh fetches (census sports fetch, `cs2_fetch`, `cs2_ai`), games from 2026-11-10 on | ahead, and band low end above -$5 per $100 |
| `cs2_fav_day_b` (secondary, added 2026-11-11) | Same, only bo3.gg tier B tournaments (rule `fav24b`). Found by slicing in-sample data, so it only counts if `cs2_fav_day` also passes | ahead at +1c |

A pass is not proof. It means the lead survived one fresh look and the live paper track is worth watching to
2027-01-01. The money decision still uses the live trust score (90% bar, many strategies tested).

## 5b. Pre-registered live test: kc_maker_safe (fixed 2026-11-10, Jan's OK)

Written before the result, from `backtest/kcdepth.md` (probe `btkcdepth`, run 42823059046). Don't move it.

- **What counts:** the live paper track `kc_maker_safe` (state/tracks.json), closed bets only, from its start on
  2026-11-09 19:00 UTC, with its rules as they are today. A rule change restarts the count.
- **When:** once, at the first daily look after the **2,500th** closed live bet (about 1 Dec at ~115 bets a day).
  No earlier verdict: peeking at 300 / 600 / 1,000 / 1,500 bets is fine for interest, but none of them counts.
- **Pass:** live P&L above **+$0.22 per $100** staked (all closed bets, $10 paper orders).
  A break-even rule passes this about 10 times in 100; if the 60-day backtest (+$0.57) is right, about 96 in 100.
- **Fail:** at or below +$0.22. Then kc_maker_safe is not the money pick.
- A pass still leaves two open checks before real money: whether $25-100 orders fill the same, and whether Kalshi
  takes a Swedish account (Jan's job).
- **Fill rule fix (2026-11-10, Jan: "Fix it", `backtest/bigbets.md`):** this is a bug fix in how a paper bid is
  counted as filled, not a rule change, so the count does not restart. From then on the bot counts only contracts
  really sold at our price (after the queue) or below. Bets closed before the fix were counted the old, kinder way,
  so at scoring time **every** closed bet is re-scored on its real trade tape with the fixed rule (probe
  `big_kalshi`, the "$10" row), and that number is the one compared with +$0.22. Pass bar unchanged.

## 6. Keep it simple

Rule-based only. No machine learning on top of a signal that hasn't passed 1-4: it would just fit the noise better.
