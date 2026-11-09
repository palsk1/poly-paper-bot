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
N_MARKETS = int(os.environ.get("INF_MARKETS", "20000"))
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



# ================================================================ run: score wallets, test copying them

import bisect

H = (3600, 21600, 86400)
SLIP, SLIP_STRESS = 0.01, 0.03


class Mk:
    def __init__(self, mid, x):
        self.id, self.x = mid, x
        self.pt = [p[0] for p in x["path"]]
        self.pp = [p[1] for p in x["path"]]
        self.f0 = x["final"][0]
        self.last = x.get("last_t") or 0

    def p0(self, t, before=False):
        """Last traded price (outcome-0 terms) at time t; the final payout once trading is over."""
        if t >= self.last + 600:
            return self.f0
        b = t // 300 * 300
        i = bisect.bisect_left(self.pt, b) - 1 if before else bisect.bisect_right(self.pt, b) - 1
        return self.pp[i] if i >= 0 else None


def po(p0, oi):
    return None if p0 is None else (p0 if oi == 0 else 1 - p0)


def buys(tapes):
    """First BUY of each wallet in each market outcome (one copy per idea), with moves and the copy fill."""
    out = []
    for mid, x in tapes["m"].items():
        if x.get("cut"):
            continue
        mk = Mk(mid, x)
        seen = set()
        for t, w, oi, sd, px, sh, cp, v24 in x["tr"]:
            if sd != "B" or (w, oi) in seen:
                continue
            seen.add((w, oi))
            pb = po(mk.p0(t, before=True), oi)
            pb = px if pb is None else pb
            p5 = po(mk.p0(t + 300), oi)
            fin = mk.f0 if oi == 0 else 1 - mk.f0
            r = {"mid": mid, "ev": x.get("ev") or mid, "t": t, "w": w, "oi": oi, "px": px, "usd": px * sh, "v24": v24,
                 "cp": cp, "fin": fin, "fee": x.get("fee") or 0.0, "p5": p5, "end": x["end"], "q": x["q"],
                 "last": mk.last, "vol": x.get("vol") or 0}
            for h in H:
                ph = po(mk.p0(t + h), oi)
                r[f"m{h}"] = None if ph is None else ph - pb            # move from just before the trade
                r[f"c{h}"] = None if ph is None or p5 is None else ph - p5  # move after our 5-minute delay
            out.append(r)
    out.sort(key=lambda r: r["t"])
    return out


def copy_pnl(r, slip=SLIP):
    """Profit per $1 staked copying this buy: real next BUY 5-65 min later + slip + taker fee, held to the result."""
    if r["cp"] is None or r["cp"] < 0:
        return None
    e = r["cp"] + slip
    if not 0.02 <= e <= 0.97:
        return None
    fee = r["fee"] * e * (1 - e)
    return (r["fin"] - e - fee) / e


def summarize(rows, slip=SLIP, boot=400, seed=1):
    vals = [(r["ev"], copy_pnl(r, slip)) for r in rows]
    vals = [(e, v) for e, v in vals if v is not None]
    if not vals:
        return {"n": 0}
    by = collections.defaultdict(list)
    for e, v in vals:
        by[e].append(v)
    keys = list(by)
    rng = random.Random(seed)
    sims = []
    for _ in range(boot):
        s = n = 0
        for _k in range(len(keys)):
            g = by[keys[rng.randrange(len(keys))]]
            s += sum(g)
            n += len(g)
        sims.append(100 * s / n if n else 0)
    sims.sort()
    return {"n": len(vals), "ev": len(keys), "per100": 100 * sum(v for _, v in vals) / len(vals),
            "lo": sims[int(0.05 * boot)], "hi": sims[int(0.95 * boot)], "won": sum(1 for _, v in vals if v > 0)}


def fmt(s):
    if not s.get("n"):
        return "no copyable trades"
    return (f"{s['n']} copies in {s['ev']} events, won {s['won']}: ${s['per100']:+.2f} per $100 "
            f"(90% band ${s['lo']:+.2f} to ${s['hi']:+.2f})")


def wallet_scores(rows, t_lo, t_hi, h=86400):
    """Per wallet: mean move in its direction h after our 5-min delay, averaged per market first, with a t-value."""
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if t_lo <= r["t"] and r["t"] + h < t_hi and r[f"c{h}"] is not None and 0.02 <= r["px"] <= 0.95:
            per[r["w"]][r["mid"]].append(r[f"c{h}"])
    out = {}
    for w, mk in per.items():
        vals = [statistics.mean(v) for v in mk.values()]
        n = len(vals)
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals) if n > 1 else 0.0
        out[w] = {"n": n, "mean": m, "t": m / (sd / n ** 0.5) if sd > 0 and n > 1 else 0.0}
    return out


def wallet_pnl_scores(rows, t_lo, t_hi):
    """Per wallet: what copying it (5-min delay, real fill, costs) made, only on markets finished before t_hi."""
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if t_lo <= r["t"] < t_hi and r["last"] < t_hi:
            v = copy_pnl(r)
            if v is not None:
                per[r["w"]][r["mid"]].append(v)
    out = {}
    for w, mk in per.items():
        vals = [statistics.mean(v) for v in mk.values()]
        n = len(vals)
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals) if n > 1 else 0.0
        out[w] = {"n": n, "mean": m, "t": m / (sd / n ** 0.5) if sd > 0 and n > 1 else 0.0}
    return out


def spearman(a, b):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for k, i in enumerate(o):
            r[i] = k
        return r
    if len(a) < 3:
        return None
    ra, rb = rank(a), rank(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else None


RULES = {  # wallet picks, fixed before looking at the test half
    "S1 5+ markets, avg +3c, t>=2": lambda s: s["n"] >= 5 and s["mean"] >= 0.03 and s["t"] >= 2,
    "S2 10+ markets, t>=3": lambda s: s["n"] >= 10 and s["t"] >= 3,
    "S3 3+ markets, avg +10c": lambda s: s["n"] >= 3 and s["mean"] >= 0.10,
    "S4 5+ markets, avg +5c, t>=2.5": lambda s: s["n"] >= 5 and s["mean"] >= 0.05 and s["t"] >= 2.5,
}
PNL_RULES = {  # picked on what copying them actually made (finished markets only), not on price moves
    "P1 copy profit: 5+ markets, +$5 per $100, t>=2": lambda s: s["n"] >= 5 and s["mean"] >= 0.05 and s["t"] >= 2,
    "P2 copy profit: 10+ markets, t>=2": lambda s: s["n"] >= 10 and s["mean"] > 0 and s["t"] >= 2,
}


def split_test(rows, L):
    ts_ = sorted(r["t"] for r in rows)
    mid_t = ts_[len(ts_) // 2]
    lo_t, hi_t = ts_[0], ts_[-1] + 1
    L += [f"Split at {bt.iso_t(mid_t)} (middle trade). Picks use only moves seen 24h after the trade and before the split.", ""]
    halves = {"A": (lo_t, mid_t), "B": (mid_t, hi_t)}
    sc = {k: wallet_scores(rows, *v) for k, v in halves.items()}
    scp = {k: wallet_pnl_scores(rows, *v) for k, v in halves.items()}
    both = [w for w in sc["A"] if w in sc["B"] and sc["A"][w]["n"] >= 5 and sc["B"][w]["n"] >= 5]
    rho = spearman([sc["A"][w]["mean"] for w in both], [sc["B"][w]["mean"] for w in both])
    L += [f"**Does 'early' repeat?** {len(both)} wallets have 5+ markets in both halves. Rank correlation of their "
          f"24h-after-delay move between halves: {rho if rho is None else round(rho, 3)} (0 = no memory, 1 = perfect).", ""]
    # top decile in A -> B moves
    if both:
        srt = sorted(both, key=lambda w: -sc["A"][w]["mean"])
        dec = max(1, len(srt) // 10)
        top, bot_ = srt[:dec], srt[-dec:]
        L += [f"- Top tenth in half A ({dec} wallets): half A avg {100 * statistics.mean(sc['A'][w]['mean'] for w in top):+.2f}c, "
              f"half B avg {100 * statistics.mean(sc['B'][w]['mean'] for w in top):+.2f}c",
              f"- Bottom tenth in half A: half A {100 * statistics.mean(sc['A'][w]['mean'] for w in bot_):+.2f}c, "
              f"half B {100 * statistics.mean(sc['B'][w]['mean'] for w in bot_):+.2f}c",
              f"- Everyone in both halves: half B {100 * statistics.mean(sc['B'][w]['mean'] for w in both):+.2f}c", ""]
    L += ["| Pick rule | direction | wallets | copies in the other half | same-size random wallets (median, 20 draws) |", "|---|---|---|---|---|"]
    res = {}
    allr = [(n, f, sc) for n, f in RULES.items()] + [(n, f, scp) for n, f in PNL_RULES.items()]
    for name, fn, scx in allr:
        for a, b in (("A", "B"), ("B", "A")):
            pick = {w for w, s in scx[a].items() if fn(s)}
            test = [r for r in rows if halves[b][0] <= r["t"] < halves[b][1]]
            mine = [r for r in test if r["w"] in pick]
            s = summarize(mine)
            # random twins: wallets with a similar number of markets in the pick half
            pool = collections.defaultdict(list)
            for w, x in scx[a].items():
                pool[min(x["n"], 30) // 3].append(w)
            rng = random.Random(5)
            tw = []
            for _ in range(20):
                twins = set()
                for w in pick:
                    cand = pool[min(scx[a][w]["n"], 30) // 3]
                    twins.add(rng.choice(cand))
                ss = summarize([r for r in test if r["w"] in twins], boot=50)
                if ss.get("n"):
                    tw.append(ss["per100"])
            res[(name, a)] = (pick, s)
            niche = summarize([r for r in mine if r["vol"] < 250e3], boot=100)
            L.append(f"| {name} | pick {a}, test {b} | {len(pick)} | {fmt(s)}; niche markets (<$250k): {fmt(niche)} | "
                     f"{'-' if not tw else f'${statistics.median(tw):+.2f} per $100'} |")
    L.append("")
    # wallets that pass in BOTH halves (a live watch list would look like this)
    keep = {}
    for name, fn, scx in allr:
        both_ = [w for w in scx["A"] if fn(scx["A"][w]) and w in scx["B"] and fn(scx["B"][w])]
        keep[name] = both_
        L.append(f"- Pass {name} in both halves: {len(both_)} wallets")
    L.append("")
    split_test.both = keep
    return res, halves, sc


def fresh_check(rows, cap=1500):
    """Real wallet history from the API: how many trades did the wallet make before this one? (<= 5 = fresh)."""
    W = {}

    def hist(w):
        out, cur = [], None
        for _ in range(6):
            p = {"user": w, "limit": 500}
            if cur:
                p["cursor"] = cur
            try:
                r, cur, _ = trades_page(p)
            except Exception:
                return w, None
            out += [bot.fnum(bot.pick(x, "timestamp", "time")) for x in r]
            if not cur or not r:
                break
        return w, (out, bool(cur))
    ws = sorted({r["waddr"] for r in rows})[:cap]
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for w, res in ex.map(hist, ws):
            W[w] = res
    for r in rows:
        h = W.get(r["waddr"])
        if not h:
            r["prior"] = None
            continue
        tt, more = h
        prior = sum(1 for x in tt if x and (x / 1000 if x > 1e11 else x) < r["t"])
        r["prior"] = None if more and prior == 0 else prior  # unknown when we couldn't reach back that far
        r["prior"] = 999 if more and prior > 0 else r["prior"]
    return rows


def band3(p):
    return "3-30c" if p < 0.30 else "30-60c" if p < 0.60 else "60-90c"


def run():
    tapes = bt.rjson(TAPES, {}) or {}
    if not tapes.get("m"):
        print("no tapes; run btinf_fetch first")
        return
    Wl = tapes["W"]
    rows = buys(tapes)
    for r in rows:
        r["waddr"] = Wl[r["w"]]
    nm = len(tapes["m"])
    L = ["# Who trades before the price moves? (informed-trader hunt)", "",
         f"Data: full trade lists of {nm} finished Polymarket markets from {len({x.get('ev') for x in tapes['m'].values()})} whole events "
         f"(sports and 5/15-minute crypto left out, every choice of an event kept so cheap losers aren't missing: "
         f"{'yes' if tapes.get('evok') else 'NO, events cache missing'}), markets ending 2026-03-01 to 2026-11-09 (holdout untouched). "
         f"{len(rows)} first buys of $100+ by {len({r['w'] for r in rows})} wallets. Prices are real trades (5-minute steps). "
         f"A copy pays the next real buy price 5-65 minutes later (our bot is ~5 min behind) + 1c + taker fee, held to the result. "
         f"No later buy within an hour = no copy (no made-up fills).", ""]
    # baseline
    L += ["## 1. Baseline: copying everyone", "",
          f"- All $100+ first buys: {fmt(summarize(rows))}",
          f"- Same at +3c: {fmt(summarize(rows, SLIP_STRESS))}"]
    for lo, hi in ((100, 1000), (1000, 10000), (10000, 1e12)):
        L.append(f"- Buys ${lo:,.0f}-{hi:,.0f}: {fmt(summarize([r for r in rows if lo <= r['usd'] < hi]))}")
    L.append("")
    L += ["Average move in the buyer's direction (cents), from just before the trade / after our 5-min delay:", ""]
    for h in H:
        a = [r[f"m{h}"] for r in rows if r[f"m{h}"] is not None]
        b = [r[f"c{h}"] for r in rows if r[f"c{h}"] is not None]
        L.append(f"- {h // 3600}h: {100 * statistics.mean(a):+.2f}c / {100 * statistics.mean(b):+.2f}c")
    L.append("")
    # 2. wallets
    L += ["## 2. Wallets that are early again and again (split-half test)", ""]
    res, halves, sc = split_test(rows, L)
    # list best A wallets that also did well in B
    best = sorted([w for w, s in sc["A"].items() if RULES["S1 5+ markets, avg +3c, t>=2"](s)], key=lambda w: -sc["A"][w]["t"])[:15]
    if best:
        L += ["Top wallets picked on half A (S1), and what they did in half B:", "", "| wallet | A markets | A avg | A t | B markets | B avg | B copies |", "|---|---|---|---|---|---|---|"]
        for w in best:
            b = sc["B"].get(w, {"n": 0, "mean": 0})
            s = summarize([r for r in rows if r["w"] == w and r["t"] >= halves["B"][0]], boot=100)
            L.append(f"| `{Wl[w]}` | {sc['A'][w]['n']} | {100 * sc['A'][w]['mean']:+.1f}c | {sc['A'][w]['t']:.1f} | {b['n']} | "
                     f"{100 * b['mean']:+.1f}c | {fmt(s) if s.get('n') else '-'} |")
        L.append("")
    # 3. pattern: fresh wallet, big bet, quiet market
    L += ["## 3. Pattern: new wallet, one big bet, quiet market", "",
          "Known at the time of the trade, no wallet history needed from us. 'Quiet' = the bet is bigger than everything "
          "traded in that market in the 24 hours before. 'New in our data' = first market we see this wallet in.", ""]
    first_seen = {}
    for r in rows:
        first_seen.setdefault(r["w"], r["t"])
    nmk = collections.Counter()
    seen_mk = collections.defaultdict(set)
    for r in rows:
        r["nprior"] = len(seen_mk[r["w"]])
        seen_mk[r["w"]].add(r["mid"])
    base = [r for r in rows if 0.03 <= r["px"] <= 0.90]
    variants = {
        "big ($1k+)": lambda r: r["usd"] >= 1000,
        "big + quiet": lambda r: r["usd"] >= 1000 and r["usd"] >= r["v24"],
        "big + new in our data": lambda r: r["usd"] >= 1000 and r["nprior"] == 0,
        "big + quiet + new": lambda r: r["usd"] >= 1000 and r["usd"] >= r["v24"] and r["nprior"] == 0,
        "$5k+ + quiet + new": lambda r: r["usd"] >= 5000 and r["usd"] >= r["v24"] and r["nprior"] == 0,
        "big + quiet + new, cheap side (3-30c)": lambda r: r["usd"] >= 1000 and r["usd"] >= r["v24"] and r["nprior"] == 0 and r["px"] < 0.30,
    }
    L += ["| Pattern | half A | half B | all |", "|---|---|---|---|"]
    for name, fn in variants.items():
        hit = [r for r in base if fn(r)]
        L.append(f"| {name} | {fmt(summarize([r for r in hit if r['t'] < halves['B'][0]]))} | "
                 f"{fmt(summarize([r for r in hit if r['t'] >= halves['B'][0]]))} | {fmt(summarize(hit))} |")
    L.append("")
    # same price band twins for the main pattern
    hit = [r for r in base if variants["big + quiet + new"](r)]
    L += ["Same price band, big buys that are NOT the pattern (are we just seeing the price band?):", ""]
    for b3 in ("3-30c", "30-60c", "60-90c"):
        h_ = [r for r in hit if band3(r["px"]) == b3]
        o_ = [r for r in base if r["usd"] >= 1000 and band3(r["px"]) == b3 and not variants["big + quiet + new"](r)]
        L.append(f"- {b3}: pattern {fmt(summarize(h_))}; others {fmt(summarize(o_))}")
    L.append("")
    # real freshness from the API for pattern hits
    L += ["Real wallet age from the Polymarket API (trades the wallet made before this bet):", ""]
    chk = fresh_check([dict(r) for r in base if r["usd"] >= 1000 and r["usd"] >= r["v24"]])
    for name, fn in (("brand new (0 earlier trades)", lambda r: r["prior"] == 0), ("1-5 earlier", lambda r: r["prior"] is not None and 1 <= r["prior"] <= 5),
                     ("6-3000 earlier", lambda r: r["prior"] is not None and 6 <= r["prior"] < 999), ("3000+ earlier", lambda r: r["prior"] == 999),
                     ("unknown", lambda r: r["prior"] is None)):
        g = [r for r in chk if fn(r)]
        L.append(f"- big + quiet, {name}: {fmt(summarize(g))}; half A {fmt(summarize([r for r in g if r['t'] < halves['B'][0]]))}; "
                 f"half B {fmt(summarize([r for r in g if r['t'] >= halves['B'][0]]))}")
    L.append("")
    fresh = [r for r in chk if r["prior"] is not None and r["prior"] <= 5]
    if fresh:
        tp = collections.defaultdict(list)
        for r in fresh:
            tp[__import__("calib").topic(r["q"])].append(r)
        L += ["Fresh + big + quiet by topic: " + "; ".join(f"{k}: {fmt(summarize(v, boot=100))}" for k, v in sorted(tp.items(), key=lambda kv: -len(kv[1]))), ""]
        L += ["Examples (fresh wallet, big bet, quiet market):", ""]
        for r in sorted(fresh, key=lambda r: -r["usd"])[:20]:
            c = copy_pnl(r)
            L.append(f"- {bt.iso_t(r['t'])[:16]} ${r['usd']:,.0f} at {100 * r['px']:.0f}c (24h before: ${r['v24']:,.0f} traded) -> "
                     f"{'won' if r['fin'] > 0.5 else 'lost'}, copy {'-' if c is None else f'{100 * c:+.0f} per $100'} | {r['q'][:80]}")
        L.append("")
    txt = "\n".join(L) + "\n"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "informed_wallets.json"), "w") as fh:
        json.dump({k: [Wl[w] for w in v] for k, v in getattr(split_test, "both", {}).items()}, fh, indent=1)
    with open(os.path.join(OUT, "informed.md"), "w") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch, "run": lambda: globals()["run"](), "all": lambda: (fetch(), globals()["run"]())}[cmd]()
