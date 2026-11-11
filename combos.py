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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    t0 = time.time()
    {"peek": peek}[cmd]()
    print(f"done in {time.time() - t0:.0f}s")
