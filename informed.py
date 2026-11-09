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
        try:
            g = bot.http_json(f"{G}/markets", {"clob_token_ids": m["toks"][0]})
            g = bot.envelope_rows(g, "data", "markets")
            cid = g[0].get("conditionId") if g else None
            print("  gamma by token ->", cid, "rows", len(g))
        except Exception as e:
            print("  gamma by token failed", e)
            cid = None
        for p in ({"asset": m["toks"][0], "limit": 3}, {"token_id": m["toks"][0], "limit": 3}):
            try:
                rows, cur, res = trades_page(p)
                print("  trades by", list(p)[0], "->", len(rows), short(rows[:1], 300))
            except Exception as e:
                print("  trades by", list(p)[0], "failed", str(e)[:150])
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
    print("\n== wallet first-trade lookup (fresh-wallet check) for 3 wallets")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek}[cmd]()
