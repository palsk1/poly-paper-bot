#!/usr/bin/env python3
"""Real-money sizes: do the leads still pay at $25, $50 and $100 a bet? (2026-11-10, Jan said "Do it")

PAPER ONLY, research only. Never trades, never changes a track.

The paper tracks buy 5 shares (about $1-5). Jan plans $300-500 in one strategy, so a real bet is $25-100. A bigger
order eats deeper into the order book: a worse average price, and in thin markets not everything is on sale.
This tool asks, for each lead still alive: how much profit per $100 is left after paying that extra price, how many
chances there are per week, and whether $300-500 could actually be put to work.

    python3 bigbets.py hist      # offline, needs bt_cache/inf_tapes.json.gz (price store): boring_no + crypto_no
                                 # replayed on the real trade lists, buying $25/$50/$100 at what the next buyers paid
    python3 bigbets.py live      # live: every market the soccer_draw / boring_no / crypto_no / mention_no rules
                                 # match right now, its real order book walked at 5 shares and $25/$50/$100,
                                 # plus how much of that answer people bought in the last 24 hours
    python3 bigbets.py kalshi    # live: every finished kc_maker* order in state/tracks.json, its real Kalshi trade
                                 # tape re-read, and how many contracts a $10/$25/$50/$100 bid would really have got
    python3 bigbets.py all       # live + kalshi (+ hist when the trade lists are there); writes backtest/bigbets.md
  From GitHub: probe workflow with what = big_all (or big_live, big_kalshi, big_hist).

How the fills are modelled
- live books: the same limit the bot uses (never more than the listed price + the track's max_over_listed, never
  above the band's top + 1c). What doesn't fit under the limit is NOT bought: a real order would just sit there.
- hist: we can't see old order books, only the trades. A $25/$50/$100 bet takes, in time order, the next real $100+
  buys of that answer (5 min to 6 h after the signal, never above the band's top + 2c), each at its own price + 1c and
  the fee. What the next buyers paid is roughly what was on sale. Trades under $100 aren't in the lists, so
  the amount on sale is a low guess.
- Kalshi: a resting bid at price P gets every contract sold to it at P (after the queue that was there first) plus
  every contract sold below P. The bot's own real-size record counts a bid as FULLY filled whenever the price
  traded below it; for big bids that's too kind, because the bets where the price crashes through are the losers.
  Here the fill is capped by the real volume sold at P or lower.
"""
import collections
import datetime as dt
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

SIZES = (25, 50, 100)
DAY = 86400
OUT = os.path.join(bot.ROOT, "backtest")
LINES = []

# what the backtests found at their own small size (per $100 bet), for "profit left" below
BACKTEST_EDGE = {"soccer_draw": 5.60, "boring_no": 5.45, "crypto_no": 6.95, "mention_no": 4.35, "kc_maker_safe": 0.56}


def P(s=""):
    print(s)
    LINES.append(s)


def usd(x):
    return ("+" if x >= 0 else "-") + f"${abs(x):,.2f}"


# ---------------------------------------------------------------- hist: trade lists (boring_no, crypto_no)

HIST_RULES = (("crypto_no", "crypto price", 1, 0.70, 0.90, 3 * DAY, 7 * DAY),
              ("boring_no", "other", 1, 0.90, 0.97, 30 * DAY, 9e9))


def hist_bets(tapes, topic_fn, topic, o, lo, hi, l0, l1, sizes=(5,) + SIZES, late=300, wait=6 * 3600, over=0.02):
    """Same signal as winners.rule_bets (first time the price is in the band with the right time left, 5 min later),
    then each stake walks the next real $100+ buys of that answer in time order at their price + 1c."""
    out = []
    for mid, x in tapes["m"].items():
        if x.get("cut") or topic_fn(x.get("q") or "") != topic or not x.get("end"):
            continue
        try:
            f0 = float(x["final"][0])
        except (TypeError, ValueError, IndexError):
            continue
        sig = None
        for t, p0 in x["path"]:
            p = p0 if o == 0 else 1 - p0
            if lo <= p < hi and l0 <= x["end"] - t < l1:
                sig = t + 300
                break
        if sig is None:
            continue
        buys = [(t, px, sh) for t, w, oi, sd, px, sh, cp, v24 in x["tr"]
                if sd == "B" and oi == o and sig + late <= t <= sig + late + wait and t < x["end"]]
        if not buys or buys[0][1] + 0.01 > hi + over or buys[0][1] < lo - 0.02 or buys[0][1] + 0.01 >= 0.995:
            continue  # same skips as winners.rule_bets: no buy, too dear, or already out of the band
        fin = f0 if o == 0 else 1 - f0
        rate = x.get("fee") or 0.0
        row = {"ev": x.get("ev") or mid, "t": buys[0][0], "q": x.get("q") or "", "won": fin > 0.5, "fin": fin,
               "first_usd": buys[0][1] * buys[0][2], "on_sale": sum(px * sh for t, px, sh in buys if px + 0.01 <= hi + over), "s": {}}
        for S in sizes:
            left, sh_tot, cost = float(S), 0.0, 0.0
            for t, px, sh in buys:
                c = px + 0.01
                if c > hi + over or c >= 0.995:
                    continue
                take = min(sh, left / c)
                sh_tot += take
                cost += take * c + rate * take * c * (1 - c)
                left -= take * c
                if left <= 1e-6:
                    break
            row["s"][S] = (sh_tot, cost, sh_tot * fin)
        out.append(row)
    return out


def hist(tapes=None, topic_fn=None):
    if tapes is None:
        import backtest as bt
        import calib
        import informed
        tapes, topic_fn = bt.rjson(informed.TAPES, {}) or {}, calib.topic
    if not tapes.get("m"):
        P("No trade lists here (bt_cache/inf_tapes.json.gz). Run `python3 store.py pull` first.")
        return {}
    res = {}
    P("## Old trades: boring_no and crypto_no at bigger sizes\n")
    P("Same bets as the backtest (backtest/winners.md), but each one spends $25, $50 or $100 at what the next real "
      "buyers paid, in order, never above the band's top + 2c. Only buys of $100 or more are in our lists, so the "
      "'on sale' numbers are a low guess. Note: the first buy in our lists is always $100+, so a single $100 bet "
      "fits by design here. The useful number is how much MORE was bought soon after: that says if several "
      "$100 bets, or a second bot like ours, would still get the same price.\n")
    for name, topic, o, lo, hi, l0, l1 in HIST_RULES:
        rows = hist_bets(tapes, topic_fn, topic, o, lo, hi, l0, l1)
        if not rows:
            continue
        ts = [r["t"] for r in rows]
        weeks = max((max(ts) - min(ts)) / DAY / 7, 1)
        P(f"### {name}: {len(rows)} bets over {weeks:.0f} weeks (about {len(rows) / weeks:.1f} a week in our sample)\n")
        P("| Stake | Bets where it all fit | Average price paid | Profit per $100 | Money that fit |")
        P("|---|---|---|---|---|")
        out = {}
        for S in (5,) + SIZES:
            full = sum(1 for r in rows if r["s"][S][1] >= S * 0.97)
            sh = sum(r["s"][S][0] for r in rows)
            cost = sum(r["s"][S][1] for r in rows)
            pay = sum(r["s"][S][2] for r in rows)
            per100 = 100 * (pay - cost) / cost if cost else 0
            label = "$5 (paper size)" if S == 5 else f"${S}"
            P(f"| {label} | {full} of {len(rows)} | {100 * cost / sh:.1f}c | {usd(per100)} | ${cost:,.0f} of ${S * len(rows):,} |")
            out[S] = {"full": full, "n": len(rows), "per100": round(per100, 2), "avg_c": round(100 * cost / sh, 2),
                      "spent": round(cost, 2)}
        sale = sorted(r["on_sale"] for r in rows)
        first = sorted(r["first_usd"] for r in rows)
        P(f"\nThe first real buy after a signal was a typical ${statistics.median(first):,.0f}. In the 6 hours after a signal, people bought a typical ${statistics.median(sale):,.0f} of that answer "
          f"inside the band (in $100+ buys). A quarter of the bets saw under ${sale[len(sale) // 4]:,.0f}.\n")
        res[name] = {"rows": len(rows), "per_week": round(len(rows) / weeks, 2), "sizes": out,
                     "on_sale_median": round(statistics.median(sale), 2)}
    return res


# ---------------------------------------------------------------- live: today's books

LIVE_TRACKS = (("soccer_draw", "draws"), ("boring_no", "kind"), ("crypto_no", "kind"), ("mention_no", "mentions"))


def flow_24h(m, outcome_index):
    """$ of this answer bought on Polymarket in the last 24 hours (data-api trades, up to 500 newest)."""
    cid = m.get("conditionId")
    if not cid:
        return None
    try:
        rows = bot.envelope_rows(bot.http_json(f"{bot.DATA}/v2/trades", {"condition_id": cid, "limit": 500}),
                                 "data", "trades")
    except Exception as e:
        print(f"trades failed for {cid[:10]}: {e}")
        return None
    t0 = time.time() - DAY
    tok = bot.market_tokens(m)[outcome_index]
    tot = 0.0
    for r in rows:
        ts = bot.fnum(r.get("timestamp"), 0)
        if ts > 1e12:
            ts /= 1000
        if ts < t0:
            continue
        if str(r.get("asset")) == str(tok) and str(r.get("side")).upper() == "BUY":
            tot += bot.fnum(r.get("price"), 0) * bot.fnum(r.get("size"), 0)
    return tot


def live():
    fns = {"draws": bot.draw_candidates, "kind": bot.mention_candidates, "mentions": bot.mention_candidates}
    res = {}
    P("## Today's order books\n")
    P("Every market each track's rules match right now (not only the ones it bought), its real book walked at the "
      "paper size and at $25, $50 and $100, with the bot's own price limit. 'Extra' = how much more a share costs than "
      "at the paper size. 'Bought 24h' = how much of that answer people bought in the last day.\n")
    for name, src in LIVE_TRACKS:
        if name not in bot.CFG["tracks"]:
            continue
        r = bot.rules_for(name)
        try:
            cands = fns[src]([name]).get(name, [])
        except Exception as e:
            P(f"{name}: scan failed ({e})\n")
            continue
        seen, uniq = set(), []
        for c in cands:   # one per event, like the track
            if c["event_key"] in seen:
                continue
            seen.add(c["event_key"])
            uniq.append(c)
        uniq = uniq[:int(os.environ.get("BIG_MAX", "60"))]
        with ThreadPoolExecutor(8) as ex:
            books = list(ex.map(lambda c: bot.book(c["token"]), uniq))
        with ThreadPoolExecutor(6) as ex:
            flows = list(ex.map(lambda c: flow_24h(c["market"], bot.market_tokens(c["market"]).index(c["token"])), uniq))
        rows = []
        for c, bk, fl in zip(uniq, books, flows):
            if not bk or not bk["asks"]:
                continue
            limit = r.get("max_price", 1.0) + 0.01
            if r.get("max_over_listed") is not None:
                limit = min(limit, c["price"] + r["max_over_listed"])
            p5 = bot.walk(bk["asks"], bot.CFG["shares_per_trade"])
            if p5 is None or p5 > limit + 1e-9 or p5 < r.get("min_price", 0):
                continue   # the track itself would skip it at paper size
            rate = c["fee_rate"]
            row = {"title": c["title"][:70], "p5": p5, "flow": fl, "under_limit": sum(p * s for p, s in bk["asks"] if p <= limit + 1e-9),
                   "s": {}}
            for S in SIZES:
                sh, cost = bot.fill_usd(bk["asks"], S, limit)
                fee = bot.taker_fee(sh, cost / sh, rate) if sh > 1e-9 else 0.0
                row["s"][S] = (sh, cost, fee)
            row["fee5"] = rate * p5 * (1 - p5)
            rows.append(row)
        if not rows:
            P(f"### {name}: 0 markets it could buy right now\n")
            res[name] = {"n": 0}
            continue
        edge = BACKTEST_EDGE.get(name, 0)
        P(f"### {name}: {len(rows)} markets it could buy right now (backtest: {usd(edge)} per $100 at paper size)\n")
        P("| Stake | Markets where it all fits | Extra per share | Profit per $100 left | Money that fits, all markets |")
        P("|---|---|---|---|---|")
        out = {}
        for S in SIZES:
            fit = [x for x in rows if x["s"][S][1] >= S * 0.97]
            got = [x for x in rows if x["s"][S][0] > 1e-9]
            extra = [x["s"][S][1] / x["s"][S][0] - x["p5"] for x in got]
            # profit left per $100: backtest edge minus the extra price (and extra fee) as a share of the price paid
            lost = [100 * ((x["s"][S][1] + x["s"][S][2]) / x["s"][S][0] - x["p5"] - x["fee5"]) / x["p5"] for x in got]
            avg_extra = statistics.mean(extra) if extra else 0
            left = edge - (statistics.mean(lost) if lost else 0)
            total = sum(min(x["s"][S][1], S) for x in rows)
            P(f"| ${S} | {len(fit)} of {len(rows)} | {100 * avg_extra:+.2f}c | {usd(left)} | ${total:,.0f} |")
            out[S] = {"fit": len(fit), "n": len(rows), "extra_c": round(100 * avg_extra, 3), "left": round(left, 2),
                      "money": round(total, 2)}
        fl = sorted(x["flow"] for x in rows if x["flow"] is not None)
        ul = sorted(x["under_limit"] for x in rows)
        if fl:
            P(f"\nPeople bought a typical ${statistics.median(fl):,.0f} of these answers in the last 24 hours "
              f"(a quarter under ${fl[len(fl) // 4]:,.0f}). On sale under the bot's limit right now: typical "
              f"${statistics.median(ul):,.0f}, all markets together ${sum(ul):,.0f}.")
        thin = sorted(rows, key=lambda x: x["s"][100][1])[:4]
        P("Thinnest: " + " | ".join(f"{x['title'][:50]} (${x['s'][100][1]:.0f} of $100 fits)" for x in thin) + "\n")
        res[name] = {"n": len(rows), "sizes": out, "flow_median": round(statistics.median(fl), 2) if fl else None,
                     "on_sale_total": round(sum(ul), 2), "on_sale_median": round(statistics.median(ul), 2)}
    return res


# ---------------------------------------------------------------- kalshi: resting bids, real tapes

def kalshi_fill(o, trades, want):
    """Contracts a bid of `want` at o['price'] would get: sold at our price after the queue, plus everything sold
    below our price (the queue at our price was used up first, so those sales would have hit us)."""
    t0 = bot.parse_iso(o["placed"])
    at, below = 0.0, 0.0
    for t in trades:
        ts = bot.parse_iso(t.get("created_time"))
        if ts is None or ts <= t0:
            continue
        yp = bot.fnum(t.get("yes_price_dollars"), None)
        if yp is None:
            yp = bot.fnum(t.get("yes_price"), 0) / 100
        px = yp if o["side"] == "yes" else round(1 - yp, 6)
        if str(t.get("taker_side")) == o["side"]:
            continue   # a taker buying our side doesn't fill a bid on our side
        n = bot.fnum(t.get("count_fp") or t.get("count"), 0)
        if abs(px - o["price"]) < 1e-6:
            at += n
        elif px < o["price"]:
            below += n
    return min(float(want), max(0.0, at - o.get("queue", 0)) + below)


def kalshi(names=("kc_maker_safe", "kc_maker", "kc_maker_early")):
    tracks = bot.load_tracks()
    res = {}
    P("## Kalshi 15-minute crypto: bigger resting bids, on the real trade tapes\n")
    P("Every finished order of the live paper tracks, its real trade tape read again. A bigger bid only gets what "
      "people really sold at our price (after the queue) or below. The bot's own size record counts a bid as fully "
      "filled whenever the price fell below it, which is too kind for big bids: those are the bets that lose.\n")
    tapes = {}
    for n in names:
        tr = tracks.get(n) or {}
        orders = [c for c in tr.get("closed") or [] if c.get("reason") == "resolved" and c.get("ticker")]
        if not orders:
            continue
        need = [o for o in orders if o["ticker"] not in tapes]

        def get(o):
            try:
                t0 = bot.parse_iso(o["placed"]).timestamp()
                t1 = bot.parse_iso(o["close"]).timestamp()
                return o["ticker"], bot.kalshi_trades(o["ticker"], t0, t1)
            except Exception as e:
                print(f"tape failed for {o['ticker']}: {e}")
                return o["ticker"], None
        with ThreadPoolExecutor(4) as ex:
            for tk, got in ex.map(get, need):
                tapes[tk] = got
        rows = []
        for o in orders:
            got = tapes.get(o["ticker"])
            if not got:
                continue
            trades, complete = got
            pay = o["exit"]
            r = {"won": pay >= 0.5, "price": o["price"], "s": {}}
            for S in (10,) + SIZES:
                want = S / o["price"]
                f = kalshi_fill(o, trades, want)
                r["s"][S] = (f, f * o["price"], f * pay - f * o["price"])
            rows.append(r)
        if not rows:
            continue
        days = max((bot.parse_iso(orders[-1]["close"]) - bot.parse_iso(orders[0]["placed"])).total_seconds() / DAY, 0.1)
        P(f"### {n}: {len(rows)} filled orders over {days:.1f} days (about {len(rows) / days:.0f} a day), "
          f"{sum(1 for r in rows if not r['won'])} lost\n")
        P("| Bid size | Orders fully filled | Money that filled | P&L | Per $100 | Bot's own record says |")
        P("|---|---|---|---|---|---|")
        out = {}
        for S in (10,) + SIZES:
            full = sum(1 for r in rows if r["s"][S][0] >= S / r["price"] * 0.97)
            cost = sum(r["s"][S][1] for r in rows)
            pnl = sum(r["s"][S][2] for r in rows)
            own = [c["rs_pnl"][str(S)] for c in orders if (c.get("rs_pnl") or {}).get(str(S))]
            own_txt = usd(100 * sum(x[1] for x in own) / sum(x[0] for x in own)) if own and sum(x[0] for x in own) else "-"
            lost_fill = [r["s"][S][0] / (S / r["price"]) for r in rows if not r["won"]]
            won_fill = [r["s"][S][0] / (S / r["price"]) for r in rows if r["won"]]
            per100 = 100 * pnl / cost if cost else 0
            P(f"| ${S} | {full} of {len(rows)} | ${cost:,.0f} | {usd(pnl)} | {usd(per100)} | {own_txt} |")
            out[S] = {"full": full, "n": len(rows), "spent": round(cost, 2), "pnl": round(pnl, 2), "per100": round(per100, 2),
                      "won_fill": round(statistics.mean(won_fill), 3) if won_fill else None,
                      "lost_fill": round(statistics.mean(lost_fill), 3) if lost_fill else None}
        s100 = out[100]
        if s100["won_fill"] is not None and s100["lost_fill"] is not None:
            P(f"\nAt $100 a bid, winning bets got {100 * s100['won_fill']:.0f} of every 100 contracts they asked for, "
              f"losing bets {100 * s100['lost_fill']:.0f}. A big gap means the bigger the bid, the more of it lands on losers.\n")
        res[n] = {"orders": len(rows), "per_day": round(len(rows) / days, 1), "sizes": out}
    return res


# ---------------------------------------------------------------- report

def write(res):
    os.makedirs(OUT, exist_ok=True)
    head = [f"# Do the leads still pay at real-money sizes? (bigbets.py, {bot.iso()[:16]}Z)", "",
            "Paper only, research only. The paper tracks buy about $1-5 a bet. Real money would be $25-100 a bet. "
            "Code: `bigbets.py`, run with probe `big_all`. Raw numbers: `backtest/bigbets.json`.", ""]
    with open(os.path.join(OUT, "bigbets.md"), "w") as f:
        f.write("\n".join(head + LINES) + "\n")
    with open(os.path.join(OUT, "bigbets.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("BIGBETS JSON " + json.dumps(res, default=str))


def main(what):
    res = {}
    if what in ("live", "all"):
        res["live"] = live()
    if what in ("kalshi", "all"):
        res["kalshi"] = kalshi()
    if what in ("hist", "all"):
        try:
            res["hist"] = hist()
        except Exception as e:
            P(f"(old trades skipped: {e})")
    write(res)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
