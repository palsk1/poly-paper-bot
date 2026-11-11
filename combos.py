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


def leg_token(leg):
    """CLOB token of the leg's outcome, from the Gamma market (combo legs carry v2 condition ids the chart doesn't know)."""
    mid, oi = (leg.get("market") or {}).get("market_id"), leg.get("leg_outcome_index")
    if mid not in _tok:
        m = get(f"https://gamma-api.polymarket.com/markets/{mid}")
        toks = m.get("clobTokenIds") if isinstance(m, dict) else None
        if isinstance(toks, str):
            try:
                toks = json.loads(toks)
            except ValueError:
                toks = None
        _tok[mid] = toks or []
        if len(_tok) <= 3:
            print("debug gamma", mid, str(m)[:300])
    toks = _tok[mid]
    return toks[oi] if isinstance(oi, int) and oi < len(toks) else None


_dbg = [0]


def price_at(tok, t):
    """Last chart price of a single-leg token at or before t (1-minute points, up to 3 h back)."""
    res = get(CLOB + "/prices-history", {"market": tok, "startTs": t - 3 * 3600, "endTs": t + 60, "fidelity": 1})
    pts = [(bot.fnum(x.get("t"), 0), bot.fnum(x.get("p"), None)) for x in bot.envelope_rows(res, "history", "data") if isinstance(x, dict)]
    pts = [x for x in pts if x[1] is not None and x[0] <= t + 60]
    if _dbg[0] < 3:
        _dbg[0] += 1
        print("debug hist", tok[:12], t, str(res)[:300])
    return (pts[-1][1], t - pts[-1][0]) if pts else (None, None)


def iso_t(s):
    import datetime as dt
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def one(pos):
    legs = pos.get("legs") or []
    t = iso_t(pos["first_entry_at"])
    prod, ages, live = 1.0, [], 0
    for lg in legs:
        tok = leg_token(lg)
        if not tok:
            return None
        p, age = price_at(tok, t)
        if p is None:
            return None
        prod *= p
        ages.append(age)
    evs = [((lg.get("market") or {}).get("event") or {}).get("event_id") for lg in legs]
    kinds = [(lg.get("market") or {}).get("sports_market_type") or "other" for lg in legs]
    gross = bot.fnum(pos.get("gross_entry_cost_usdc"), 0)
    fee = bot.fnum(pos.get("entry_fees_usdc"), 0)
    price = bot.fnum(pos.get("entry_avg_price_usdc"), 0)
    size = bot.fnum(pos.get("current_size"), 0) or ((gross - fee) / price if price else 0)
    if bot.fnum(pos.get("current_size"), 0):
        price = (gross - fee) / size
    return {"price": price, "prod": prod, "legs": len(legs), "same_game": len(set(evs)) < len(evs),
            "gross": gross, "fee": fee, "size": size, "status": pos.get("status"),
            "payout": (bot.fnum(pos.get("realized_payout_usdc"), 0) or size) if pos.get("status") in ("RESOLVED_WIN", "REDEEMED", "REDEEMABLE")
            else (0.0 if pos.get("status") == "RESOLVED_LOSS" else None),
            "max_age": max(ages) if ages else 0, "kinds": kinds, "t": t, "wallet": pos.get("proxy_wallet")}


def run(cap_w=160, cap_pos=1500):
    from concurrent.futures import ThreadPoolExecutor
    ws = wallets(cap_w)
    pos = []
    with ThreadPoolExecutor(8) as ex:
        for ps in ex.map(positions, ws):
            pos += [p for p in ps if p.get("first_entry_at") and p.get("legs") and bot.fnum(p.get("gross_entry_cost_usdc"), 0) > 0]
    print("combo positions:", len(pos), collections.Counter(p.get("status") for p in pos).most_common())
    pos = pos[:cap_pos]
    with ThreadPoolExecutor(8) as ex:
        res = [r for r in ex.map(one, pos) if r]
    res = [r for r in res if r["max_age"] <= 3600 and 0.001 < r["prod"] < 0.999 and 0 < r["price"] < 1]
    print("priced (every leg had a chart price within 1 h of the buy):", len(res))
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
              f"finished {len(done)}: got back ${100 * back / spent if spent else 0:.2f} per $100 (legs said ${100 * exp_back / spent if spent else 0:.2f}; winners-only sample)")

    block("ALL", res)
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
        print(f"  paid {r['price']:.3f} legs {r['prod']:.3f} legs={r['legs']} same_game={r['same_game']} ${r['gross']:,.0f} {r['status']} {r['kinds']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    t0 = time.time()
    {"peek": peek, "run": run}[cmd]()
    print(f"done in {time.time() - t0:.0f}s")
