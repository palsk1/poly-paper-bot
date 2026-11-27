# Kalshi's "AI market share on OpenRouter" bets vs OpenRouter's own chart (27 Nov 2026)

Tool: `aim.py` (`orfind`, `orparams`, `orshare`, `orday`, `orlive`, `orcheck`). Data: `bt_cache/aim/or_*.json.gz` in the price store.

## In short

**Dropped, no track. The public number is live, and the price sits right on it.**

- **We found the number Kalshi really uses.** The 22 Nov dig (`backtest/aim_use.md`) used OpenRouter's free daily token file and got Google at 3-7 in 100 when Kalshi settled at 13-23. Kalshi's rule says "text market share", and the rankings page counts **requests, not tokens, for text models only**. That chart has a public data address (`/api/frontend/v1/public/stats/rankings/author-market-share?metric=requests&modality=text`, no key, readable from Actions), with 53 weeks of history. It gives Kalshi's result in 69 of 73 weeks; the other 4 are off by one strike right next to the value (small restatements before Kalshi's Monday 10 AM look).
- **The chart is live.** The newest week on it is the running week, updated through the day. There is no by-day history (22 settings tried), so we cannot replay "running share vs price" for past weeks.
- **Right now (Friday 27 Nov, 4.6 days into the week) the price hugs the running number.** Google runs at 14.29 in 100: "above 14.3" costs 53-72c, "above 15.0" 17-30c, "above 15.5" 1-2c. OpenAI runs at 18.15: "above 18.0" costs 37-40c, "above 18.8" 3-5c. Anthropic 5.78: "above 5.7" 11-15c, "above 5.6" 33-39c. The people trading these are watching the same chart, and they even price a slide over the weekend.
- **After the week ends (chart final, a few hours before Kalshi closes):** 9 winning sides still on sale, all at 98-99c, +$0.11 per $100. Nothing left.
- **The 22 Nov lead took a hit on its first unseen week.** "Yes at 15-85c on the first day of the week": the week ending 23 Nov (not in the 22 Nov data) went 17 bets, 1 won, -$157 at $10 a bet. All weeks now: 256 bets, +$31.54 per $100, luck range -$2.81 to +$65.89, exam "Ahead, but could be luck". The written re-check on the weeks ending 30 Nov-21 Dec stays as planned; it now has to make back a bad week.

## Ceiling (rough guess)

- Most it could make in an average day: about $0. There is no gap to buy.
- Money needed: $100-200 (about 20 bets a week at $10).
- Where it stops growing: 500-contract lots trade at these prices, so $25 a bet is fine.
- Bad day: -$150 (a whole ladder on one lab goes the wrong way, like 23 Nov).

## Release-date ladders

Already dug on 24 Nov (`backtest/dates.md`): 12 AI release ladders, too few. OpenRouter shows "stealth" test models before some launches (for example `stealth/crouton-alpha` in the chart), but there are too few release ladders to test that. Not dug further.

## What would be needed to test it properly

Only a recorder: save the live chart and Kalshi's share quotes every hour for several weeks (`python3 aim.py orlive` does one look and appends to `bt_cache/aim/or_live.json.gz`). That would show whether the weekend slide is priced right. Given how tight the prices are today, it is not worth a scheduled job without Jan asking for it.

## Traps

- Default settings of the chart endpoint give **token** share (Tencent 36.8, Google 3.1 for the week of 16 Nov); `metric=requests` alone still includes non-text traffic (Google 13.2); only `metric=requests&modality=text` matches the page (Google 16.1).
- Kalshi's event code is the settle Monday; the rule's "week of" date is the week before. OpenRouter weeks start Monday 00:00 UTC.
- `rankings/models` only holds the current day; the free daily export holds tokens of the top 50 models, not requests.
