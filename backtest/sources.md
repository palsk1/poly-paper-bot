# Who reads the settle source first? (2026-11-09, `sources.py`, probe `src_*`)

Question: for market families that settle on a public website or data feed, can a free reader see the answer
earlier or better than the traders, and does the price lag?

## 1. Map (probe `src_map`, `src_kdaily`, `src_precur`)

19,011 open Polymarket events and 15,994 Kalshi series, grouped by the domain in their rules. Big
"data-settled" families with short horizons: crypto (Binance / CF Benchmarks), weather (aviationweather.gov,
weather.com, NWS), stocks and commodities (Pyth, Google, ICE), **US gas price (AAA, Kalshi $26M + $14M
contracts lifetime)**, Netflix / Spotify / Billboard / Apple charts, Truth Social and Elon post counts, Fed Register
executive orders, ERCOT power load, SOFR, Freddie Mac mortgage rate, USGS earthquakes, IMF PortWatch (Hormuz).

Readable from GitHub Actions (probe `src_reach`): GasBuddy, AAA, White House actions page + feed, Federal Register
API (incl. public inspection), Roll Call factba.se, xtracker, ERCOT dashboard JSON, USGS live feed, Apple top-apps
RSS, TSA, Netflix Tudum top 10, Mortgage News Daily, kworb (Spotify), NY Fed SOFR API, IMF PortWatch ArcGIS,
Box Office Mojo, Yahoo RBOB futures. Blocked (403/401): Truth Social API, FlixPatrol, LMArena, RealClearPolling,
Pyth hermes.

## 2. US gas price, Kalshi KXAAAGASD (probe `src_gas`, `src_gas_KXAAAGASW`)

68 daily ladders (Sep-Nov 2026). Average miss vs the AAA settle value, in cents:

| Guess made (UTC, day before) | 14h | 16h | 18h | 20h | 22h | 2h |
|---|---|---|---|---|---|---|
| Market (where the ladder crosses 50c) | 0.55 | 0.39 | 0.30 | 0.25 | 0.20 | 0.16 |
| Yesterday's value | 1.34 | 1.37 | 1.41 | 1.41 | 1.41 | 1.49 |
| Yesterday + 0.7 x last change (best trend rule) | 0.82 | 0.82 | 0.85 | 0.85 | 0.85 | 0.96 |

The market gets sharper all day, so traders are already reading live station data (GasBuddy / OPIS) during the
day. Every trend rule lost $34-80 per $100 at +1c + fee. Weekly ladder (KXAAAGASW, 10 weeks): same picture.
**Dead unless a live GasBuddy reading beats the market at 14-18h UTC; that needs a forward recording to test.**

## 3. Earthquakes, Kalshi KXBIGGESTQUAKE (probe `src_quake`)

60 days, USGS catalog vs 1-minute Kalshi candles. The rung a quake decides reaches a 90c bid typically **5-20
minutes after the quake**, which is about when USGS posts it. A bot that checks every 5 minutes (plus run time)
arrives with or after the crowd. Slow cases (1-3 hours) were magnitude revisions, not slow traders.
Volume is tiny (a few thousand contracts a day). **Dropped.**

## 4. Executive orders, Kalshi KXEOWEEK (probe `src_eo`)

The Federal Register (the settle source) publishes an EO a median 5 days after signing; the White House posts it
the same day. So the count is known days before it settles. But at the end of the week the decided rungs already
trade at 99c / 1c (10 weeks, 36 rungs). Leftovers are 1-5c, the "already decided" kind we dropped before.
**Dropped.**

## Verdict

On these Kalshi data families the crowd already reads the source as fast as a free 5-minute bot could. What's left
is the already-decided 95-99c leftover. Not tested: thin count markets (Truth Social daily posts, settle via
Roll Call), Netflix daily in-app top 10 (FlixPatrol blocked), Hormuz (no free live ship data).
