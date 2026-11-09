# Economic data markets vs free forecasts (econ.py, 2026-11-09)

## The short version

- **Question:** Kalshi lists "will CPI / jobless claims / unemployment / payrolls / GDP be above X?" markets. Free
  professional forecasts exist (Cleveland Fed for inflation, Atlanta Fed GDPNow for GDP). Do they beat the price?
- **Data:** every strike of 340 finished Kalshi releases, 2021 to 2026-11-09 (3,600 markets, all volumes, so no
  volume hole), hourly bid/ask from Kalshi, Kalshi's taker fee. Forecasts as they stood the day before.
  Fed decisions are left out: there is no free history of futures-market odds.
- **Main answer: no.** The market guesses CPI better than the Cleveland Fed nowcast (score 0.09 vs 0.13; lower is
  better), and betting the forecast's view on every strike, costs included, comes out between -$4 and +$3 per $100
  (luck ranges straddle zero). The bookie test for sports said the same: the market already knows the public forecast.
- **Two small leads, both not proven:**
  1. **GDP (Atlanta Fed GDPNow):** the forecast beats the market's guess and betting it made +$22 to +$30 per $100,
     both halves ahead, a wrong-quarter forecast lost. But it is only 18-19 releases (4 a year), and the next one is
     in late January 2027, after the trial. Not turned into a track.
  2. **Core CPI:** +$15-17 per $100, but almost all of it came from two months in 2022. Dropped.
- **One rule that held up (found by looking, so the live test is what counts):** buy the **expensive side (80-99c)
  only when the forecast says it is worth at least 3c more**. 24 hours before: 141 bets on 91 releases, 7 lost,
  **+$6.73 per $100** (luck range +$3.39 to +$9.94); 72 hours before: +$7.75. Both halves ahead, still ahead at 2c
  worse prices, and the same price band **without** the forecast lost about $5 per $100. A wrong-month forecast
  gave about $0. It works across CPI, claims and unemployment, even with the dumb "same as last time" forecast for
  the jobs numbers: the market seems to underprice favorites that sit far from where the number "should" land.
  Paper track `econ_fav` ($50) tests it live from 2026-11-10.
- **Caveats:** hourly quotes don't show how many contracts sit at the ask, so real fills may be worse (the live track
  walks the real book). The 80-99c band was picked after seeing a table of four bands. Betting cheap long shots the
  forecast likes lost money (-$4 to -$19 per $100): the forecast's spread is a bit too wide for long shots.

## Drill-down (econ.py drill / drill2 / drill3)

- Blend test (70% market + 30% forecast vs market alone, both halves): helps for GDP (0.149 to 0.128 at 24h) and
  core CPI, hurts or ties for headline CPI, CPI year-on-year and the "exactly X" CPI markets.
- Calibration: the Cleveland forecast's 10-30 in 100 strikes came in 9-19 in 100, so its spread is a bit wide.
  Payrolls "same as last time" is the worst model, as expected.
- Price band without the forecast (24h): 80-100c any side -$5.06 per $100, 50-80c -$8.98, 0-20c -$37.70.
  With the forecast agreeing (3c+): 80-100c +$6.73, 50-80c +$2.78, 0-20c -$19.26.
- Favorite rule by series (24h): CPI -$1.19 (28 bets), core +$8.91 (8), CPI y/y +$8.73 (5), GDP +$12.67 (6),
  claims +$8.24 (53), unemployment +$13.58 (23), payrolls +$1.47 (17). Thresholds: 0c +$4.05, 5c +$9.14, 10c +$3.59.
- The 7 losses at 24h: CPI May/Oct/Nov 2022 (the wild inflation year), claims Feb and Apr 2026, payrolls Jun 2026 (2).

## Full run output (econ.py run)

Written by `python3 econ.py run` on 2026-11-09. Kalshi markets that closed before 2026-11-10 (the holdout date in PROTOCOL.md). Every strike of every event is used, whatever its volume, so the bt_cache volume hole doesn't apply here.

Forecasts: Cleveland Fed inflation nowcast (CPI, core CPI, CPI year-on-year), Atlanta Fed GDPNow (GDP), and plain 'same as last time' models from FRED's as-first-published numbers for jobless claims, unemployment and payrolls (these are the dumb control: we expect them to lose). The forecast is always the one published on an EARLIER day than the bet. Its spread comes from its own past misses, using only releases before the bet.

Bets: buy YES at the ask or NO at 1 minus the bid, from Kalshi's hourly quotes (at most 12 hours old), plus Kalshi's taker fee for a 20-contract order, held to the result. A bet is made when the forecast says the side is worth at least the threshold more than it costs. 'Coin-flip side' = same markets, same moment, random side: what costs alone do. 'Wrong month' = each release gets another release's forecast: a real edge must vanish there.

## Data checks

- KXCPI: 62 releases where our number reproduces every Kalshi result, 1 that don't (dropped), 1 without a number
- KXCPICORE: 50 releases where our number reproduces every Kalshi result, 1 that don't (dropped), 1 without a number
- KXCPIYOY: 46 releases where our number reproduces every Kalshi result, 0 that don't (dropped), 1 without a number
- KXECONSTATCPI: 10 releases where our number reproduces every Kalshi result, 0 that don't (dropped), 0 without a number
- KXGDP: 21 releases where our number reproduces every Kalshi result, 1 that don't (dropped), 0 without a number
- KXJOBLESSCLAIMS: 62 releases where our number reproduces every Kalshi result, 0 that don't (dropped), 1 without a number
- KXPAYROLLS: 42 releases where our number reproduces every Kalshi result, 0 that don't (dropped), 2 without a number
- KXU3: 57 releases where our number reproduces every Kalshi result, 5 that don't (dropped), 2 without a number

## Who guesses better? (lower is better, all quoted strikes)

| Series | Hours before | Strikes | Forecast score | Market score |
|---|---|---|---|---|
| KXCPI | 1 | 321 | 0.1313 | 0.0934 |
| KXCPI | 6 | 352 | 0.1225 | 0.0862 |
| KXCPI | 24 | 296 | 0.1305 | 0.0954 |
| KXCPI | 72 | 255 | 0.1264 | 0.0934 |
| KXCPICORE | 1 | 252 | 0.1152 | 0.1051 |
| KXCPICORE | 6 | 278 | 0.1076 | 0.0924 |
| KXCPICORE | 24 | 208 | 0.1116 | 0.1087 |
| KXCPICORE | 72 | 177 | 0.1160 | 0.1150 |
| KXCPIYOY | 1 | 304 | 0.0984 | 0.0729 |
| KXCPIYOY | 6 | 320 | 0.0973 | 0.0711 |
| KXCPIYOY | 24 | 256 | 0.0870 | 0.0612 |
| KXCPIYOY | 72 | 214 | 0.0915 | 0.0690 |
| KXECONSTATCPI | 1 | 85 | 0.0695 | 0.0458 |
| KXECONSTATCPI | 6 | 89 | 0.0730 | 0.0489 |
| KXECONSTATCPI | 24 | 92 | 0.0641 | 0.0431 |
| KXECONSTATCPI | 72 | 90 | 0.0730 | 0.0561 |
| KXGDP | 1 | 105 | 0.0966 | 0.1011 |
| KXGDP | 6 | 118 | 0.1028 | 0.1111 |
| KXGDP | 24 | 93 | 0.1155 | 0.1327 |
| KXGDP | 72 | 85 | 0.1297 | 0.1231 |
| KXJOBLESSCLAIMS | 1 | 510 | 0.1097 | 0.1002 |
| KXJOBLESSCLAIMS | 6 | 510 | 0.1098 | 0.1009 |
| KXJOBLESSCLAIMS | 24 | 500 | 0.1100 | 0.1072 |
| KXJOBLESSCLAIMS | 72 | 461 | 0.1060 | 0.1126 |
| KXU3 | 1 | 281 | 0.1174 | 0.1135 |
| KXU3 | 6 | 319 | 0.1141 | 0.1104 |
| KXU3 | 24 | 233 | 0.1144 | 0.1130 |
| KXU3 | 72 | 221 | 0.1064 | 0.1025 |
| KXPAYROLLS | 1 | 308 | 0.2090 | 0.1777 |
| KXPAYROLLS | 6 | 337 | 0.2172 | 0.1802 |
| KXPAYROLLS | 24 | 302 | 0.2249 | 0.1918 |
| KXPAYROLLS | 72 | 276 | 0.2275 | 0.1882 |

## Betting the forecast

### 1 hour before the release

- forecast beats price by 0c+: 1465 bets on 339 releases, won 565, staked $581.44, P&L -$16.44 = -$2.83 per $100 (luck range -$8.32 to +$2.91); coin-flip side on the same markets -$6.41 per $100
  - first half -$5.14 per $100 (607 bets), second half -$0.89 (858 bets); with 1c worse prices -$5.18 per $100
  - wrong-month forecast: 1766 bets on 343 releases, won 756, staked $819.78, P&L -$63.78 = -$7.78 per $100 (luck range -$12.91 to -$2.64); coin-flip side on the same markets -$7.69 per $100
- forecast beats price by 3c+: 1087 bets on 322 releases, won 359, staked $370.48, P&L -$11.48 = -$3.10 per $100 (luck range -$10.63 to +$5.18); coin-flip side on the same markets -$6.60 per $100
  - first half -$5.08 per $100 (447 bets), second half -$1.44 (640 bets); with 1c worse prices -$5.75 per $100
  - wrong-month forecast: 1508 bets on 340 releases, won 551, staked $611.09, P&L -$60.09 = -$9.83 per $100 (luck range -$16.67 to -$3.14); coin-flip side on the same markets -$7.68 per $100
- forecast beats price by 5c+: 939 bets on 311 releases, won 299, staked $308.55, P&L -$9.55 = -$3.10 per $100 (luck range -$11.98 to +$5.44); coin-flip side on the same markets -$6.62 per $100
  - first half -$5.85 per $100 (397 bets), second half -$0.64 (542 bets); with 1c worse prices -$5.93 per $100
  - wrong-month forecast: 1397 bets on 336 releases, won 481, staked $536.64, P&L -$55.64 = -$10.37 per $100 (luck range -$17.57 to -$3.22); coin-flip side on the same markets -$7.70 per $100
- forecast beats price by 10c+: 656 bets on 264 releases, won 196, staked $199.12, P&L -$3.12 = -$1.56 per $100 (luck range -$12.82 to +$9.09); coin-flip side on the same markets -$6.95 per $100
  - first half -$6.31 per $100 (280 bets), second half +$2.41 (376 bets); with 1c worse prices -$4.47 per $100
  - wrong-month forecast: 1197 bets on 323 releases, won 359, staked $410.26, P&L -$51.26 = -$12.50 per $100 (luck range -$21.52 to -$2.88); coin-flip side on the same markets -$7.90 per $100

### 6 hours before the release

- forecast beats price by 0c+: 1606 bets on 345 releases, won 628, staked $641.94, P&L -$13.94 = -$2.17 per $100 (luck range -$7.38 to +$2.90); coin-flip side on the same markets -$5.93 per $100
  - first half -$4.85 per $100 (686 bets), second half +$0.12 (920 bets); with 1c worse prices -$4.83 per $100
  - wrong-month forecast: 1923 bets on 347 releases, won 823, staked $877.17, P&L -$54.17 = -$6.18 per $100 (luck range -$11.33 to -$1.12); coin-flip side on the same markets -$7.24 per $100
- forecast beats price by 3c+: 1193 bets on 332 releases, won 391, staked $405.35, P&L -$14.35 = -$3.54 per $100 (luck range -$11.13 to +$3.51); coin-flip side on the same markets -$6.20 per $100
  - first half -$5.80 per $100 (499 bets), second half -$1.68 (694 bets); with 1c worse prices -$6.72 per $100
  - wrong-month forecast: 1646 bets on 345 releases, won 606, staked $660.93, P&L -$54.93 = -$8.31 per $100 (luck range -$15.59 to -$1.75); coin-flip side on the same markets -$7.34 per $100
- forecast beats price by 5c+: 1026 bets on 316 releases, won 326, staked $336.25, P&L -$10.25 = -$3.05 per $100 (luck range -$10.94 to +$5.80); coin-flip side on the same markets -$6.24 per $100
  - first half -$7.00 per $100 (442 bets), second half +$0.36 (584 bets); with 1c worse prices -$6.38 per $100
  - wrong-month forecast: 1511 bets on 341 releases, won 518, staked $568.15, P&L -$50.15 = -$8.83 per $100 (luck range -$16.07 to -$1.61); coin-flip side on the same markets -$7.30 per $100
- forecast beats price by 10c+: 715 bets on 277 releases, won 204, staked $212.99, P&L -$8.99 = -$4.22 per $100 (luck range -$15.38 to +$6.35); coin-flip side on the same markets -$6.49 per $100
  - first half -$8.58 per $100 (318 bets), second half -$0.54 (397 bets); with 1c worse prices -$5.64 per $100
  - wrong-month forecast: 1311 bets on 328 releases, won 400, staked $445.27, P&L -$45.27 = -$10.17 per $100 (luck range -$18.73 to -$1.63); coin-flip side on the same markets -$7.35 per $100

### 24 hours before the release

- forecast beats price by 0c+: 1389 bets on 320 releases, won 599, staked $597.93, P&L +$1.07 = +$0.18 per $100 (luck range -$5.44 to +$5.38); coin-flip side on the same markets -$5.90 per $100
  - first half +$0.66 per $100 (453 bets), second half -$0.09 (936 bets); with 1c worse prices -$1.53 per $100
  - wrong-month forecast: 1681 bets on 328 releases, won 778, staked $807.50, P&L -$29.50 = -$3.65 per $100 (luck range -$9.02 to +$1.70); coin-flip side on the same markets -$7.14 per $100
- forecast beats price by 3c+: 1051 bets on 305 releases, won 401, staked $402.79, P&L -$1.79 = -$0.45 per $100 (luck range -$7.51 to +$6.56); coin-flip side on the same markets -$5.69 per $100
  - first half +$0.28 per $100 (375 bets), second half -$0.92 (676 bets); with 1c worse prices -$4.15 per $100
  - wrong-month forecast: 1427 bets on 323 releases, won 579, staked $607.12, P&L -$28.12 = -$4.63 per $100 (luck range -$11.40 to +$2.33); coin-flip side on the same markets -$6.70 per $100
- forecast beats price by 5c+: 889 bets on 289 releases, won 317, staked $318.66, P&L -$1.66 = -$0.52 per $100 (luck range -$9.88 to +$8.13); coin-flip side on the same markets -$5.77 per $100
  - first half +$2.93 per $100 (330 bets), second half -$2.76 (559 bets); with 1c worse prices -$4.06 per $100
  - wrong-month forecast: 1320 bets on 316 releases, won 499, staked $527.41, P&L -$28.41 = -$5.39 per $100 (luck range -$13.34 to +$2.33); coin-flip side on the same markets -$6.69 per $100
- forecast beats price by 10c+: 622 bets on 247 releases, won 203, staked $203.47, P&L -$0.47 = -$0.23 per $100 (luck range -$10.88 to +$11.66); coin-flip side on the same markets -$5.90 per $100
  - first half +$2.37 per $100 (245 bets), second half -$1.99 (377 bets); with 1c worse prices -$2.63 per $100
  - wrong-month forecast: 1142 bets on 305 releases, won 390, staked $409.35, P&L -$19.35 = -$4.73 per $100 (luck range -$13.84 to +$3.90); coin-flip side on the same markets -$6.76 per $100

### 72 hours before the release

- forecast beats price by 0c+: 1299 bets on 305 releases, won 612, staked $611.41, P&L +$0.59 = +$0.10 per $100 (luck range -$4.63 to +$5.24); coin-flip side on the same markets -$6.17 per $100
  - first half -$3.01 per $100 (398 bets), second half +$1.70 (901 bets); with 1c worse prices -$1.80 per $100
  - wrong-month forecast: 1528 bets on 308 releases, won 713, staked $751.69, P&L -$38.69 = -$5.15 per $100 (luck range -$11.00 to +$0.59); coin-flip side on the same markets -$7.19 per $100
- forecast beats price by 3c+: 935 bets on 275 releases, won 402, staked $391.66, P&L +$10.34 = +$2.64 per $100 (luck range -$4.48 to +$10.21); coin-flip side on the same markets -$5.83 per $100
  - first half +$6.08 per $100 (323 bets), second half +$0.64 (612 bets); with 1c worse prices -$0.24 per $100
  - wrong-month forecast: 1313 bets on 302 releases, won 552, staked $581.65, P&L -$29.65 = -$5.10 per $100 (luck range -$12.50 to +$2.94); coin-flip side on the same markets -$6.60 per $100
- forecast beats price by 5c+: 794 bets on 260 releases, won 327, staked $322.48, P&L +$4.52 = +$1.40 per $100 (luck range -$6.76 to +$10.17); coin-flip side on the same markets -$5.93 per $100
  - first half +$7.37 per $100 (286 bets), second half -$2.14 (508 bets); with 1c worse prices -$0.60 per $100
  - wrong-month forecast: 1213 bets on 298 releases, won 482, staked $512.44, P&L -$30.44 = -$5.94 per $100 (luck range -$13.78 to +$2.14); coin-flip side on the same markets -$6.51 per $100
- forecast beats price by 10c+: 563 bets on 226 releases, won 209, staked $208.66, P&L +$0.34 = +$0.17 per $100 (luck range -$11.12 to +$12.70); coin-flip side on the same markets -$5.91 per $100
  - first half +$7.81 per $100 (214 bets), second half -$4.57 (349 bets); with 1c worse prices -$2.32 per $100
  - wrong-month forecast: 1039 bets on 288 releases, won 373, staked $394.03, P&L -$21.03 = -$5.34 per $100 (luck range -$15.45 to +$4.10); coin-flip side on the same markets -$6.53 per $100

## By series (24 hours before, 3c+ threshold)

- KXCPI: 182 bets on 58 releases, won 64, staked $69.25, P&L -$5.25 = -$7.58 per $100 (luck range -$21.80 to +$7.09); coin-flip side on the same markets -$5.52 per $100
  - first half -$8.91 per $100 (91 bets), second half -$4.53 (91 bets)
- KXCPICORE: 110 bets on 42 releases, won 40, staked $34.05, P&L +$5.95 = +$17.47 per $100 (luck range -$6.82 to +$37.06); coin-flip side on the same markets -$5.78 per $100
  - first half +$10.80 per $100 (59 bets), second half +$32.28 (51 bets)
- KXCPIYOY: 111 bets on 38 releases, won 23, staked $27.68, P&L -$4.68 = -$16.90 per $100 (luck range -$38.91 to +$5.89); coin-flip side on the same markets -$5.37 per $100
  - first half -$62.09 per $100 (40 bets), second half +$10.94 (71 bets)
- KXECONSTATCPI: 35 bets on 9 releases, won 9, staked $11.86, P&L -$2.86 = -$24.14 per $100 (luck range -$34.02 to -$14.74); coin-flip side on the same markets -$7.34 per $100
  - first half -$22.79 per $100 (16 bets), second half -$25.77 (19 bets)
- KXGDP: 56 bets on 18 releases, won 26, staked $20.05, P&L +$5.95 = +$29.64 per $100 (luck range +$0.56 to +$55.65); coin-flip side on the same markets -$5.10 per $100
  - first half +$59.64 per $100 (19 bets), second half +$6.34 (37 bets)
- KXJOBLESSCLAIMS: 238 bets on 58 releases, won 121, staked $116.24, P&L +$4.76 = +$4.09 per $100 (luck range -$8.08 to +$15.17); coin-flip side on the same markets -$6.79 per $100
  - first half +$10.44 per $100 (124 bets), second half -$6.06 (114 bets)
- KXU3: 99 bets on 45 releases, won 49, staked $48.98, P&L +$0.02 = +$0.04 per $100 (luck range -$17.03 to +$16.85); coin-flip side on the same markets -$5.50 per $100
  - first half -$8.99 per $100 (43 bets), second half +$7.39 (56 bets)
- KXPAYROLLS: 220 bets on 37 releases, won 69, staked $74.67, P&L -$5.67 = -$7.59 per $100 (luck range -$33.49 to +$21.35); coin-flip side on the same markets -$4.76 per $100
  - first half +$23.41 per $100 (58 bets), second half -$22.56 (162 bets)

## By series (1 hour before, 3c+ threshold)

- KXCPI: 189 bets on 61 releases, won 61, staked $65.84, P&L -$4.84 = -$7.35 per $100 (luck range -$22.45 to +$8.22); coin-flip side on the same markets -$5.87 per $100
  - first half -$10.04 per $100 (102 bets), second half -$0.81 (87 bets)
- KXCPICORE: 138 bets on 47 releases, won 42, staked $36.59, P&L +$5.41 = +$14.79 per $100 (luck range -$7.43 to +$35.91); coin-flip side on the same markets -$6.66 per $100
  - first half +$16.85 per $100 (77 bets), second half +$10.86 (61 bets)
- KXCPIYOY: 136 bets on 45 releases, won 33, staked $38.68, P&L -$5.68 = -$14.69 per $100 (luck range -$34.50 to +$4.23); coin-flip side on the same markets -$5.91 per $100
  - first half -$25.89 per $100 (66 bets), second half -$0.54 (70 bets)
- KXECONSTATCPI: 31 bets on 9 releases, won 7, staked $9.89, P&L -$2.89 = -$29.23 per $100 (luck range -$50.63 to -$7.16); coin-flip side on the same markets -$9.79 per $100
  - first half -$29.07 per $100 (16 bets), second half -$29.43 (15 bets)
- KXGDP: 62 bets on 19 releases, won 25, staked $20.40, P&L +$4.60 = +$22.55 per $100 (luck range -$4.39 to +$49.54); coin-flip side on the same markets -$6.60 per $100
  - first half +$9.15 per $100 (23 bets), second half +$38.22 (39 bets)
- KXJOBLESSCLAIMS: 205 bets on 55 releases, won 86, staked $86.37, P&L -$0.37 = -$0.43 per $100 (luck range -$13.79 to +$13.54); coin-flip side on the same markets -$8.55 per $100
  - first half +$14.35 per $100 (100 bets), second half -$19.79 (105 bets)
- KXU3: 103 bets on 47 releases, won 45, staked $47.22, P&L -$2.22 = -$4.70 per $100 (luck range -$22.42 to +$14.48); coin-flip side on the same markets -$6.52 per $100
  - first half -$19.45 per $100 (43 bets), second half +$6.02 (60 bets)
- KXPAYROLLS: 223 bets on 39 releases, won 60, staked $65.48, P&L -$5.48 = -$8.37 per $100 (luck range -$35.98 to +$18.93); coin-flip side on the same markets -$5.35 per $100
  - first half -$3.53 per $100 (62 bets), second half -$10.78 (161 bets)

## By price paid (24 hours before, 3c+ threshold)

- paid 0-20c: 398 bets on 205 releases, won 30, staked $37.16, P&L -$7.16 = -$19.26 per $100 (luck range -$43.51 to +$7.38); coin-flip side on the same markets -$4.20 per $100
- paid 20-50c: 288 bets on 196 releases, won 88, staked $95.12, P&L -$7.12 = -$7.48 per $100 (luck range -$24.01 to +$9.96); coin-flip side on the same markets -$6.65 per $100
- paid 50-80c: 224 bets on 170 releases, won 149, staked $144.97, P&L +$4.03 = +$2.78 per $100 (luck range -$6.96 to +$13.02); coin-flip side on the same markets -$7.22 per $100
- paid 80-100c: 141 bets on 91 releases, won 134, staked $125.55, P&L +$8.45 = +$6.73 per $100 (luck range +$3.39 to +$9.94); coin-flip side on the same markets -$5.08 per $100


