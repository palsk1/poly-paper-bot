# Crypto "funding" payments: can a small bank collect them? (27 Nov 2026)

Script: `outside/funding.py` (probe `out_funding_scan`, `out_funding_fetch_12_40`, `out_funding_fetch2_12`,
`out_funding_fetch3`, then `report`; data in the price store, `bt_cache/out_funding/`). Paper research only.

## What this is, in plain words

Crypto exchanges sell "perpetual futures" (perps): a bet on a coin's price with no end date. To keep the bet's
price close to the real coin price, one side pays the other a small fee every hour or every 8 hours, the
**funding**. Most of the time the buyers pay the sellers. So the classic trick is:

- buy $150 of a coin, and at the same time sell (short) $150 of its perp;
- if the price goes up, one side wins what the other loses, so the price doesn't matter;
- you keep the funding the buyers pay you.

It is the trade Ethena (sUSDe) runs with billions. It is real, but it pays like a savings account, not a
jackpot.

Data used (all real, public, no key): Binance funding of all 919 perps (incl. 67 delisted) and hourly prices
of 98 coins for 12 months (Nov 2025 - Oct 2026, data.binance.vision); Hyperliquid funding of the 40 biggest
coins (hourly, 12 months) and hourly prices (May-Nov 2026, the API keeps only 5,000 hours); Kraken Futures
funding and hourly prices of 36 coins (12 months) plus Kraken spot daily prices; OKX (last 3 months only)
and dYdX (12 months) funding. Fees used: Binance spot 10c + perp 5c per $100 traded, Hyperliquid perp 4.5c,
Kraken perp 5c, Kraken spot 40c per $100, plus a small price-slip guess.

## 1. Simple carry on the big coins: real, but tiny

Funding a short collected, average per day per $100 shorted, 12 months:

| Coin | Binance | Hyperliquid | Kraken | dYdX |
|---|---|---|---|---|
| BTC | 0.9c | 1.6c | 1.0c | -0.4c |
| ETH | 0.7c | 1.7c | 1.0c | -0.2c |
| SOL | -0.1c | 0.2c | 0.1c | -1.1c |
| XRP | 0.0c | 0.9c | 0.2c | -0.9c |
| DOGE | 0.8c | 1.6c | 0.5c | 0.4c |

Funding flips a lot: BTC was negative (shorts pay) on 20 of 100 days on Binance, SOL and XRP on about 45 of 100.
From February to April 2026 it ran negative for weeks.

What $300 would have made (buy $150 spot, short $150, held the whole time, after fees):
- Binance BTC, 12 months: **+$4.46** (about 1c a day). ETH +$2.80, SOL -$1.25, XRP -$0.82.
- Short on Hyperliquid + spot elsewhere, 6 months: BTC **+$4.97**, ETH +$5.04 (about 3c a day). Hyperliquid pays
  more because its formula adds a fixed 1c per $100 every 8 hours to shorts when the market is calm.
- For comparison: $300 in a Swedish savings account at about 2 in 100 a year makes $6 a year (1.6c a day),
  with no exchange risk.

**Rule picked on the first half, checked on the second half** (one coin at a time with the whole $300, switch to
the coin whose last-days funding is highest; 240 versions tried on Nov 2025-May 2026): best first-half version
made $9.60; the same rule on the unseen May-Oct 2026 half made **+$3.44 in 181 days (2c a day), 3 trades**.
Plain "BTC always" made $0.84 then $3.08. Exam: "Too early to tell".

**Swedish tax makes it worse:** the winning leg is taxed 30 in 100, the losing leg only counts 70 in 100 of its loss.
BTC moved 30 in 100 over the year, so a $150/$150 pair leaves about **$4 extra tax** on a trade that earned
$4.46. The carry on BTC/ETH is about wiped out after Swedish tax. (Rough guess; holding the spot leg unsold
delays its part of the tax.)

## 2. Cross-site: short where funding is high, buy where it is low

Hyperliquid's funding was higher than Binance's on most days for almost every coin (e.g. BTC 139 of 179 days,
gap about 0.7c per $100 a day; this matches a 2026 SSRN paper that found about 7 in 100 a year). The two prices
stayed close (BTC typically 1 in 10,000 apart). But:
- **Static short Hyperliquid / buy Binance, 2x per leg, 25 coins:** +$0.59 then +$1.12 per coin per 3 months on
  $300 (about 1c a day). Price jumps on altcoins hit a leg 2-5 times in 25 at 2x, 11-19 times at 3x (each one costs
  money and a restart). Moving $1 USDC fees on every margin top-up eat a $300 version alive.
- **Best switching rule** (48 versions, picked on May-Aug, checked on Aug-Oct): +$6.25 in total over 18 trades
  across all 25 coins (a third of a cent a day per coin). Exam "Ahead, but could be luck".
- **Hyperliquid vs Kraken** (the Sweden-legal pair): checked half +$49.25 on 23 trades (May-Nov 2026), but one coin
  (MON) made $34 of it. Exam "Ahead, but could be luck".
- **Kraken vs Binance:** first half looked like +$666, the unseen half **lost $129** on 271 trades. Exam "Losing".
  Classic: wide, jumpy prices on thin Kraken alt perps look like profit in the half you picked from.

## 3. The one lead: Kraken spot + Kraken perp on "hot" altcoins

Kraken's own perps on thin altcoins often trade above the coin, so shorts collect a lot: over 12 months XPL paid
a short $141 on $300, GRASS $73, XMR $47 (BTC $6.40, ETH $7.48). This is the only version a Swede can do
legally on one licensed exchange.

Rule written after seeing that table (so **found by looking**): every 30 days, take the 3 coins with the highest
Kraken funding over the last 90 days, $100 each (buy the coin on Kraken spot, short the same on Kraken Futures),
pay both fees plus the real perp-vs-spot gap at each switch.
- Result: **+$46.76 on $300 over 9 months (Feb-Oct 2026), about 17c a day.** Every month ahead or flat
  ($0.69 to $15.16 a month). Coins it held: XPL, GRASS, XMR, STRK, MON, ZRO.
- Exam: 7 positions, "Too early to tell" (luck range +$1.45 to +$11.91 per $100, but far too few separate bets).
- Catches (some are guesses): it assumes the coin itself counts as margin for the short in one Kraken account; if
  you must keep $150 in dollars as margin instead, halve it (about 9c a day). Kraken charges a small hourly fee
  when the dollar part of the account goes negative. XMR is (I believe) not sold to EEA customers. These coins
  swing 50-70 in 100 a year, so the Swedish tax drag is about $5 per $100 a year. XPL fell from 29c to 8c and its
  Kraken perp printed a few crazy prices (once 8,000 in 10,000 off Binance spot), so a stop-out on a bad print is
  possible.

## 4. Can Jan use it from Sweden?

| Place | Usable? | Notes |
|---|---|---|
| Kraken (spot + Futures) | **Yes**, licensed (MiFID II, Cyprus) | KYC, a knowledge quiz and tax ID before futures; up to 10x. Fees: perp 5c per $100 (2c waiting order), spot 25-40c per $100 on Kraken Pro (up to 80c in the simple app; the test used 40c). Min order about 1 contract = $1 on most perps. SEPA euro deposit usually free (guess). |
| Hyperliquid | Works, no KYC, **no EU licence** | Terms ban only US, Ontario and sanctioned places; no EU regulator has named it (the UK FCA warns). You must bridge USDC (min $5 deposit, $1 per withdrawal). No investor protection. Legal grey zone for a Swede: my guess, not advice. |
| OKX EU | Partly | Licensed (Malta) but sells "X-Perps", 5-year futures with funding, up to 10x. USDT can't be traded in the EU (one-way switch to USDC). |
| Bybit EU | No futures | Spot only until its MiFID licence comes. |
| Binance | **No** | Withdrew its EU licence bid; new EU business stopped from 1 July 2026. |
| dYdX | Works, no KYC | Its funding was mostly negative for shorts this year: useless for this. |

**Tax (Sweden):** every sale or swap is a taxable event, reported on K4 section D, average-cost method, profit
taxed 30 in 100, losses count only 70 in 100. Crypto futures follow the same crypto rules (Skatteverket,
"terminer pa kryptotillgangar"). That gain/loss mismatch hurts hedged trades (see section 1).

## 5. Backward look: who got paid most, and what happened to them

- The 30 Binance perps that paid shorts the most (up to 24c per $100 a day: 1000WHY, BOB, DAM, BROCCOLI, HIPPO...)
  **all had no Binance spot coin**, so you can't hedge them there, and 9 of the 30 were delisted within the year.
  The big funding is the price of a market nobody can hedge.
- The coins where funding went the other way (shorts pay: HOME, LSK, 0G, LA, ONG...) cost a short up to $255 on
  $150 in a year. Collecting that needs borrowing the coin to sell it, which a small EU retail account can't do.
- 15 of 68 Binance coins with spot would have knocked out even a 1x short at least once in a year (the price about doubled
  within a day of the last rebalance, on small coins).
- The money-makers in this trade are funds like Ethena: cheap fees, billions in size, and they still earned only
  about 4-5 in 100 a year in 2026 (sUSDe), down from 17 in 2024. Funding pays well only in hot bull markets.

## Ceilings (rough guesses)

| Idea | Most in an average day at best size | Money needed | Stops growing at | Bad day |
|---|---|---|---|---|
| BTC/ETH carry (Kraken or Hyperliquid) | 1-3c a day at $300; about $1 a day at $10,000 | $300+ | millions (deep markets) | -$1 to -$3 at $300 (fees on a forced rebalance); exchange failure = lose it all |
| Cross-site Hyperliquid vs Kraken/Binance | about 1-2c a day per coin at $300 | $300 split over 2 sites | the $1 transfer fees dominate under ~$2,000 | -$5 to -$10 at $300 when an altcoin spike knocks out one leg |
| Kraken altcoin carry, rolling top 3 | about 17c a day at $300 (9c if margin must be dollars); maybe $2-5 a day at $5,000 | $300 | about $5,000-10,000 (these perps trade only $0.1-1 million a day) | -$5 to -$15 at $300 (premium collapses, bad price print, or perp delisted) |

## Verdict

- Simple carry on BTC/ETH: **dropped**. Real, but 1-3c a day on $300, below a savings account after Swedish tax.
- Cross-site funding spread: **dropped** for a $300 bank. The gap is real (Hyperliquid pays shorts more), but
  fees, $1 transfers and knocked-out legs eat it; the one positive checked half rests on one coin.
- Rotation rules on Binance: **dropped** (+$3.44 in 6 unseen months), and Binance is closed to Swedes anyway.
- **Kraken spot + perp on high-funding altcoins: interesting for later / worth a cheap paper track.** +$46.76 on
  $300 in 9 months, every month ahead, but found by looking, only 7 positions, and the margin setup is a guess.
  A paper track could run from GitHub Actions (Kraken's public API is reachable, no key): each month pick the 3
  coins, record Kraken's real funding and both prices. Needs about 6 more months before anyone should believe it.
