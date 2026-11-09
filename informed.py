#!/usr/bin/env python3
"""Informed-trader hunt: which Polymarket wallets trade BEFORE big price moves (not just which ones made money).
Read-only research, paper only. Probe inputs: btinf_peek, btinf_fetch, btinf_run (see TOOLS.md).
"""
import collections
import datetime as dt
import json
import os
import random
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import backtest as bt

D, G, C = bot.DATA, bot.GAMMA, bot.CLOB
CACHE = bt.CACHE
OUT = bt.OUT


def short(x, n=800):
    return json.dumps(x)[:n]


def trades_page(params):
    res = bot.http_json(f"{D}/v2/trades", params)
    rows = bot.envelope_rows(res, "data", "trades")
    cur = ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor")) if isinstance(res, dict) else None
    return rows, cur, res


def peek():
    mk = (bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}) or {}).get("markets") or {}
    sm = bt.rjson(os.path.join(CACHE, "small_markets.json.gz"), {}) or {}
    print("bt_cache markets", len(mk), "small markets", len(sm) if isinstance(sm, (dict, list)) else type(sm))
    if mk:
        k0 = next(iter(mk))
        print("market row sample", k0, short(mk[k0], 600))
    if isinstance(sm, dict) and sm:
        k0 = next(iter(sm))
        print("small row sample", k0, short(sm[k0], 600))
    rng = random.Random(1)
    vals = [m for m in mk.values() if m.get("closed") and m.get("toks")]
    vals.sort(key=lambda m: m.get("vol") or 0)
    picks = [vals[int(q * (len(vals) - 1))] for q in (0.05, 0.3, 0.6, 0.9, 0.99)] if vals else []
    for m in picks:
        print(f"\n== {m['q'][:80]} vol ${m.get('vol') or 0:,.0f} start {bt.iso_t(m['start']) if m.get('start') else '?'} end {bt.iso_t(m['end']) if m.get('end') else '?'}")
        cid = None
        for url, p in ((f"{G}/markets/{m['id']}", None), (f"{G}/markets", {"id": [m["id"], picks[0]["id"]], "closed": "true"}),
                       (f"{G}/markets", {"clob_token_ids": m["toks"][0], "closed": "true"})):
            try:
                g = bot.http_json(url, p)
                g = [g] if isinstance(g, dict) and g.get("conditionId") else bot.envelope_rows(g, "data", "markets")
                print("  gamma", url[-30:], p and list(p), "->", len(g), [x.get("conditionId", "")[:12] for x in g])
                cid = cid or (g[0].get("conditionId") if g else None)
            except Exception as e:
                print("  gamma failed", url[-30:], str(e)[:120])
        if not cid:
            continue
        allr, cur, t0, pages = [], None, time.time(), 0
        for i in range(400):
            p = {"condition_id": cid, "limit": 500}
            if cur:
                p["cursor"] = cur
            try:
                rows, cur, res = trades_page(p)
            except Exception as e:
                print("  page", i, "failed", str(e)[:200])
                break
            pages += 1
            if i == 0:
                print("  first row", short(rows[:1], 1500))
                print("  top keys", list(res.keys()) if isinstance(res, dict) else "list", "pagination", short(res.get("pagination") if isinstance(res, dict) else None, 300))
            allr += rows
            if not cur or not rows:
                break
        tt = sorted(bot.act_time(r).timestamp() for r in allr if bot.act_time(r))
        sides = collections.Counter(str(r.get("side")) for r in allr)
        wal = collections.Counter(str(bot.pick(r, "proxy_wallet", "proxyWallet", default="")) for r in allr)
        usd = sum(bot.fnum(r.get("size")) * bot.fnum(r.get("price")) for r in allr)
        print(f"  {len(allr)} trades in {pages} pages, {time.time() - t0:.1f}s, ${usd:,.0f} traded, first {bt.iso_t(tt[0]) if tt else '-'} last {bt.iso_t(tt[-1]) if tt else '-'}, sides {dict(sides)}, wallets {len(wal)}")
        for extra in ({"taker_only": "false"}, {"filterType": "CASH", "filterAmount": 500}, {"min_size": 500}):
            try:
                rows, _, res = trades_page({"condition_id": cid, "limit": 500, **extra})
                print("  with", extra, "->", len(rows))
            except Exception as e:
                print("  with", extra, "failed", str(e)[:150])
        try:
            h = bot.http_json(f"{C}/prices-history", {"market": m["toks"][0], "startTs": int(m["end"]) - 3 * 86400, "endTs": int(m["end"]), "fidelity": 5})
            pts = h.get("history") or []
            print("  prices-history fidelity 5 last 3d:", len(pts), short(pts[:2], 200))
        except Exception as e:
            print("  prices-history failed", str(e)[:150])
    print("\n== global feed (no market)")
    for p in ({"limit": 5}, {"limit": 5, "filterType": "CASH", "filterAmount": 5000}, {"limit": 5, "min_cash": 5000}):
        try:
            rows, cur, res = trades_page(p)
            print(" ", p, "->", len(rows), "cursor", bool(cur), [(r.get("price"), r.get("size"), (r.get("title") or "")[:40]) for r in rows[:5]])
        except Exception as e:
            print(" ", p, "failed", str(e)[:150])
    print("\n== global big-trade feed depth")
    for amt in (1000, 5000, 20000):
        cur, n, t_last, t0 = None, 0, None, time.time()
        for i in range(60):
            p = {"limit": 500, "filterType": "CASH", "filterAmount": amt}
            if cur:
                p["cursor"] = cur
            try:
                rows, cur, _ = trades_page(p)
            except Exception as e:
                print("   page", i, "failed", str(e)[:150])
                break
            n += len(rows)
            tt = [bot.act_time(r).timestamp() for r in rows if bot.act_time(r)]
            if tt:
                t_last = min(tt)
            if not cur or not rows:
                break
        print(f"  >= ${amt}: {n} trades in {i + 1} pages back to {bt.iso_t(t_last) if t_last else '-'} ({time.time() - t0:.0f}s)")
    print("\n== wallet first-trade lookup (fresh-wallet check)")
    for p in ({"user": "0xd3ecb2aee0d65622da559ff356b00e8c2e626603", "limit": 1, "sortDirection": "ASC"}, {"user": "0xd3ecb2aee0d65622da559ff356b00e8c2e626603", "limit": 1, "order": "asc"}):
        try:
            rows, cur, _ = trades_page(p)
            print(" ", list(p)[2:], "->", [bt.iso_t(bot.act_time(r).timestamp()) for r in rows])
        except Exception as e:
            print(" ", p, "failed", str(e)[:150])
    for path in ("v2/positions", "v1/user-stats", "v2/user-stats", "v2/profile"):
        try:
            r = bot.http_json(f"{D}/{path}", {"user": "0xd3ecb2aee0d65622da559ff356b00e8c2e626603", "limit": 1})
            print(" ", path, short(r, 300))
        except Exception as e:
            print(" ", path, "failed", str(e)[:100])



# ================================================================ fetch: full trade tapes for a sample of whole events

TAPES = os.path.join(CACHE, "inf_tapes.json.gz")
EV_PATH = os.path.join(CACHE, "events.json.gz")
HOLDOUT_T = 1794268800  # 2026-11-10 00:00 UTC: markets ending later are never used (backtest/PROTOCOL.md)
MIN_USD = 100           # trades kept in full; smaller ones only feed the price path and volume counts
FETCH_MIN = float(os.environ.get("INF_FETCH_MIN", "200"))
N_MARKETS = int(os.environ.get("INF_MARKETS", "9000"))
T0 = time.time()


def skip_market(m):
    s = (m.get("slug") or "") + " " + (m.get("q") or "").lower()
    return (m.get("sports") or "updown" in s or "up-or-down" in s or "up or down" in s or len(m.get("toks") or []) != 2
            or not m.get("closed") or len(m.get("final") or []) != 2 or max(m["final"] or [0]) < 0.99
            or not m.get("end") or m["end"] >= HOLDOUT_T or m["end"] < 1772323200)  # 2026-03-01


def universe():
    """Whole events, so cheap choices that went nowhere (and ended with little volume) are in too (bt_cache volume bias, PR #38)."""
    main = (bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}) or {}).get("markets") or {}
    ev = bt.rjson(EV_PATH, {}) or {}
    allm = dict(ev.get("markets") or {})
    allm.update(main)
    groups = collections.defaultdict(list)
    for mid, m in allm.items():
        if not skip_market(m) and 2000 <= (m.get("vol") or 0) <= 2e6:
            groups[m.get("ev") or mid].append(mid)
    print(f"universe: {len(main)} main + {len(ev.get('markets') or {})} extra markets, {len(groups)} events after filters "
          f"(events cache {'found' if ev else 'MISSING, volume bias not fixed'})")
    return allm, groups, bool(ev)


def cids_for(ids):
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        try:
            g = bot.envelope_rows(bot.http_json(f"{G}/markets", {"id": chunk, "closed": "true", "limit": 100}), "data", "markets")
        except Exception as e:
            print("  gamma ids failed", str(e)[:120])
            continue
        for x in g:
            if x.get("conditionId"):
                out[str(x.get("id"))] = x["conditionId"]
    return out


def tape(cid, max_pages=300):
    rows, cur = [], None
    for _ in range(max_pages):
        p = {"condition_id": cid, "limit": 500}
        if cur:
            p["cursor"] = cur
        r, cur, _ = trades_page(p)
        rows += r
        if not cur or not r:
            break
    return rows, bool(cur)


def compress(m, rows, W):
    """5-minute price path (outcome-0 terms) from every trade; trades >= MIN_USD kept with: wallet, outcome, side, price, size,
    next real BUY price of the same outcome 5-65 min later (our copy fill), $ traded in the market in the 24h before."""
    tt = []
    for r in rows:
        t = bot.fnum(bot.pick(r, "timestamp", "time"))
        t = t / 1000 if t > 1e11 else t
        px, sh = bot.fnum(r.get("price")), bot.fnum(r.get("size"))
        oi = r.get("outcome_index")
        if oi not in (0, 1):
            tok = str(bot.pick(r, "token_id", "asset", default=""))
            oi = 0 if tok == m["toks"][0] else 1 if tok == m["toks"][1] else None
        if not t or oi is None or not 0 < px < 1 or sh <= 0:
            continue
        tt.append((int(t), oi, str(r.get("side") or "").upper()[:1], px, sh, str(r.get("proxy_wallet") or "").lower()))
    tt.sort()
    path, last_b = [], None
    for t, oi, sd, px, sh, w in tt:
        p0 = round(px if oi == 0 else 1 - px, 4)
        b = t // 300 * 300
        if path and path[-1][0] == b:
            path[-1][1] = p0
        else:
            path.append([b, p0])
    # squeeze unchanged buckets
    sq = []
    for b, p in path:
        if not sq or sq[-1][1] != p:
            sq.append([b, p])
    keep, j, k, vol24 = [], 0, 0, 0.0
    buys = {0: [], 1: []}
    for idx, (t, oi, sd, px, sh, w) in enumerate(tt):
        if sd == "B":
            buys[oi].append((t, px))
    import bisect
    bt_t = {o: [x[0] for x in buys[o]] for o in (0, 1)}
    for idx, (t, oi, sd, px, sh, w) in enumerate(tt):
        while k < idx and tt[k][0] < t - 86400:
            vol24 -= tt[k][3] * tt[k][4]
            k += 1
        usd = px * sh
        if usd >= MIN_USD and w:
            cp = -1
            q = bisect.bisect_left(bt_t[oi], t + 300)
            if q < len(bt_t[oi]) and bt_t[oi][q] <= t + 3900:
                cp = buys[oi][q][1]
            if w not in W:
                W[w] = len(W)
            keep.append([t, W[w], oi, sd, round(px, 4), round(sh, 2), cp, round(vol24)])
        vol24 += usd
    return {"q": m["q"][:140], "end": m["end"], "final": m["final"], "fee": m.get("fee") or 0.0, "vol": m.get("vol"),
            "ev": m.get("ev"), "n": len(tt), "usd": round(sum(x[3] * x[4] for x in tt)), "path": sq, "tr": keep,
            "last_t": tt[-1][0] if tt else None}


def fetch():
    have = bt.rjson(TAPES, {}) or {}
    have.setdefault("W", [])
    have.setdefault("m", {})
    W = {w: i for i, w in enumerate(have["W"])}
    allm, groups, evok = universe()
    rng = random.Random(11)
    evs = sorted(groups)
    rng.shuffle(evs)
    want = []
    for e in evs:
        if len(want) >= N_MARKETS:
            break
        want += groups[e]
    todo = [mid for mid in want if mid not in have["m"]]
    print(f"fetch: {len(want)} markets wanted from {len(evs)} events, {len(have['m'])} cached, {len(todo)} to read")
    cmap = {}
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for part in ex.map(cids_for, [todo[i:i + 500] for i in range(0, len(todo), 500)]):
            cmap.update(part)
    print(f"  condition ids for {len(cmap)} of {len(todo)} ({time.time() - T0:.0f}s)")

    def one(mid):
        if (time.time() - T0) / 60 > FETCH_MIN:
            return mid, None
        try:
            rows, cut = tape(cmap[mid])
        except Exception as e:
            return mid, str(e)[:100]
        return mid, (rows, cut)

    done = 0
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for mid, res in ex.map(one, [m for m in todo if m in cmap]):
            if res is None or isinstance(res, str):
                continue
            rows, cut = res
            c = compress(allm[mid], rows, W)
            c["cut"] = cut
            have["m"][mid] = c
            done += 1
            if done % 500 == 0:
                print(f"  {done} tapes, {sum(len(x['tr']) for x in have['m'].values())} big trades, {time.time() - T0:.0f}s")
                have["W"] = sorted(W, key=W.get)
                bt.wjson(TAPES, have)
    have["W"] = sorted(W, key=W.get)
    have["evok"] = evok
    bt.wjson(TAPES, have)
    print(f"fetch done: {len(have['m'])} markets, {sum(len(x['tr']) for x in have['m'].values())} trades >= ${MIN_USD}, "
          f"{len(W)} wallets, {sum(1 for x in have['m'].values() if x.get('cut'))} tapes cut short, {time.time() - T0:.0f}s")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch, "run": lambda: globals()["run"](), "all": lambda: (fetch(), globals()["run"]())}[cmd]()
