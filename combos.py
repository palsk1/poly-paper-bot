"""Polymarket Combos (parlays) check, 2026-11-11 (Jan: "is the combos page worth exploring?"). Report backtest/combos.md.

Combos are bought through a request-for-quote: the user asks, pro market makers answer within 400 ms,
the user can only buy (or sell back) the YES side = the parlay. So the question is how much the makers
charge over "the legs multiplied", and whether combo buyers lose more than single-bet buyers.

    python3 combos.py peek      # probe `cmb_peek`: raw API shapes (catalog, global trades, combo activity)
    python3 combos.py run       # probe `cmb_run`: sample combo buys, price vs legs multiplied, results
"""
import collections
import json
import os
import sys
import time

import bot

DATA = "https://data-api.polymarket.com"
RFQ = "https://combos-rfq-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"


def show(name, obj, n=1500):
    print(f"\n=== {name} ===")
    print(json.dumps(obj, indent=1, default=str)[:n])


def get(url, params=None):
    try:
        return bot.http_json(url, params)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def rows(res):
    if isinstance(res, dict):
        return res.get("data") or res.get("markets") or []
    return res or []


def peek2():
    """Per-fill combo prices: trades/activity feeds by combo condition."""
    u = "0xebfdb8164f0e0748818d6c7a9ac85a323267fd63"
    ps = rows(get(DATA + "/v2/positions/combos", {"user": u, "limit": 5, "status": "RESOLVED_WIN,RESOLVED_LOSS"}))
    for p in ps[:2]:
        cid = p["combo_condition_id"]
        print("position", cid, p.get("entry_avg_price_usdc"), p.get("gross_entry_cost_usdc"), p.get("first_entry_at"), p.get("current_size"))
        show("trades by condition", rows(get(DATA + "/v2/trades", {"condition": cid, "limit": 20})), 2500)
        show("trades by user+condition", rows(get(DATA + "/v2/trades", {"user": u, "condition": cid, "limit": 20})), 2000)
        show("activity by user+condition", rows(get(DATA + "/v2/activity", {"user": u, "condition": cid, "limit": 20})), 2000)
        show("combo activity by user+condition", [{k: v for k, v in a.items() if k != "legs"} for a in rows(get(DATA + "/v2/activity/combos", {"user": u, "condition": cid}))], 2000)
    act = rows(get(DATA + "/v2/activity", {"user": u, "limit": 500}))
    print("activity types", collections.Counter((a.get("type"), a.get("is_combo")) for a in act))
    show("combo activity rows in /v2/activity", [a for a in act if a.get("is_combo")][:3], 2500)


def peek3(n=12):
    """Show a few 2-3 leg combo fills with each leg's question, side and chart price, to sanity-check the legs-multiplied number."""
    import random
    ws = wallets(40)
    random.seed(3)
    pos = []
    for u in ws[:25]:
        pos += [p for p in positions(u, 1) if 2 <= len(p.get("legs") or []) <= 3]
    random.shuffle(pos)
    for p in pos[:n]:
        cid = p["combo_condition_id"]
        fills = rows(get(DATA + "/v2/trades", {"condition": cid, "limit": 50}))
        print(f"\nCOMBO {cid[:14]} status {p.get('status')} avg {p.get('entry_avg_price_usdc')} first {p.get('first_entry_at')} fills {len(fills)}")
        for f in fills[:4]:
            print(f"   fill {f.get('side')} {f.get('price'):.4f} x {f.get('size'):.1f} at {f.get('timestamp')}")
        t = fills[-1]["timestamp"] if fills else iso_t(p["first_entry_at"])
        prod = 1
        for lg in p["legs"]:
            m = lg.get("market") or {}
            tok = leg_token(lg)
            pr, age = price_at(tok, t) if tok else (None, None)
            g = _tok.get(m.get("market_id"))
            print(f"   leg {m.get('question')!r} outcome[{lg.get('leg_outcome_index')}]={lg.get('leg_outcome_label')} {lg.get('leg_status')} "
                  f"chart {pr} ({age}s old) end {m.get('end_date')}")
            prod *= pr or 0
        print(f"   legs multiplied {prod:.4f} vs first fill {fills[-1]['price'] if fills else None}")


def peek():
    cat = get(RFQ + "/v1/rfq/combo-markets", {"limit": 100})
    ms = rows(cat)
    print("combo-enabled leg markets on page 1:", len(ms), "next:", (cat or {}).get("next_cursor"))
    show("combo-markets[0]", ms[:1])
    tags = collections.Counter(t for m in ms for t in (m.get("tags") or []))
    print("tags:", tags.most_common(15))

    # global trade feed, look for combo rows
    combo_rows, n, cur = [], 0, None
    for _ in range(8):
        p = {"limit": 1000}
        if cur:
            p = {"cursor": cur}
        res = get(DATA + "/v2/trades", p)
        rs = rows(res)
        n += len(rs)
        combo_rows += [r for r in rs if r.get("is_combo")]
        cur = (res.get("pagination") or {}).get("next_cursor") if isinstance(res, dict) else None
        if not cur:
            break
    print(f"global trades scanned {n}, combo rows {len(combo_rows)}")
    if n:
        show("trade[0] (any)", rows(get(DATA + "/v2/trades", {"limit": 1}))[:1], 1200)
    show("combo trade rows", combo_rows[:3], 2500)

    for cat_name in ("combos",):
        lb = get(DATA + "/v2/leaderboard", {"category": cat_name, "time_period": "month"})
        show(f"leaderboard {cat_name}", rows(lb)[:3], 1500)
        bw = get(DATA + "/v2/biggest-winners", {"category": cat_name, "time_period": "week"})
        show(f"biggest winners {cat_name}", rows(bw)[:2], 1500)

    users = [r.get("proxy_wallet") for r in combo_rows if r.get("proxy_wallet")]
    if not users:
        lb = rows(get(DATA + "/v2/leaderboard", {"category": "combos", "time_period": "month", "sort_direction": "asc"}))
        show("leaderboard combos asc (losers?)", lb[:2], 800)
        users = [r.get("user_id") for r in rows(get(DATA + "/v2/leaderboard", {"category": "combos", "time_period": "week"}))[5:7]]
        users += [r.get("user_id") for r in lb[:1]]
    for u in users[:3]:
        act = rows(get(DATA + "/v2/activity/combos", {"user": u, "limit": 200}))
        print(u, "activity rows", len(act), collections.Counter(a.get("type") for a in act))
        show(f"activity/combos {u}", act[:2], 5000)
        pos = rows(get(DATA + "/v2/positions/combos", {"user": u, "limit": 100}))
        print(u, "positions", len(pos))
        show(f"positions/combos {u}", pos[:1], 5000)
        tr = rows(get(DATA + "/v2/trades", {"user": u, "limit": 200}))
        ct = [t for t in tr if t.get("is_combo")]
        print(u, "trades", len(tr), "combo trades", len(ct))
        show("combo trade rows for user", ct[:2], 1500)
        if act:
            leg = (act[0].get("legs") or [{}])[0]
            cid = leg.get("leg_condition_id")
            show("gamma market for leg cid", get("https://gamma-api.polymarket.com/markets", {"condition_ids": cid}), 1200)
            show("tokens for leg cid", get(DATA + "/v2/tokens", {"condition": cid}), 1500)


CLOB = "https://clob.polymarket.com"
_tok = {}


def wallets(cap=160):
    """Combo traders from the combo P&L boards and biggest combo wins (winners only: fine for the markup, biased for results)."""
    seen = []
    for per in ("day", "week", "month", "all"):
        for off in (0, 50, 100):
            for r in rows(get(DATA + "/v2/leaderboard", {"category": "combos", "time_period": per, "limit": 50, "offset": off})):
                u = r.get("user_id")
                if u and u not in seen:
                    seen.append(u)
        for r in rows(get(DATA + "/v2/biggest-winners", {"category": "combos", "time_period": per, "limit": 100})):
            u = r.get("user_id")
            if u and u not in seen:
                seen.append(u)
    print("combo wallets found:", len(seen))
    return seen[:cap]


def positions(u, pages=5):
    out, cur = [], None
    for _ in range(pages):
        p = {"user": u, "limit": 100, "status": "OPEN,RESOLVED_WIN,RESOLVED_LOSS,RESOLVED_PARTIAL"} if not cur else {"user": u, "cursor": cur}
        res = get(DATA + "/v2/positions/combos", p)
        out += rows(res)
        cur = (res.get("pagination") or {}).get("next_cursor") if isinstance(res, dict) else None
        if not cur:
            break
    return out


def leg_info(leg):
    """(CLOB token of the leg's outcome, game start unix or None), from the Gamma market (combo legs carry v2 ids the chart doesn't know)."""
    mid, oi = (leg.get("market") or {}).get("market_id"), leg.get("leg_outcome_index")
    if mid not in _tok:
        m = get(f"https://gamma-api.polymarket.com/markets/{mid}")
        toks = m.get("clobTokenIds") if isinstance(m, dict) else None
        if isinstance(toks, str):
            try:
                toks = json.loads(toks)
            except ValueError:
                toks = None
        gs = None
        try:
            g = (m.get("gameStartTime") or "").strip() if isinstance(m, dict) else ""
            if g:
                import datetime as dt
                gs = int(dt.datetime.fromisoformat(g.replace(" ", "T").replace("+00", "+00:00").replace("Z", "+00:00")).timestamp())
        except ValueError:
            gs = None
        _tok[mid] = (toks or [], gs)
    toks, gs = _tok[mid]
    return (toks[oi] if isinstance(oi, int) and oi < len(toks) else None), gs


def leg_token(leg):
    return leg_info(leg)[0]


_dbg = [0]


def price_at(tok, t):
    """Last chart price of a single-leg token at or before t (1-minute points, up to 3 h back)."""
    res = get(CLOB + "/prices-history", {"market": tok, "startTs": t - 3 * 3600, "endTs": t + 60, "fidelity": 1})
    pts = [(bot.fnum(x.get("t"), 0), bot.fnum(x.get("p"), None)) for x in bot.envelope_rows(res, "history", "data") if isinstance(x, dict)]
    pts = [x for x in pts if x[1] is not None and x[0] <= t + 60]
    if _dbg[0] < 0:
        _dbg[0] += 1
        print("debug hist", tok[:12], t, str(res)[:300])
    return (pts[-1][1], t - pts[-1][0]) if pts else (None, None)


def iso_t(s):
    import datetime as dt
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def fee_of(p, shares):
    return 0.05 * p * (1 - p) * shares   # sports fee rate (2026-07), checked on a real combo buy: 515.74 on 44,044 shares at 37.4c


def yes_result(pos):
    st = pos.get("status")
    if st not in ("RESOLVED_WIN", "RESOLVED_LOSS"):
        return None
    win = st == "RESOLVED_WIN"
    if pos.get("outcome_index") == 1:      # this wallet held the NO side (the maker's side): flip it
        win = not win
    return 1.0 if win else 0.0


def one(pos, max_fills=4):
    """Every YES buy of one combo (public trade list): price paid vs the legs multiplied on the chart at that minute."""
    legs = pos.get("legs") or []
    fills = [f for f in rows(get(DATA + "/v2/trades", {"condition": pos["combo_condition_id"], "limit": 100}))
             if f.get("side") == "BUY" and bot.fnum(f.get("size"), 0) > 0 and 0 < bot.fnum(f.get("price"), 0) < 1]
    fills = sorted(fills, key=lambda f: f["timestamp"])[:max_fills]
    infos = [leg_info(lg) for lg in legs]
    if not fills or any(not tok for tok, _ in infos):
        return []
    evs = [((lg.get("market") or {}).get("event") or {}).get("event_id") for lg in legs]
    kinds = [(lg.get("market") or {}).get("sports_market_type") or "other" for lg in legs]
    res = yes_result(pos)
    out = []
    for f in fills:
        t = int(f["timestamp"])
        prod, ages, decided = 1.0, [], False
        for tok, _ in infos:
            p, age = price_at(tok, t)
            if p is None:
                prod = None
                break
            decided |= p >= 0.985 or p <= 0.015
            prod *= p
            ages.append(age)
        if prod is None:
            continue
        price, size = float(f["price"]), float(f["size"])
        out.append({"price": price, "prod": prod, "legs": len(legs), "same_game": len(set(evs)) < len(evs),
                    "gross": price * size + fee_of(price, size), "fee": fee_of(price, size), "size": size,
                    "payout": None if res is None else res * size, "decided": decided,
                    "in_play": any(gs and gs <= t for _, gs in infos), "max_age": max(ages) if ages else 0,
                    "kinds": kinds, "t": t, "cid": pos["combo_condition_id"]})
    return out


def run(cap_w=160, cap_pos=2500):
    from concurrent.futures import ThreadPoolExecutor
    ws = wallets(cap_w)
    pos = []
    with ThreadPoolExecutor(8) as ex:
        for ps in ex.map(positions, ws):
            pos += [p for p in ps if p.get("first_entry_at") and p.get("legs") and bot.fnum(p.get("gross_entry_cost_usdc"), 0) > 0]
    print("combo positions:", len(pos), collections.Counter(p.get("status") for p in pos).most_common())
    by = {}
    for p in pos:                      # one row per combo; prefer a holder of the YES side
        c = p["combo_condition_id"]
        if c not in by or p.get("outcome_index") == 0:
            by[c] = p
    pos = list(by.values())
    import random
    random.seed(11)
    random.shuffle(pos)
    print("different combos:", len(pos), "held on the NO (maker) side by these wallets:", sum(1 for p in pos if p.get("outcome_index") == 1))
    pos = pos[:cap_pos]
    res = []
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(one, pos):
            res += r
    allr = res
    res = [r for r in res if r["max_age"] <= 1800 and not r["decided"]]
    print(f"YES buys priced: {len(allr)}; kept {len(res)} (every leg had a chart price within 30 min, no leg already 98.5c+/1.5c-)")
    json.dump(res, open("combos_rows.json", "w"))

    def block(name, rs):
        if not rs:
            print(f"{name}: none"); return
        g = sum(r["gross"] for r in rs)
        fair = sum(r["size"] * r["prod"] for r in rs)          # what the shares would cost at the legs multiplied
        paid = sum(r["size"] * r["price"] for r in rs)
        fee = sum(r["fee"] for r in rs)
        ratios = sorted(r["price"] / r["prod"] for r in rs)
        cheap = sum(1 for x in ratios if x < 1)
        done = [r for r in rs if r["payout"] is not None]
        back = sum(r["payout"] for r in done); spent = sum(r["gross"] for r in done)
        exp_back = sum(r["size"] * r["prod"] for r in done)
        print(f"{name}: {len(rs)} combos, ${g:,.0f} spent | per $100 spent: legs-multiplied worth ${100 * fair / g:.2f}, "
              f"maker's extra ${100 * (paid - fair) / g:.2f}, fee ${100 * fee / g:.2f} | median price/legs {ratios[len(ratios) // 2]:.3f}, "
              f"middle half {ratios[len(ratios) // 4]:.3f}-{ratios[3 * len(ratios) // 4]:.3f}, cheaper than legs {cheap}/{len(rs)} | "
              f"finished {len(done)}: got back ${100 * back / spent if spent else 0:.2f} per $100 (legs said ${100 * exp_back / spent if spent else 0:.2f}; combos picked from big combo wallets)")

    block("ALL", res)
    block("before any game started", [r for r in res if not r["in_play"]])
    block("a game already running", [r for r in res if r["in_play"]])
    for k in (2, 3, 4):
        block(f"{k} legs", [r for r in res if r["legs"] == k])
    block("5+ legs", [r for r in res if r["legs"] >= 5])
    block("same game in it", [r for r in res if r["same_game"]])
    block("all different games", [r for r in res if not r["same_game"]])
    block("under $100", [r for r in res if r["gross"] < 100])
    block("$100-1,000", [r for r in res if 100 <= r["gross"] < 1000])
    block("$1,000+", [r for r in res if r["gross"] >= 1000])
    block("long shot (legs < 20c)", [r for r in res if r["prod"] < 0.2])
    block("legs 20-60c", [r for r in res if 0.2 <= r["prod"] < 0.6])
    block("legs 60c+", [r for r in res if r["prod"] >= 0.6])
    print("cheapest 8 vs legs:")
    for r in sorted(res, key=lambda r: r["price"] / r["prod"])[:8]:
        print(f"  paid {r['price']:.3f} legs {r['prod']:.3f} legs={r['legs']} same_game={r['same_game']} ${r['gross']:,.0f} {r['payout']} {r['kinds']}")


def yes_positions(u):
    """A wallet's finished YES combos (status filter needed: the default listing hides redeemed wins)."""
    out, cur = [], None
    for _ in range(3):
        p = {"user": u, "limit": 100, "status": "RESOLVED_WIN,RESOLVED_LOSS"} if not cur else {"user": u, "cursor": cur}
        res = get(DATA + "/v2/positions/combos", p)
        out += [x for x in rows(res) if x.get("outcome_index") == 0]
        cur = (res.get("pagination") or {}).get("next_cursor") if isinstance(res, dict) else None
        if not cur:
            break
    return out


def replay(n_seed=700, n_buyers=500, cap_combos=3000):
    """Paper house: would selling combos a bit cheaper than the pros have kept money after the real results?
    Sample: ordinary buyers found on the big wallets' combos (second hop), then ALL their finished YES combos, so the
    combos are not picked by who won. Each buy is re-priced: we'd sell at legs x (1 + markup) and only get the buy
    when that is below what the buyer really paid (we'd be the cheapest quote)."""
    import random
    from concurrent.futures import ThreadPoolExecutor
    import exam
    random.seed(5)
    seeds = wallets(160)
    pos = []
    with ThreadPoolExecutor(8) as ex:
        for ps in ex.map(lambda u: positions(u, 2), seeds):
            pos += ps
    cids = list({p["combo_condition_id"] for p in pos})
    random.shuffle(cids)
    buyers = collections.Counter()
    with ThreadPoolExecutor(8) as ex:
        for fs in ex.map(lambda c: rows(get(DATA + "/v2/trades", {"condition": c, "limit": 100})), cids[:n_seed]):
            for f in fs:
                if f.get("side") == "BUY" and f.get("proxy_wallet") not in seeds:
                    buyers[f["proxy_wallet"]] += 1
    bl = list(buyers)
    random.shuffle(bl)
    print(f"seed combos read {min(n_seed, len(cids))}, ordinary buyers found {len(bl)}, using {min(n_buyers, len(bl))}")
    yp = {}
    with ThreadPoolExecutor(8) as ex:
        for ps in ex.map(yes_positions, bl[:n_buyers]):
            for p in ps:
                if p.get("legs") and p.get("first_entry_at"):
                    yp.setdefault(p["combo_condition_id"], p)
    combos = list(yp.values())
    random.shuffle(combos)
    print("finished YES combos of those buyers:", len(combos), collections.Counter(p["status"] for p in combos).most_common())
    res = []
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(lambda p: one(p, 3), combos[:cap_combos]):
            res += r
    res = [r for r in res if r["max_age"] <= 1800 and not r["decided"] and r["payout"] is not None]
    print(f"buys kept: {len(res)} on {len({r['cid'] for r in res})} combos")
    json.dump(res, open("combos_replay.json", "w"))

    def house(rs, name):
        paid = sum(r["price"] * r["size"] for r in rs)
        back = sum(r["payout"] for r in rs)
        fair = sum(r["prod"] * r["size"] for r in rs)
        n = len(rs)
        print(f"{name}: {n} buys, buyers paid ${paid:,.0f}, legs said ${fair:,.0f}, combos paid out ${back:,.0f} "
              f"-> the house kept ${100 * (paid - back) / paid if paid else 0:+.2f} per $100 of buyers' money "
              f"(legs-only guess ${100 * (paid - fair) / paid if paid else 0:+.2f}); won {sum(1 for r in rs if r['payout'] > 0)} of {n}")

    print("\n-- The pros as they are (sold at the real price) --")
    house(res, "all buys")
    for k, f in (("2 legs", lambda r: r["legs"] == 2), ("3-4 legs", lambda r: 3 <= r["legs"] <= 4), ("5+ legs", lambda r: r["legs"] >= 5),
                 ("legs under 20c", lambda r: r["prod"] < 0.2), ("legs 20-60c", lambda r: 0.2 <= r["prod"] < 0.6),
                 ("legs 60c+", lambda r: r["prod"] >= 0.6), ("before games", lambda r: not r["in_play"]), ("game running", lambda r: r["in_play"]),
                 ("no same-game legs", lambda r: not r["same_game"])):
        house([r for r in res if f(r)], k)

    print("\n-- Us as the house: quote legs x (1 + markup), only where that beats the pros' price; $25 at risk a buy --")
    tries = 0
    best = None
    for name, f in (("all", lambda r: True), ("2-4 legs, no same game", lambda r: r["legs"] <= 4 and not r["same_game"]),
                    ("long shots under 20c", lambda r: r["prod"] < 0.2)):
        for m in (0.0, 0.02, 0.03, 0.05, 0.10):
            tries += 1
            bets = []
            for r in res:
                if not f(r):
                    continue
                q = r["prod"] * (1 + m)
                if not (q < r["price"] and q < 0.97):
                    continue
                sh = 25 / (1 - q)                     # shares we'd back with $25 of our money
                bets.append({"ev": r["cid"], "t": r["t"], "cost": 25.0, "pay": 0.0 if r["payout"] > 0 else 25 + q * sh})
            c = exam.score(bets, f"paper house {name} +{int(m * 100)}%", tries=tries, log=False, quiet=True)
            print(f"{name:24s} markup +{int(m * 100):2d}%: {len(bets):5d} buys we'd win, {usd(c.get('per100'))} per $100 at risk, "
                  f"luck range {usd(c.get('lo100'))} to {usd(c.get('hi100'))}, halves {usd(c.get('half1'))}/{usd(c.get('half2'))}, {c['verdict']}")
            if c.get("per100") is not None and (best is None or (c.get("lo100") or -1e9) > (best[1].get("lo100") or -1e9)):
                best = (bets, c, name, m)
    if best:
        exam.score(best[0], f"Paper house for Polymarket combos ({best[2]}, legs +{int(best[3] * 100)}%)", tries=tries,
                   src="combos.py replay, backtest/combos.md", log=True)


# ---------------------------------------------------------------- live paper quoter results (quoter/quoter.py on Jan's server)
def q_logs(local=None):
    """Every line the paper quoter wrote: from a local folder, or the public release `quoter-data`."""
    import gzip
    import io
    import urllib.request
    out = []
    if local:
        for fn in sorted(os.listdir(local)):
            if fn.endswith(".jsonl"):
                out += [json.loads(x) for x in open(os.path.join(local, fn)) if x.strip()]
        return out
    rel = get("https://api.github.com/repos/palsk1/poly-paper-bot/releases/tags/quoter-data")
    if not isinstance(rel, dict) or rel.get("error"):
        print("no quoter data yet:", rel)
        return out
    for a in rel.get("assets") or []:
        if a["name"].endswith(".jsonl.gz"):
            raw = urllib.request.urlopen(urllib.request.Request(a["browser_download_url"], headers={"User-Agent": "poly-paper-bot"}), timeout=60).read()
            out += [json.loads(x) for x in gzip.open(io.BytesIO(raw)).read().decode().splitlines() if x.strip()]
    return out


_leg_cache = {}


def leg_result(tok):
    """1 = this leg's outcome won, 0 = lost, None = not settled yet (Gamma, by CLOB token)."""
    if tok in _leg_cache:
        return _leg_cache[tok]
    r = None
    try:
        ms = get(GAMMA + "/markets", {"clob_token_ids": tok, "closed": "true"})
        for m in (ms if isinstance(ms, list) else []):
            toks = json.loads(m["clobTokenIds"]) if isinstance(m.get("clobTokenIds"), str) else m.get("clobTokenIds") or []
            px = json.loads(m["outcomePrices"]) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices") or []
            if tok in toks and px:
                p = float(px[toks.index(tok)])
                r = 1 if p >= 0.99 else 0 if p <= 0.01 else None
    except Exception as e:  # noqa: BLE001
        print("leg lookup failed", tok[:12], e)
    _leg_cache[tok] = r
    return r


def q_match(lines, rule, result=leg_result, stake=25.0):
    """Pair each request we priced with the trade that really happened. We 'win' a request when our would-be quote
    is below the price the winning pro got (the buyer takes the cheapest quote). The house's bet: $stake of our
    money backs the parlay failing; we keep it plus the buyer's money if any leg loses, we lose it if all legs win."""
    trades = {}
    for x in lines:
        if x.get("k") == "trade" and x.get("rfq"):
            trades[x["rfq"]] = x
    reqs = [x for x in lines if x.get("k") == "req"]
    won, pending, bets = [], 0, []
    for r in reqs:
        q = (r.get("quotes") or {}).get(rule)
        tr = trades.get(r.get("rfq"))
        if q is None or not tr or not r.get("in_time"):
            continue
        price = float(tr["price"]) / 1e6 if tr.get("price") is not None else None
        if price is None or not q < price:
            continue
        won.append(r)
        toks = r.get("tokens") or [lg["token"] for lg in r.get("leg_info") or []]
        res = [result(t) for t in toks]
        if 0 in res:
            pay = stake + q * stake / (1 - q)     # parlay failed: we keep our stake and the buyer's money
        elif res and all(x == 1 for x in res):
            pay = 0.0                              # parlay hit: our stake goes to the buyer
        else:
            pending += 1
            continue
        bets.append({"ev": r.get("cid") or r["rfq"], "t": (r.get("seen") or 0) / 1000, "cost": stake, "pay": pay,
                     "price": price, "q": q})
    return reqs, trades, won, pending, bets


def qscore(local=None):
    """Score the live paper quoter (pre-registered in backtest/PROTOCOL.md 5c)."""
    import exam
    lines = q_logs(local or os.environ.get("QUOTER_DIR"))
    notes = [x for x in lines if x.get("k") == "note"]
    reqs = [x for x in lines if x.get("k") == "req"]
    print(f"lines {len(lines)}: requests {len(reqs)}, trades {sum(1 for x in lines if x.get('k') == 'trade')}, notes {len(notes)}")
    auth = [x for x in notes if x.get("what") == "auth"]
    if auth:
        print("last login:", auth[-1])
    if not reqs:
        print("No requests seen yet. If logins succeed but nothing arrives, Polymarket doesn't send requests to a quoter that only listens.")
        return
    print("skipped:", collections.Counter((x.get("skip") or "priced").split(" ")[0] for x in reqs).most_common())
    lat = sorted((x["priced"] - x["seen"]) for x in reqs if x.get("priced"))
    if lat:
        print(f"time to price a request: middle {lat[len(lat) // 2]} ms, slowest 1 in 10 {lat[int(len(lat) * 0.9)]} ms; "
              f"in time {sum(1 for x in reqs if x.get('in_time'))} of {len(reqs)}")
    print("legs:", collections.Counter(x["legs"] if isinstance(x.get("legs"), int) else len(x.get("legs") or []) for x in reqs).most_common(8))
    for x in notes:
        if x.get("what") == "counts":
            print("10-min counts:", x.get("counts"), x.get("pricer"))
    for rule in ("main", "m3", "all5"):
        reqs, trades, won, pending, bets = q_match(lines, rule)
        quoted = sum(1 for r in reqs if (r.get("quotes") or {}).get(rule) is not None)
        traded = sum(1 for r in reqs if (r.get("quotes") or {}).get(rule) is not None and r.get("rfq") in trades)
        print(f"\n[{rule}] would quote {quoted}, of those really traded {traded}, we'd have been cheapest on {len(won)}, "
              f"settled {len(bets)}, waiting {pending}")
        if bets:
            c = exam.score(bets, f"Paper combo quoter, live ({rule})", tries=1, prereg=True, src="quoter/quoter.py, combos.py qscore",
                           log=(rule == "main"), quiet=False)
            gap = sum(b["price"] - b["q"] for b in bets) / len(bets)
            print(f"average: we'd quote {100 * gap:.1f}c a share below the pro who won")


def qtest():
    """Offline check of the quoter scoring with made-up lines."""
    L = [{"k": "req", "rfq": "a", "cid": "c1", "dir": "BUY", "seen": 1000, "priced": 1050, "in_time": True,
          "quotes": {"main": 0.30, "m3": 0.29, "all5": 0.30}, "leg_info": [{"token": "t1"}, {"token": "t2"}]},
         {"k": "req", "rfq": "b", "cid": "c2", "dir": "BUY", "seen": 2000, "priced": 2050, "in_time": True,
          "quotes": {"main": 0.50, "m3": 0.49, "all5": 0.50}, "leg_info": [{"token": "t3"}, {"token": "t4"}]},
         {"k": "req", "rfq": "c", "cid": "c3", "dir": "BUY", "seen": 3000, "priced": 3050, "in_time": True,
          "quotes": {"main": 0.40, "m3": 0.39, "all5": 0.40}, "leg_info": [{"token": "t1"}, {"token": "t5"}]},
         {"k": "req", "rfq": "d", "cid": "c4", "dir": "BUY", "seen": 4000, "priced": 4050, "in_time": True,
          "quotes": {"main": 0.20, "m3": 0.19, "all5": 0.20}, "leg_info": [{"token": "t1"}]},
         {"k": "trade", "rfq": "a", "price": 330000}, {"k": "trade", "rfq": "b", "price": 480000},
         {"k": "trade", "rfq": "c", "price": 450000}, {"k": "trade", "rfq": "d", "price": 250000}]
    res = {"t1": 1, "t2": 0, "t3": 1, "t4": 1, "t5": None}.get
    reqs, trades, won, pending, bets = q_match(L, "main", result=res)
    # a: cheaper (30 < 33), a leg lost -> we keep $25 + buyer's money; b: pro cheaper, not ours; c: ours, still open;
    # d: ours, its one leg won -> we pay
    assert [r["rfq"] for r in won] == ["a", "c", "d"] and pending == 1, (won, pending)
    assert abs(bets[0]["pay"] - (25 + 0.30 * 25 / 0.70)) < 1e-9 and bets[1]["pay"] == 0.0, bets
    print("quoter scoring test ok")


def qstate(path="state/quoter.json", min_age=1500, max_lookups=300):
    """Small scoreboard of the paper combo quoter for the dashboard (run by watch, at most every 25 min)."""
    import exam
    old = {}
    try:
        old = json.load(open(path))
    except (OSError, ValueError):
        pass
    if old.get("generated_ts") and time.time() - old["generated_ts"] < min_age:
        print("quoter state is fresh, skipped")
        return
    lines = q_logs(os.environ.get("QUOTER_DIR"))
    if not lines:
        return
    cache = {k: v for k, v in (old.get("leg_results") or {}).items()}
    lookups = [0]

    def res(tok):
        if tok in cache:
            return cache[tok]
        if lookups[0] >= max_lookups:
            return None
        lookups[0] += 1
        r = leg_result(tok)
        if r is not None:
            cache[tok] = r
        return r

    reqs, trades, won, pending, bets = q_match(lines, "main", result=res)
    names = {}
    for x in lines:
        if x.get("k") == "legs":
            for tok, info in (x.get("legs") or {}).items():
                names[tok] = info
    recent = []
    for r in sorted(won, key=lambda r: r.get("seen") or 0, reverse=True):
        toks = r.get("tokens") or [lg["token"] for lg in r.get("leg_info") or []]
        rs = [cache.get(t) for t in toks]
        q = r["quotes"]["main"]
        price = float(trades[r["rfq"]]["price"]) / 1e6
        if 0 in rs:
            end, gain = "kept", round(25 * q / (1 - q), 2)
        elif rs and all(v == 1 for v in rs):
            end, gain = "paid", -25.0
        else:
            end, gain = "waiting", None
        recent.append({"t": (r.get("seen") or 0) / 1000, "q": round(q, 4), "price": round(price, 4), "end": end, "gain": gain,
                       "legs": [{"title": (names.get(t) or {}).get("title") or "unknown market",
                                 "out": (names.get(t) or {}).get("out") or "", "res": v} for t, v in zip(toks, rs)]})
    recent = [x for x in recent if x["end"] != "waiting"][:30] + [x for x in recent if x["end"] == "waiting"][:30]
    heard = sum(int((x.get("pricer") or {}).get("heard", 0)) for x in lines if x.get("k") == "note" and x.get("what") == "counts")
    last = max((x.get("t") or 0) for x in lines)
    c = exam.score(bets, "Paper combo quoter, live (main)", tries=1, prereg=True, log=False, quiet=True) if bets else {}
    paid = sum(b["cost"] for b in bets)
    back = sum(b["pay"] for b in bets)
    # running total for the dashboard graph (same shape as a track's curve: start, one point per finished bet, now)
    curve, run_ = [], 0.0
    for b_ in sorted(bets, key=lambda b_: b_.get("t") or 0):
        run_ += b_["pay"] - b_["cost"]
        curve.append([time.strftime("%Y-%m-%dT%H:%M", time.gmtime(b_.get("t") or 0)), round(run_, 2)])
    if curve:
        curve = [[curve[0][0], 0.0]] + curve + [[time.strftime("%Y-%m-%dT%H:%M", time.gmtime()), round(run_, 2)]]
    out = {"generated_ts": time.time(), "last_seen": last / 1000 if last else None,
           "days": sorted({time.strftime("%Y-%m-%d", time.gmtime((x.get("t") or 0) / 1000)) for x in lines if x.get("t")}),
           "heard": heard, "priced": len(reqs), "trades": len(trades), "would_win": len(won), "settled": len(bets),
           "waiting": pending, "won_by_house": sum(1 for b in bets if b["pay"] > 0),
           "pnl": round(back - paid, 2), "at_risk": round(paid, 2), "curve": curve, "per100": c.get("per100"), "lo100": c.get("lo100"), "hi100": c.get("hi100"),
           "verdict": c.get("verdict") if bets else "Too early to tell",
           "rule": "2-4 legs, no two legs from the same game, our price = the legs multiplied, +5%, $25 at risk a bet",
           "pass_rule": "Pass (fixed 11 Nov): above +$1.00 per $100 and both halves ahead, at 1 Jan or 1,000 finished bets",
           "bets": recent, "leg_results": cache}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print({k: v for k, v in out.items() if k not in ("leg_results", "bets")}, "lookups", lookups[0], "listed", len(recent))


def usd(x):
    return "n/a" if x is None else (f"+${x:.2f}" if x >= 0 else f"-${-x:.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    t0 = time.time()
    {"peek": peek, "peek2": peek2, "peek3": peek3, "run": run, "replay": replay, "qscore": qscore, "qtest": qtest, "qstate": qstate}[cmd]()
    print(f"done in {time.time() - t0:.0f}s")
