# All copied wallets re-checked, and a hunt for new ones (27 Nov 2026, Jan: "check all wallets we are observing and check for new ones ... make it our own instead of copying")

Tools: `walletpnl.py scan` (probe `wpnl_scan_30`): for every copied wallet and the top 30 new ones, Polymarket's own
leaderboard number (all-time, last 30 days), every position (what it bought, at what price, how long before the end, what it
made) and its newest 20,000 money moves (buys a day, both sides, merges). `optfair.py wallets` (probe `opt_wallets`): the one
repeat pattern as a plain rule on 14,077 finished Bitcoin / Ethereum markets at prices people really paid.

## Plain answer

- **The wallets are real winners, our copies are not.** 35 of the 41 wallets we copy are ahead all-time on Polymarket's own
  board, most by 00,000 to  million. Our 80 copy tracks together are behind (table below), because we buy 5 minutes
  later at worse prices, and because their profit sits in a few big calls.
- **Their profit is judgment, not a rule.** For 16 of the 38 the 5 biggest wins are bigger than the whole profit
  (TheReturnOfDarthMaul: one Fed bet, .6M of top-5 wins vs .6M total; Jsram .3M vs .2M; wan123 .2M vs /bin/bash.8M).
  Pooled over the 54 profitable wallets whose numbers add up: their 90c+ buys LOST (-$1.31 per $100 on $380M), their money
  came from 10-70c picks and cheap long shots that hit. That's the same finding as our own tests: favourites don't pay, and
  picking the right underdog is a call, not a pattern.
- **One repeat pattern:** three separate crypto wallets (Tokor, 0xf705..., justdance) made -3M each buying Yes on "will
  Bitcoin / Ethereum reach / dip to $X" with weeks left. As a plain rule on 14,077 past markets it is NOT there (table below):
  the wallets were right about where crypto went. The other side (No) is ahead, which is what `crypto_no` already does.
- **New wallets:** 676 wallets on the boards are ahead both all-time and in the last 30 days. The top 30 are mostly sports and
  esports traders with hundreds of buys a day on both sides (market makers or live-game speed bots, a race we can't win),
  election long-shot holders (one wallet: 536 bets under 10c on 14 elections, +$1.6M from Le Pen / Bolsonaro / Philippe),
  and crypto ladder traders like Tokor. None is a pattern a slow bot can copy. No new copy track suggested.

## The crypto wallets' pattern as a plain rule (optfair.py wallets)

First real trade where the price fits, bought at the next real trade + 1c + fee, one bet per market, $10 a bet.
Markets in one monthly ladder win and lose together, so the exam counts 21 separate bets.

| rule | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| Yes, 10-70c, 7+ days left | 269 | 88 | +$2.35 | -$12.23 | +$16.67 |
| Yes, 10-70c, 20+ days left | 210 | 62 | -$1.44 | -$3.77 | +$0.85 |
| Yes, 30-70c, 7+ days left | 206 | 87 | -$15.36 | -$18.81 | -$11.95 |
| Yes, under 10c, 1+ day left | 882 | 52 | -$10.82 | -$52.90 | +$31.08 |
| Yes, 10-70c, 1-7 days left | 572 | 151 | -$20.82 | -$28.22 | -$13.37 |
| dip only, Yes 10-70c, 7+ days | 138 | 45 | -$5.12 | +$32.54 | -$42.53 |
| reach only, Yes 10-70c, 7+ days | 131 | 43 | +$10.18 | +$5.34 | +$14.90 |
| the other side: No, 30-90c, 7+ days | 269 | 181 | +$9.11 | +$13.41 | +$4.88 |

Exam: Yes 10-70c 7+ days "Ahead, but could be luck" (luck range -$26.56 to +$31.26, gone at 1c more a share); the No side
"Ahead, but could be luck" (+$4.54 to +$13.68, both halves ahead, still +$4.76 at 2c more), only 21 separate ladders.
Month by month the Yes rule swings from +$163 to -$100 per $100: it's a bet on the month's direction.

## Every wallet we copy

"Board" = Polymarket's own leaderboard on 27 Nov. "Our copies" = w_ / wb_ paper tracks (P&L in dollars, finished bets).

| wallet | board all-time | last 30 days | volume | top-5 wins | main topic (their money) | buys a day | both sides | our copies w_ / wb_ |
|---|---|---|---|---|---|---|---|---|
| Tokor | +$1,249k | +$700k | $13M | +$874k | crypto +$1,228k, other +$84k | 193 | 77 in 100 $ | $-23.72 (155) / $-28.79 (165) |
| flawfence | +$1,007k | +$167k | $33M | +$916k | politics +$1,321k, other -$58k | 105 | 20 in 100 $ | $+1.30 (0) / $-1.25 (2) |
| TheReturnOfDarthMaul | +$1,584k | -$4k | $30M | +$2,634k | economics +$1,730k, geopolitics -$83k | 57 | 4 in 100 $ | $+5.42 (2) / $+5.45 (6) |
| UnderperformingForALiving | +$426k | +$606k | $50M | +$653k | politics +$27k, geopolitics -$57k | 6 | 36 in 100 $ | $-2.94 (40) / $-2.98 (39) |
| tunatyler | +$356k | +$141k | $16M | +$93k | politics +$196k, geopolitics +$63k | 42 | 20 in 100 $ | $+0.09 (8) / $-0.20 (8) |
| dromedaryy | +$788k | +$465k | $17M | +$1,098k | politics +$801k, geopolitics -$259k | 38 | 61 in 100 $ | $+2.52 (6) / $+6.59 (6) |
| debased | +$1,229k | +$341k | $515M | +$5,097k | politics +$852k, geopolitics +$300k | 97 | 92 in 100 $ | $-7.06 (21) / $-6.24 (25) |
| Jsram | +$2,202k | -$23k | $76M | +$4,266k | sports +$2,216k, other -$884k | 190 | 6 in 100 $ | $-1.76 (1) / $-2.13 (1) |
| 0x448861155279dbf833d041b963e3ac854599e319 | +$747k | -$17k | $90M | +$603k | politics +$942k, other -$133k | 181 | 14 in 100 $ | $-10.30 (38) / $-8.70 (38) |
| cigarettes | -$95k | +$1,302k | $625M | +$6,977k | politics +$19,394k, economics +$4,285k | 4306 | 55 in 100 $ | $-34.96 (130) / $-38.96 (140) |
| RememberAmalek | +$1,097k | +$211k | $43M | +$892k | politics +$605k, geopolitics +$332k | 70 | 20 in 100 $ | $-4.48 (13) / $-3.57 (25) |
| lava-lava | +$1,351k | +$114k | $44M | +$548k | politics +$929k, other +$241k | 75 | 85 in 100 $ | $-1.63 (3) / $-2.36 (3) |
| Dropper | +$1,610k | +$145k | $56M | +$486k | politics +$432k, other +$413k | 38 | 57 in 100 $ | $-10.67 (11) / $-7.18 (13) |
| wan123 | +$760k | -$324k | $64M | +$2,228k | geopolitics +$1,546k, sports -$630k | 79 | 36 in 100 $ | $-2.88 (5) / $+0.40 (8) |
| anoin123 | -$4,910k | -$201k | $136M | +$1,030k | geopolitics -$5,067k, other +$78k | 407 | 51 in 100 $ | $-15.56 (29) / $-9.16 (29) |
| Hauchn | +$304k | +$245k | $10M | +$428k | other +$491k, sports -$0k | 34 | 66 in 100 $ | $-2.63 (2) / $+0.38 (9) |
| betwick | +$625k | +$203k | $45M | +$576k | geopolitics +$38k, other +$235k | 30 | 17 in 100 $ | $-14.79 (9) / $-13.08 (14) |
| aghy | +$195k | +$15k | $3M | +$293k | economics +$220k, other -$20k | 11 | 0 in 100 $ | $-3.52 (1) / $+3.26 (1) |
| eCash | +$295k | +$36k | $11M | +$229k | politics +$115k, geopolitics +$157k | 25 | 16 in 100 $ | $-20.12 (10) / $-21.90 (17) |
| pako | +$369k | -$39k | $22M | +$465k | economics +$569k, geopolitics -$177k | 13 | 16 in 100 $ | $+2.04 (8) / $-1.39 (11) |
| Bertapotamous | +$209k | +$39k | $32M | +$674k | geopolitics +$570k, politics -$226k | 36 | 27 in 100 $ | $+0.08 (6) / $+3.03 (11) |
| hell0pia | +$111k | +$21k | $3M | +$170k | geopolitics +$59k, other +$128k | 5 | 1 in 100 $ | $-0.52 (5) / $+4.37 (11) |
| eightpenguins | +$311k | -$0k | $9M | +$222k | geopolitics +$96k, other +$61k | 21 | 18 in 100 $ | $-0.80 (9) / $-4.23 (11) |
| New.Jeans | +$152k | +$34k | $13M | +$172k | other -$34k, politics +$34k | 21 | 50 in 100 $ | $+0.66 (0) / $+3.60 (2) |
| Vilgefortz | +$367k | -$1k | $20M | +$238k | economics +$344k, politics +$15k | 12 | 5 in 100 $ | $-4.70 (1) / $-4.67 (4) |
| Albert 1953 | +$288k | +$53k | $11M | +$101k | other +$221k, politics +$12k | 18 | 42 in 100 $ | $+5.07 (4) / $+12.67 (7) |
| YoungAlphaGoat | +$106k | +$13k | $6M | +$26k | other +$78k, politics +$17k | 50 | 56 in 100 $ | $+0.00 (0) / $-27.89 (13) |
| The-Joker | +$144k | +$15k | $12M | +$65k | other +$164k, geopolitics +$2k | 32 | 24 in 100 $ | $+1.58 (13) / $-5.82 (17) |
| balerinacapuchina | +$62k | +$30k | $2M | +$71k | politics +$84k, other +$29k | 3 | 13 in 100 $ | $+1.23 (4) / $+1.73 (5) |
| sbel | -$1k | +$9k | $0M | +$3k | other -$1k, politics -$0k | 20 | 0 in 100 $ | $-55.94 (110) / $-64.38 (116) |
| HellYeahTrader | +$4k | +$6k | $0M | +$2k | other +$4k | 126 | 0 in 100 $ | $-53.44 (69) / $-64.01 (88) |
| -Dominus- | +$43k | +$9k | $1M | +$14k | politics +$4k, other +$8k | 12 | 17 in 100 $ | $+7.23 (15) / $+5.55 (19) |
| BlondBeast | +$45k | +$3k | $1M | +$21k | mentions +$32k, geopolitics +$4k | 14 | 17 in 100 $ | $+0.24 (12) / $+1.16 (19) |
| groth | +$154k | +$14k | $3M | +$66k | geopolitics +$115k, other +$41k | 21 | 16 in 100 $ | $-16.14 (16) / $-19.16 (27) |
| JJo | +$312k | +$51k | $50M | +$137k | politics +$118k, geopolitics +$72k | 31 | 18 in 100 $ | $-8.44 (25) / $-8.74 (29) |
| rabbitfoot1 | +$7k | -$227k | $39M | +$1,433k | sports +$61k, other -$281k | 72 | 34 in 100 $ | $-13.85 (27) / $-15.84 (28) |
| Bigggggggg | +$534k | +$2,930k | $49M | +$617k | politics +$1,607k, other +$831k | 270 | 0 in 100 $ | $-21.24 (112) / $-28.00 (121) |
| glpgb | +$95k | +$1,097k | $5M | +$87k | politics +$396k, other +$27k | 255 | 49 in 100 $ | $-12.42 (50) / $-15.27 (54) |
| Railcool | +$520k | +$437k | $5M | +$271k | other -$18k, politics +$557k | 32 | 11 in 100 $ | $+0.00 (0) / $+0.00 (0) |
| Monopoly_Money | +$19k | +$105k | $6M | +$253k | politics -$2k, geopolitics -$17k | 4 | 5 in 100 $ | $-15.40 (5) / $-6.55 (10) |
| sabsabinxz | +$91k | +$20k | $1M | +$60k | geopolitics +$97k, other +$5k | 3 | 6 in 100 $ | $+0.00 (0) / $+0.00 (0) |

All 80 copy tracks together: $-696.67 in paper P&L so far.

## Top 30 new wallets (ahead all-time and in the last 30 days, biggest all-time first)

| wallet | board all-time | last 30 days | volume | top-5 wins | main topic | buys a day | both sides |
|---|---|---|---|---|---|---|---|
| 0x006cc834 | +$4,711k | +$0k | $64M | +$3,108k | sports +$1,836k, other +$2,392k | 6 | 18 in 100 $ |
| 0x5966db1f | +$3,953k | +$484k | $31M | +$2,358k | sports +$2,344k, other +$682k | 49 | 0 in 100 $ |
| primm | +$3,536k | +$281k | $68M | +$1,239k | sports +$3,306k, other +$290k | 325 | 38 in 100 $ |
| keeptheblueflagflyinghig | +$3,179k | +$3,241k | $137M | +$2,497k | sports +$18,919k, other +$4,997k | 5124 | 88 in 100 $ |
| 0xf705fa04 | +$2,879k | +$376k | $112M | +$522k | crypto +$2,865k, other +$48k | 105 | 52 in 100 $ |
| gmpm2 | +$2,825k | +$1,002k | $132M | +$5,270k | other +$754k, sports +$2,560k | 134 | 50 in 100 $ |
| denizz | +$2,355k | +$203k | $101M | +$2,043k | geopolitics +$2,240k, other +$70k | 61 | 56 in 100 $ |
| THEHIGHLIFE | +$2,300k | +$177k | $94M | +$400k | esports +$2,161k, sports +$132k | 428 | 21 in 100 $ |
| The Spirit of Ukraine>UM | +$2,001k | +$398k | $148M | +$925k | politics +$1,072k, geopolitics +$726k | 71 | 8 in 100 $ |
| justdance | +$1,958k | +$36k | $132M | +$384k | crypto +$12,743k, politics +$315k | 219 | 84 in 100 $ |
| gopfan2 | +$1,708k | +$16k | $71M | +$672k | politics +$902k, other +$586k | 65 | 8 in 100 $ |
| scottilicious | +$1,672k | +$98k | $74M | +$245k | politics +$561k, geopolitics +$520k | 22 | 9 in 100 $ |
| Kickstand7 | +$1,594k | +$23k | $70M | +$688k | politics +$599k, economics +$263k | 20 | 51 in 100 $ |
| Car | +$1,591k | +$296k | $196M | +$213k | geopolitics +$1,688k, politics +$387k | 151 | 62 in 100 $ |
| 0x6e82b93e | +$1,569k | +$25k | $36M | +$624k | sports +$1,190k, politics +$343k | 18 | 22 in 100 $ |
| Crevanor | +$1,498k | +$204k | $61M | +$273k | sports +$10,009k, other +$598k | 577 | 71 in 100 $ |
| sportmaster777 | +$1,420k | +$33k | $38M | +$240k | sports +$3,625k, other +$145k | 102 | 30 in 100 $ |
| curie | +$1,411k | +$0k | $106M | +$411k | sports +$7,448k, other +$1,578k | 655 | 80 in 100 $ |
| 0xa3a417e4 | +$1,369k | +$52k | $51M | +$1,370k | politics +$1,534k, geopolitics +$71k | 0 | 0 in 100 $ |
| fantasy7788 | +$1,138k | +$1,215k | $36M | +$1,560k | esports +$480k, sports +$560k | 8 | 6 in 100 $ |
| balthazar | +$1,204k | +$2,903k | $91M | +$337k | other +$5,295k, geopolitics +$1,463k | 1634 | 12 in 100 $ |
| monkeymashingkeyboard | +$1,185k | +$997k | $47M | +$670k | sports +$1,222k, other -$21k | 638 | 6 in 100 $ |
| Mooseborzoiii | +$1,170k | +$609k | $37M | +$4,114k | esports +$1,192k, sports -$22k | 2137 | 5 in 100 $ |
| 0xdbdd4515 | +$1,089k | +$120k | $63M | +$65k | sports +$3,491k, other +$1,990k | 704 | 25 in 100 $ |
| Woaifacai | +$1,052k | +$409k | $46M | +$1,364k | other +$478k, sports +$377k | 53 | 25 in 100 $ |
| tradecraft | +$1,037k | +$124k | $81M | +$276k | other +$10,636k, sports +$305k | 931 | 70 in 100 $ |
| SlavaUkraini | +$1,013k | +$262k | $37M | +$634k | politics +$859k, other +$138k | 7 | 6 in 100 $ |
| mr.ozi | +$1,007k | +$58k | $46M | +$456k | geopolitics +$400k, politics +$533k | 46 | 28 in 100 $ |
| ScottyNooo | +$1,001k | +$78k | $148M | +$1,598k | geopolitics +$242k, other +$45k | 96 | 88 in 100 $ |
| juice-fruit | +$959k | +$249k | $24M | +$1,451k | sports +$1,214k, other -$153k | 9 | 0 in 100 $ |

Notes: topic money comes from the positions list, which is off for the busiest wallets (cigarettes, debased, bigggggggg,
keeptheblueflagflyinghigh and other 1,000+ buys-a-day wallets show far more than the board); trust the board number.
"Both sides" = share of buy dollars in markets where it bought Yes and No (market makers sit at 50-90 in 100).
Pooled over the 54 profitable wallets whose position numbers match the board: bought at 90c+ -$1.31 per $100 ($380M),
70-90c +$5.66, 30-70c +$7.61, 10-30c +$16.90, under 10c +$166 (tiny money, and these are the wallets whose long shots hit:
the board shows survivors).
