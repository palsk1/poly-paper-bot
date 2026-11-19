# Kalshi's own settle number vs Binance: the 15-minute crypto tracks re-tested

Generated 2026-11-19T20:40:48Z. Code `kdocs.py run` (probe `kd_retest`). Paper only. Jan (19 Nov): "Download and do the re-test. After make a paper twin no matter the result, name it clearly."

Kalshi's number = `GET /live_data/events/{event}`, the CF Benchmarks 60-second average Kalshi settles on, one value a second, no login (`backtest/kalshi_docs.md`). Binance = what the tracks use today.

## In plain words (Claude, 19 Nov)

- **The twin does not beat the original.** With 3 minutes left, the old Binance check (`kc_maker_safe`) made
  **+$0.47 per $100** on 16,120 bets in 126 days (124 lost). The same bid checked on Kalshi's own settle number (the
  twin, `kc_maker_safe_kprice`) made **+$0.40 per $100** on 16,189 bets (103 lost). It loses a bit less often, but it
  also skips some good bets: where only Binance said "bet", those bets made +$0.32 per $100. Where only Kalshi's number said "bet", they made
  +$0.04. A tie, give or take luck. At 4-5 minutes left the twin is a hair ahead, at 1-3 minutes a hair behind.
- **Big news on the side: `kc_maker_safe` itself passes the exam on 4 months.** Verdict "Looks real": +$0.47 per
  $100, luck range +$0.36 to +$0.59, both halves ahead, worst case per $100 +$0.24 (above $0). At $10 a bet that is
  about +$765 over 126 days, about $6 a day. This is still a paper fill model (fills from the real trade tape,
  waiting behind the line), and live bets on the real tape earned less (+$0.18 per $100, `bigbets.md`). So the
  1 Dec live test still decides.
- **The 45-second buy (`kfastlive`)**: only 3 weeks of trade tapes. With Kalshi's number the waiting bids lost 0
  times (vs 1-2 with Binance), but they made fewer bets and the money is tiny ($5-15 in 3 weeks at $10 a bet).
  Too small to tell.
- **Bug found on the way (fixed):** candles for markets older than about mid-September come from Kalshi's
  `/historical` endpoint in dollars under the old cents names, so they came out 100 times too small (a 99c bid
  read as 1c). The first run of this test was wrong because of that (no-check bids "lost" a third of the time).
  `kcrypto.fix_cents` now repairs them when loading. Earlier kcrypto backtests used newer data and are not affected.
- Rules were fixed before the run (twin = the same bid with the z 2+ check on Kalshi's number, with the
  60-second-average fix). The twin runs live as a paper track anyway, as Jan asked.

## 1. kc_maker_safe's check: Binance vs Kalshi's own number

78304 windows with Kalshi's number, closing 2026-07-17 to 2026-11-19, all 7 coins. Same bid as the live tracks (one tick in front of the best bid on the leading side, 95c+), placed with M minutes left, filled only from real trades (kcrypto.py 'fair' fills). Only bids where all three checks could be computed are counted (candles repaired by `kcrypto.fix_cents`), so every line uses the same windows. P&L per $100 staked; '$10 bets' = total if every bet was $10.

| Minutes left | Check | Bets | Lost | Per $100 | $10 bets |
|---|---|---|---|---|---|
| 1 | no check (kc_maker) | 19378 | 244 | -$0.08 | -$154.41 |
| 1 | Binance z 2+ (kc_maker_safe) | 8859 | 67 | +$0.13 | +$116.05 |
| 1 | Binance + gap (kc_maker_safe_usd) | 4905 | 16 | +$0.16 | +$77.81 |
| 1 | **Kalshi's number z 2+ (twin)** | 7443 | 35 | +$0.07 | +$51.00 |
| 1 | Kalshi's number, no 1.5 fix | 9966 | 54 | +$0.08 | +$81.27 |
| 1 | Kalshi's number z 3+ | 3245 | 7 | +$0.21 | +$68.87 |
| 2 | no check (kc_maker) | 30166 | 410 | +$0.01 | +$24.85 |
| 2 | Binance z 2+ (kc_maker_safe) | 16692 | 129 | +$0.23 | +$380.44 |
| 2 | Binance + gap (kc_maker_safe_usd) | 12163 | 43 | +$0.31 | +$375.37 |
| 2 | **Kalshi's number z 2+ (twin)** | 16781 | 105 | +$0.14 | +$233.08 |
| 2 | Kalshi's number, no 1.5 fix | 21254 | 175 | +$0.10 | +$220.49 |
| 2 | Kalshi's number z 3+ | 7695 | 17 | +$0.31 | +$234.76 |
| 3 | no check (kc_maker) | 28681 | 426 | +$0.18 | +$517.08 |
| 3 | Binance z 2+ (kc_maker_safe) | 16120 | 124 | +$0.47 | +$765.49 |
| 3 | Binance + gap (kc_maker_safe_usd) | 12131 | 44 | +$0.54 | +$655.12 |
| 3 | **Kalshi's number z 2+ (twin)** | 16189 | 103 | +$0.40 | +$651.63 |
| 3 | Kalshi's number, no 1.5 fix | 21077 | 190 | +$0.36 | +$759.10 |
| 3 | Kalshi's number z 3+ | 6725 | 10 | +$0.55 | +$368.28 |
| 4 | no check (kc_maker) | 23736 | 369 | +$0.52 | +$1227.57 |
| 4 | Binance z 2+ (kc_maker_safe) | 13076 | 139 | +$0.58 | +$754.23 |
| 4 | Binance + gap (kc_maker_safe_usd) | 9812 | 60 | +$0.68 | +$675.47 |
| 4 | **Kalshi's number z 2+ (twin)** | 12806 | 93 | +$0.71 | +$909.72 |
| 4 | Kalshi's number, no 1.5 fix | 17317 | 178 | +$0.66 | +$1151.68 |
| 4 | Kalshi's number z 3+ | 4592 | 15 | +$0.65 | +$301.94 |
| 5 | no check (kc_maker) | 18041 | 358 | +$0.45 | +$820.70 |
| 5 | Binance z 2+ (kc_maker_safe) | 9699 | 136 | +$0.63 | +$613.27 |
| 5 | Binance + gap (kc_maker_safe_usd) | 7050 | 69 | +$0.73 | +$518.10 |
| 5 | **Kalshi's number z 2+ (twin)** | 9088 | 101 | +$0.72 | +$659.82 |
| 5 | Kalshi's number, no 1.5 fix | 13014 | 190 | +$0.64 | +$834.18 |
| 5 | Kalshi's number z 3+ | 2699 | 17 | +$0.70 | +$190.63 |

Where the two checks disagree (3 minutes left):

| Bets | Count | Lost | Per $100 |
|---|---|---|---|
| Binance says yes, Kalshi's number says no (the twin skips these) | 4073 | 77 | +$0.32 |
| Kalshi's number says yes, Binance says no (only the twin bets) | 4142 | 56 | +$0.04 |

By coin, 3 minutes left (bets / lost / per $100):

| Coin | Binance (kc_maker_safe) | Twin |
|---|---|---|
| KXBTC15M | 2322 / 29 / +$0.25 | 2312 / 23 / +$0.24 |
| KXETH15M | 2562 / 24 / +$0.32 | 2513 / 16 / +$0.35 |
| KXSOL15M | 2635 / 13 / +$0.67 | 2595 / 10 / +$0.54 |
| KXXRP15M | 2674 / 19 / +$0.57 | 2730 / 18 / +$0.48 |
| KXDOGE15M | 2587 / 15 / +$0.61 | 2579 / 7 / +$0.73 |
| KXHYPE15M | 1052 / 4 / +$0.62 | 1100 / 7 / +$0.21 |
| KXBNB15M | 2288 / 20 / +$0.32 | 2360 / 22 / +$0.10 |

Exam (3 minutes left, $10 bets):

- kc_maker_safe check on Binance (re-test, 3 min): {"id": "kc_maker_safe_check_on_binance_re_test_3_min", "name": "kc_maker_safe check on Binance (re-test, 3 min)", "bets": 16120, "tries": 6, "luck_tries": 163, "src": "kdocs.py run", "note": "19 Nov, Kalshi docs dig: same bid, the spot check done on Kalshi's free per-second settle number instead of Binance. Rule fixed before the run.", "groups": 16120, "events": 16120, "days": 126, "bunched": false, "staked": 159206.88, "profit": 753.12, "per100": 0.47, "lo100": 0.36, "hi100": 0.59, "floor100": 0.24, "no_loss": false, "half1": 0.55, "half2": 0.4, "luck_show": 0.22, "need": 3745, "more": 0, "pa
- kc_maker_safe check on Kalshi's own number (twin rule, 3 min): {"id": "kc_maker_safe_check_on_kalshi_s_own_number_twin_rule_3_min", "name": "kc_maker_safe check on Kalshi's own number (twin rule, 3 min)", "bets": 16189, "tries": 6, "luck_tries": 164, "src": "kdocs.py run", "note": "19 Nov, Kalshi docs dig: same bid, the spot check done on Kalshi's free per-second settle number instead of Binance. Rule fixed before the run.", "groups": 16189, "events": 16189, "days": 126, "bunched": false, "staked": 160216.62, "profit": 643.38, "per100": 0.4, "lo100": 0.3, "hi100": 0.5, "floor100": 0.19, "no_loss": false, "half1": 0.51, "half2": 0.29, "luck_show": 0.2, "ne

## 2. The last-seconds buy (the kfastlive idea): Binance vs Kalshi's own number

8758 windows with a real trade tape and Kalshi's number, closing 2026-10-28 to 2026-11-19. kfast.py's replay, unchanged, once with its Binance model and once with Kalshi's number deciding the side and the z. Taker = buy at the next real trade 1-4 s later, with fee; bid = a waiting order filled only by real trades ('fair'). The z scale for Kalshi's number is set from all windows (one number per seconds-left), so treat small differences as noise.

| Test | Model | Bets | Lost | Per $100 | $10 bets |
|---|---|---|---|---|---|
| bid 99.8c, 45 s left, z 2+ (kfastlive main) | Binance | 777 | 1 | +$0.07 | +$5.55 |
| bid 99.8c, 45 s left, z 2+ (kfastlive main) | Kalshi | 605 | 0 | +$0.20 | +$12.12 |
| bid 99.5c, 45 s left, z 2+ | Binance | 441 | 2 | +$0.05 | +$2.06 |
| bid 99.5c, 45 s left, z 2+ | Kalshi | 292 | 0 | +$0.50 | +$14.67 |
| taker, 45 s left, z 4+ | Binance | 656 | 3 | +$0.28 | +$18.92 |
| taker, 45 s left, z 4+ | Kalshi | 256 | 0 | +$0.20 | +$5.25 |
| taker, 45 s left, z 2+ | Binance | 1564 | 25 | -$0.25 | +$407.32 |
| taker, 45 s left, z 2+ | Kalshi | 856 | 14 | -$0.74 | -$92.68 |
| taker, 20 s left, z 3+ | Binance | 544 | 27 | -$0.24 | -$173.20 |
| taker, 20 s left, z 3+ | Kalshi | 173 | 1 | -$0.26 | -$4.07 |
| bid 99.8c, 20 s left, z 3+ | Binance | 324 | 0 | +$0.20 | +$6.49 |
| bid 99.8c, 20 s left, z 3+ | Kalshi | 195 | 0 | +$0.20 | +$3.91 |

