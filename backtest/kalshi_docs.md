# Kalshi's API docs, read end to end (19 Nov 2026)

Jan asked: "did you read Kalshi's documentation?" (docs.kalshi.com). Honest answer before today: only the parts
the bot needed. Today we read all of it: about 290 pages (guides, every endpoint, every websocket channel, the
FIX pages and the whole changelog back to April 2025). We skipped only the pages for perps, clearing firms (FCM)
and margin, which are for institutions. Then we tried every new piece that needs no login from GitHub
(`kdocs.py`, probes `kd_check`, `kd_depth`, `kd_agree`). This mirrors the 11 Nov Polymarket API check.

## The one real find: Kalshi shows its own settle number, every second, for free

Each 15-minute crypto window settles on CF Benchmarks' index (BRTI for Bitcoin), averaged over the last 60
seconds. We never had that number. Our tracks use Binance instead, and Binance runs about 0.09% high and picked
the wrong winner in 178 of 8,499 windows (`backtest/kfast.md`, `backtest/kcloss.md`).

`GET /live_data/events/{event_ticker}` (added 30 Jul 2026) needs **no login**. For any 15-minute crypto event it
returns 3,601 points, one a second, for the hour before the close. The last point equals Kalshi's own
`expiration_value` to the cent (checked on 8 windows, Bitcoin and Ether). It works from GitHub Actions (0.4 s a
call) and goes back at least 120 days (to 22 Jul). Each call covers an hour, so 4 months of Bitcoin is about
2,900 calls, about 20 minutes.

Example, the 06:30 UTC Bitcoin window on 19 Nov: Kalshi's number at the close was $63,476.75 (line $63,398.80,
so Yes won). Binance's last-minute average was $63,539.26, $62 higher. Both said Yes here, but on a close
window that gap is the difference between a win and a loss.

**Quick check on 600 recent windows** (`kd_agree`, the last 300 settled Bitcoin and 300 Ether windows, about
3 days, 19 Nov): Kalshi's last point matched the result in **600 of 600**. Which side was ahead with time left:

| | Kalshi's own number | Binance, 60 s average | Binance wrong, Kalshi right | Kalshi wrong, Binance right |
|---|---|---|---|---|
| Bitcoin, 45 s left | 287 of 300 | 243 of 300 | 51 | 7 |
| Bitcoin, 3 min left | 262 of 300 | 233 of 300 | | |
| Ether, 45 s left | 287 of 300 | 256 of 300 | 37 | 6 |
| Ether, 3 min left | 264 of 300 | 248 of 300 | | |

Binance sat about 0.10% above Kalshi's number (median, both coins). Big caveat: these are **all** windows,
including the coin flips where the price sits right on the line. Our tracks only bet when the coin is far past
the line, where Binance is usually right anyway, and `kc_maker_safe_usd` already moves Binance down by 0.09%. So
this does not yet say how many of *our* losing bets it would have saved. That is the next dig.

What it could fix:
- `kc_maker_safe` / `kc_maker_safe_usd` check "is the coin far past the line" with Binance. The settle number
  itself would remove the 0.09% gap and most of the wrong-winner windows. Their rules are locked (1 Dec test), so
  this would be a new twin, not a change.
- The fast Kalshi tests (`kfastlive`) buy 45 s before the close. With 45 s left, 15 of the 60 seconds in the
  average are already fixed and visible here.
- A cleaner backtest of both, on 4 months instead of 14 days.

## Other useful things (smaller)

| Feature | What it is | Use for us |
|---|---|---|
| Fees, checked live | KXBTC15M / ETH / SOL: fee type "quadratic" (no fee on waiting orders), **no fee change scheduled** (`/series/fee_changes`) | kc_maker's "no maker fee" still true. Kalshi does add maker fees to some series (combos since 20 Aug, a few tech series in Sept), so re-check before real money |
| Order groups | Auto-cancel all your orders once more than N contracts fill within 15 s | Real pick-off brake for a waiting-order bot |
| Post-only orders | Never take, never pay a taker fee; cancelled if they would cross | A real kc_maker must use it |
| Queue position | `/portfolio/orders/{id}/queue_position`: contracts ahead of you in line | Would replace our paper guess "behind the queue" (needs a key) |
| Amend keeps your place | Cutting size or changing only expiry keeps your spot in line; a new price goes to the back | Real bot detail |
| Cancel on pause | `cancel_order_on_pause`: drop orders when trading pauses (every Thursday 03:00-05:00 New York time) | Real bot detail |
| Cancel on disconnect | Only over FIX (the pro line), not REST | Not for us |
| CF Benchmarks feed | The raw index, 1 or 5 times a second, plus the running 60 s average in the final minute; websocket or REST | **Needs a Kalshi API key** (and an entitlement for REST). The free chart above covers most of it |
| Websockets | Every channel, even public prices, needs a key | Jan's server can't stream Kalshi without a key; keep 1 s polling |
| Many books in one call | `/markets/orderbooks?tickers=` up to 100 markets | Faster scans (kalshi_patient), small win |
| Weather index | `/live_data/weather/{city}`: Kalshi's own minute temperature (Miami so far) behind hourly temperature markets | Weather was dropped; only worth a look if hourly markets spread |
| Incentive programs | Liquidity rewards on some series (e.g. KXLUVA) | US members only; none on 15-minute crypto (checked again) |
| Location check | Since Aug 2026, API keys need a location attestation to trade Sports, Elections and Entertainment | Part of Jan's "may I trade Kalshi from Sweden" check |
| Rate limits | Basic tier: 200 read tokens a second (about 20 calls), a free upgrade to Advanced exists | Plenty for us |
| Demo site | demo.kalshi.co with fake money and its own keys | Could test a real bot's order code without money |

Nothing else changes our tracks. Two traps to remember: Kalshi's maintenance pause (Thursday 03:00-05:00 New
York time) and that orders can't even be cancelled once a market's close time passes.

## Best next step (Jan decides)

Download Kalshi's own per-second settle number for 4 months of 15-minute windows (Bitcoin first, then the other
coins), and re-run the `kc_maker_safe` spot check and the 45-second buy with it instead of Binance. About an hour
of probe time, no key, no money, research only. If it cuts the losing windows a lot, it becomes a new paper twin
next to the locked tracks.
