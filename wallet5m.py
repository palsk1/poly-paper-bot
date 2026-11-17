#!/usr/bin/env python3
"""One wallet on Polymarket's 5-minute crypto "Up or Down" windows (17 Nov 2026, the Reddit "GoodFallen" wallet).

What it answers: is the profit real after fees, what does the wallet really do inside a window (when it buys, which
side, both sides?, waiting orders or hitting the sell side), and could a paper bot copy or rebuild it.

  fetch [addr] [pages]  wallet trades + activity (merges/redeems) + positions, Gamma results for every window,
                        the full trade list of the newest ~400 windows, Binance 1-second BTC prices.
                        Everything lands in bt_cache/w5m/ (probe w5m_fetch uploads it as an artifact).
  run                   offline report from bt_cache/w5m/ -> backtest/wallet5m.md
Data facts are in backtest/wallet5m.md.
"""
import collections
import datetime as dt
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

ADDR = "0x0ca4e9d27ff826a109ecbf74754fb66b93f277a6"
CACHE = os.path.join(bot.ROOT, "bt_cache", "w5m")


def wj(name, obj):
    os.makedirs(CACHE, exist_ok=True)
    with gzip.open(os.path.join(CACHE, name), "wt") as fh:
        json.dump(obj, fh)


def rj(name, default=None):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        return default
    with gzip.open(p, "rt") as fh:
        return json.load(fh)


def page_all(path, params, pages, label):
    out, cur = [], None
    for i in range(pages):
        p = dict(params, limit=500)
        if cur:
            p["cursor"] = cur
        try:
            res = bot.http_json(f"{bot.DATA}/{path}", p)
        except Exception as e:
            print(f"  {label} page {i} failed: {e}")
            break
        rows = bot.envelope_rows(res, "data", "positions", "trades")
        cur = ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor")) if isinstance(res, dict) else None
        out += rows
        if i % 20 == 0:
            ts = [bot.fnum(r.get("timestamp") or r.get("last_event_at")) for r in rows]
            ts = [t for t in ts if t]
            print(f"  {label} page {i}: {len(out)} rows, oldest {dt.datetime.utcfromtimestamp(min(ts)) if ts else '?'}")
        if not rows or not cur:
            break
    print(f"{label}: {len(out)} rows")
    return out


def fetch(addr=ADDR, pages=400):
    pages = int(pages)
    t0 = time.time()
    # 1) does the trade list hold every fill, or only the ones where the wallet hit the sell side?
    for extra in ({}, {"taker_only": "false"}, {"takerOnly": "false"}, {"taker_only": "true"}):
        try:
            res = bot.http_json(f"{bot.DATA}/v2/trades", dict({"user": addr, "limit": 500}, **extra))
            rows = bot.envelope_rows(res, "data")
            print("variant", extra, "rows", len(rows), "oldest", min((r["timestamp"] for r in rows), default=None))
        except Exception as e:
            print("variant", extra, "failed", e)
    trades = page_all("v2/trades", {"user": addr}, pages, "trades")
    wj("trades.json.gz", trades)
    act = page_all("v2/activity", {"user": addr}, pages, "activity")
    print("activity types:", collections.Counter(a.get("type") for a in act))
    if act:
        print("activity sample:", json.dumps(act[:2])[:1500])
    for typ in ("MERGE", "REDEEM", "SPLIT", "REWARD", "CONVERSION"):
        try:
            res = bot.http_json(f"{bot.DATA}/v2/activity", {"user": addr, "limit": 500, "type": typ})
            rows = bot.envelope_rows(res, "data")
            print(f"activity type={typ}: {len(rows)} rows", json.dumps(rows[:1])[:600])
        except Exception as e:
            print(f"activity type={typ} failed: {e}")
    wj("activity.json.gz", act)
    pos = {}
    for st in ("OPEN", "CLOSED", "REDEEMABLE"):
        for sort in ({}, {"sort_by": "TIMESTAMP"}, {"sortBy": "TIMESTAMP"}):
            rows = page_all("v2/positions", dict({"user": addr, "status": st}, **sort), 40, f"positions {st} {sort}")
            for r in rows:
                pos[r.get("token_id")] = r
    print("positions kept:", len(pos), collections.Counter(r.get("status") for r in pos.values()))
    wj("positions.json.gz", list(pos.values()))

    # 2) results of every window the wallet touched (Gamma, 20 slugs a call)
    slugs = sorted({t.get("slug") for t in trades if t.get("slug")} | {p.get("slug") for p in pos.values() if p.get("slug")})
    results_and_tapes(slugs)
    spot(trades)
    print(f"fetch took {time.time() - t0:.0f}s")


def fetch2(days=36):
    """Results + newest window tapes without re-reading the wallet: every BTC/ETH 5-minute window of the last N days."""
    now = int(time.time()) // 300 * 300 - 300
    slugs = [f"{c}-updown-5m-{t}" for c in ("btc",) for t in range(now - int(days) * 86400, now, 300)]
    results_and_tapes(slugs, wallet_only=False)


def results_and_tapes(slugs, wallet_only=True):
    print("windows touched:", len(slugs), collections.Counter(s.split("-updown-")[0] + "-" + s.split("-")[2] for s in slugs if "-updown-" in s))
    res = rj("results.json.gz", {}) or {}

    def batch(chunk):
        try:
            return bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {"slug": chunk, "closed": "true", "limit": 100}), "markets", "data")
        except Exception as e:
            print("  gamma failed", e)
            return []
    todo = [s for s in slugs if s not in res]
    with ThreadPoolExecutor(6) as ex:
        for rows in ex.map(batch, [todo[i:i + 20] for i in range(0, len(todo), 20)]):
            for m in rows:
                try:
                    names = json.loads(m.get("outcomes") or "[]")
                    prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                except Exception:
                    continue
                res[m.get("slug")] = {"cid": m.get("conditionId"), "names": names, "prices": prices, "closed": m.get("closed"),
                                      "fee": m.get("feeSchedule") or m.get("takerBaseFee") or m.get("fee"),
                                      "vol": bot.fnum(m.get("volumeNum") or m.get("volume"))}
    wj("results.json.gz", res)
    one = next(iter(res.values()), None)
    print("results:", len(res), "sample", one)

    # 3) full trade list of the newest windows the wallet traded (who traded with it, its share of the window)
    newest = sorted([s for s in res if s.startswith("btc-updown-5m-") and (res[s].get("prices") or [0])[0] in (0.0, 1.0)],
                    key=lambda s: -int(s.rsplit("-", 1)[1]))[:400]
    tapes = rj("tapes.json.gz", {}) or {}

    def tape(slug):
        cid = (res.get(slug) or {}).get("cid")
        if not cid:
            return slug, None
        rows, cur = [], None
        for _ in range(60):
            p = {"condition_id": cid, "limit": 500}
            if cur:
                p["cursor"] = cur
            try:
                r = bot.http_json(f"{bot.DATA}/v2/trades", p)
            except Exception as e:
                return slug, {"err": str(e)[:100], "rows": rows}
            page = bot.envelope_rows(r, "data")
            cur = (r.get("pagination") or {}).get("next_cursor") if isinstance(r, dict) else None
            rows += [[x.get("timestamp"), x.get("proxy_wallet"), x.get("side"), x.get("outcome"), x.get("price"), x.get("size"),
                      x.get("transaction_hash")] for x in page]
            if not page or not cur:
                return slug, {"rows": rows, "ok": True}
        return slug, {"rows": rows, "ok": False}
    with ThreadPoolExecutor(6) as ex:
        for slug, v in ex.map(tape, [s for s in newest if s not in tapes]):
            if v:
                tapes[slug] = v
    wj("tapes.json.gz", tapes)
    if not tapes:
        return
    lens = sorted(len(v["rows"]) for v in tapes.values())
    print(f"tapes: {len(tapes)}, trades per window median {lens[len(lens) // 2] if lens else 0}, max {lens[-1] if lens else 0}, "
          f"incomplete {sum(1 for v in tapes.values() if not v.get('ok'))}")



def spot(trades):
    import kfast
    days = sorted({dt.datetime.utcfromtimestamp(bot.fnum(t.get("timestamp"))).strftime("%Y-%m-%d") for t in trades})
    ok = [d for d in days if kfast.fetch_spot_day("BTCUSDT", d)]
    print("binance 1s days:", len(ok), "of", len(days), "missing", sorted(set(days) - set(ok)))
    # the newest day(s) aren't in the daily files yet: read 1-second klines from the API
    last = {}
    for d in sorted(set(days) - set(ok)):
        d0 = int(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())
        cur = d0 * 1000
        end = min(d0 + 86400, int(time.time())) * 1000
        while cur < end:
            try:
                ks = bot.http_json(f"{bot.BINANCE}/klines", {"symbol": "BTCUSDT", "interval": "1s", "startTime": cur, "limit": 1000})
            except Exception as e:
                print("  klines failed", e)
                break
            if not ks:
                break
            for k in ks:
                last[int(k[0]) // 1000] = float(k[4])
            cur = int(ks[-1][0]) + 1000
    wj("spot_api.json.gz", {str(k): v for k, v in last.items()})
    print(f"spot from API: {len(last)} seconds")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if cmd == "fetch":
        fetch(*sys.argv[2:])
    elif cmd == "fetch2":
        fetch2(*sys.argv[2:])
    elif cmd == "run":
        import wallet5m_run
        wallet5m_run.main()
