# New market families, last 3 months (27 Nov 2026)

Jan: "spawn maximum of researchers and go crazy". Idea: bet families a site started recently may have fewer pros
pricing them. `newfam.py scan` (probe `nf_scan`, about 4.5 hours) listed every Kalshi series whose first market
opened on or after 27 Aug 2026 and has nothing in Kalshi's older archive (2,666 of 17,148 series), and every
Polymarket event family (slug without dates and numbers) first started since then (70 families with 3+ events;
`nf_scanp` = Polymarket only). Data: `bt_cache/nf/scan.json.gz` in the price store; `python3 newfam.py report`.

## What is new (by money traded)

- **Kalshi, new 15-minute "up in the next 15 minutes?" windows outside crypto** (from 7 Oct): gold, silver, WTI,
  Brent, natural gas, copper, platinum, palladium, 5 currency pairs, S&P 500, 4 Treasury yields. Gold alone traded
  1.66 billion contracts in 58 days, more than any crypto window. **Dug: `k15x.py`, the one lead (below).**
- Kalshi sports side bets (NBA quarters / halves, NHL periods, protected player props, new soccer leagues):
  props and side bets were dug before (`props.md`, `census.md`), not redone.
- **Kalshi table tennis (Liga Pro, TT Elite, TT Star), eBasketball, eSoccer, eFootball**, round the clock,
  ~30,000 settled games. **Dug: `kesport.py`, dropped.**
- Kalshi daily AAA gas price per state (50 new series): gas was dug on 9 and 23 Nov (`sources.md`), dead, not redone.
- Kalshi one-offs (next NVIDIA CEO, press secretary, GTA VI, Grammys, Golden Globes): one event each, no history.
- **Polymarket GPU rental prices (Ornn index, about $10 million).** **Dug: `gpurent.py`, too early.**
- **Polymarket Treasury yield "how high / how low" ladders** (also on Kalshi). **Dug: `tyield.py`, dropped.**
- Polymarket foreign central bank decisions (Canada, Swiss, Australia, NZ, Chile, South Africa, Korea),
  AI lab ranks (dug 22 Nov, `aim.md`), ship traffic through canals, Fear & Greed index, gold / silver / oil
  15-minute up-or-down (under $10 traded each): small or already dug.

## Results

| Dig | What | Verdict |
|---|---|---|
| `k15x.py` (`k15x.md`) | Our real Kalshi bot's rule (kc_maker_safe_usd: bid 1c above the best bid on the leading side with 3 min left, cushion 2.3 on Kalshi's own number) on the 18 new non-crypto 15-minute series, 57,000+ windows | **+$0.60 per $100 on 5,402 bets, "Looks real"** (first half +$0.68, fresh half +$0.51, every week ahead). Currencies best (+$1.01, Looks real), metals +$0.53, oil about even, yields behind. Plain kc_maker and the 45-second buy lose |
| `kesport.py` (`kesport.md`) | Table tennis, eBasketball, eSoccer vs player ratings built from Kalshi's own results | Price beats the ratings everywhere (-$2 to -$20 per $100). One lean, a waiting bid on the eSoccer tie (+$12.73 on 800 fills, "could be luck"), is fading to $0. Dropped |
| `gpurent.py` (`gpurent.md`) | GPU rental price bets vs Ornn's free 3-month index history | The new monthly bets settle from January: too early. Older settled ones: price guesses better, 11-13 bets. Re-check Jan-Feb |
| `tyield.py` (`tyield.md`) | Treasury yield ladders, both sites, vs a touch model on Treasury.gov closes | All the profit is one September yield jump; Kalshi -$6.20 per $100 on 864 bets. Dropped, re-check January |

## The lead's ceiling (rough guess, `k15x.md`)

- Most in an average day: about $20 at $50 bids, $30 at $100 bids ($2.17 at $4, $5.19 at $10).
- Money needed: about $300-500 at $50 bids (money comes back every 15 minutes).
- Stops growing at: about $50-100 a bid (only 3 of 4 bids fill whole at $100).
- Bad day: about -$64 at $50 bids, -$144 at $100.

Caveats: history only (57 days), settings grid of 160 tries, rule copied from crypto (not invented here). Ties pay
Yes. Brent sits in the crypto part of the Kalshi account (exchange index 2), USD/CAD in index 0: check each series
before any real bot.
