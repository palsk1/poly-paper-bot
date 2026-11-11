"""Polymarket Combos (parlays) check, 2026-11-11 (Jan: "is the combos page worth exploring?").

Combos are bought through a request-for-quote: the user asks, pro market makers answer within 400 ms,
the user can only buy (or sell back) the YES side = the parlay. So the question is how much the makers
charge over "the legs multiplied", and whether combo buyers lose more than single-bet buyers.

    python3 combos.py peek      # probe `cmb_peek`: raw API shapes (catalog, global trades, combo activity)
    python3 combos.py run       # probe `cmb_run`: sample combo buys, price vs legs multiplied, results
"""
import collections
import json
import sys
import time

import bot

DATA = "https://data-api.polymarket.com"
RFQ = "https://combos-rfq-api.polymarket.com"


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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    t0 = time.time()
    {"peek": peek, "peek2": peek2, "peek3": peek3, "run": run}[cmd]()
    print(f"done in {time.time() - t0:.0f}s")
